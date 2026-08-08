#!/usr/bin/env python3
"""Reconcile: diff what the wiki claims against what is actually installed and used.

This is the core loop. Catalogs on the internet know what exists; only this
knows what YOU have, whether it still works, and whether anything invokes it.

Emits inventory/inventory.json (machine) and inventory/inventory.md (Obsidian).

Usage:
    python3 bin/reconcile.py [--since-days 90]
"""
import argparse, json, os, re, subprocess, sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

HOME = Path.home()
CL = HOME / ".claude"
OUT = Path(__file__).resolve().parent.parent / "inventory"

# ponytail: regex scan over 1GB of transcripts beats json.loads per line by ~20x.
# Upgrade to a real parser only if a field we need stops being greppable.
RE_SKILL = re.compile(r'"skill"\s*:\s*"([a-zA-Z0-9_:.-]+)"')
RE_MCP = re.compile(r'"name"\s*:\s*"(mcp__[a-zA-Z0-9_]+)"')
RE_AGENT = re.compile(r'"subagent_type"\s*:\s*"([a-zA-Z0-9_-]+)"')
RE_DAY = re.compile(r'"timestamp"\s*:\s*"(\d{4}-\d{2}-\d{2})')


def scan_usage():
    """Count invocations and last-used day per skill / mcp server / subagent."""
    counts = {"skill": Counter(), "mcp": Counter(), "agent": Counter()}
    last = defaultdict(str)
    sessions = 0
    for f in (CL / "projects").rglob("*.jsonl"):
        sessions += 1
        day = ""
        try:
            with open(f, errors="replace") as fh:
                for line in fh:
                    m = RE_DAY.search(line)
                    if m:
                        day = m.group(1)
                    for n in RE_SKILL.findall(line):
                        counts["skill"][n] += 1
                        last[f"skill:{n}"] = max(last[f"skill:{n}"], day)
                    for n in RE_MCP.findall(line):
                        srv = "__".join(n.split("__")[:2])
                        counts["mcp"][srv] += 1
                        last[f"mcp:{srv}"] = max(last[f"mcp:{srv}"], day)
                    for n in RE_AGENT.findall(line):
                        counts["agent"][n] += 1
                        last[f"agent:{n}"] = max(last[f"agent:{n}"], day)
        except OSError:
            continue
    return counts, last, sessions


def installed_skills():
    """Skill name -> (activation mode guess, description bytes, install date)."""
    out = {}
    sk = CL / "skills"
    if not sk.exists():
        return out
    for name in sorted(os.listdir(sk)):
        p = sk / name / "SKILL.md"
        if not p.exists():
            continue
        try:
            head = p.read_text(errors="replace")[:4000]
        except OSError:
            head = ""
        desc = ""
        m = re.search(r"^description:\s*(.+)$", head, re.M)
        if m:
            desc = m.group(1).strip()
        # A skill the model is forbidden to call can never show invocations.
        # Reporting it as unused blames the tool for a rule.
        user_only = bool(re.search(r"^disable-model-invocation:\s*true", head,
                                   re.M | re.I))
        st = (sk / name).stat()
        out[name] = {
            "desc_bytes": len(desc),
            "user_only": user_only,
            "installed": date.fromtimestamp(st.st_birthtime
                                            if hasattr(st, "st_birthtime")
                                            else st.st_mtime).isoformat(),
            "path": str(sk / name),
        }
    return out


def settings():
    try:
        return json.loads((CL / "settings.json").read_text())
    except (OSError, ValueError):
        return {}


def mcp_config():
    """Declared MCP servers: user scope + every project .mcp.json we know of."""
    servers = {}
    try:
        top = json.loads((HOME / ".claude.json").read_text())
    except (OSError, ValueError):
        top = {}
    for n in top.get("mcpServers", {}):
        servers[n] = {"scope": "user", "approved": True}
    for proj, cfg in top.get("projects", {}).items():
        for n in cfg.get("mcpServers", {}):
            servers.setdefault(n, {"scope": f"project:{Path(proj).name}",
                                   "approved": True})
        enabled = set(cfg.get("enabledMcpjsonServers", []))
        mcpf = Path(proj) / ".mcp.json"
        if mcpf.exists():
            try:
                for n in json.loads(mcpf.read_text()).get("mcpServers", {}):
                    servers.setdefault(n, {"scope": f"project:{Path(proj).name}",
                                           "approved": n in enabled})
            except ValueError:
                pass
    return servers


def hooks(cfg):
    out = []
    for ev, arr in cfg.get("hooks", {}).items():
        for m in arr:
            for h in m.get("hooks", []):
                c = h.get("command", "")
                binary = c.strip('"').split()[0].strip('"') if c else ""
                out.append({"event": ev, "command": c,
                            "reachable": bool(binary) and os.path.exists(binary)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since-days", type=int, default=90,
                    help="usage older than this counts as stale")
    args = ap.parse_args()
    cutoff = (date.today() - timedelta(days=args.since_days)).isoformat()
    grace = (date.today() - timedelta(days=14)).isoformat()

    counts, last, sessions = scan_usage()
    skills = installed_skills()
    cfg = settings()
    servers = mcp_config()

    findings = []
    rows = []

    def row(kind, name, activation, observable, value, last_seen, status):
        """One installed thing.

        `observable` is the field that matters. It says HOW this tool's use can
        be seen - or that it cannot be. A count of 0 under observable='none'
        means "not measurable", not "unused". Conflating those two produced
        three separate wrong findings before this field existed: hooks (rtk),
        plugin-activated skills (caveman), and disable-model-invocation
        skills (zoom-out) were all reported as dead while running fine.
        """
        rows.append({"kind": kind, "name": name, "activation": activation,
                     "observable": observable, "value": value,
                     "last_used": last_seen or "-", "status": status})

    for name, meta in skills.items():
        used = counts["skill"][name]
        seen = last.get(f"skill:{name}", "")
        # Blind spot: hook-activated tools never appear as Skill calls, so
        # counting invocations alone deletes the best-integrated tools first.
        # A skill is hook-activated if a settings.json hook names it, OR it
        # ships with an enabled plugin of the same name (caveman, ponytail).
        plugin_names = {p.split("@")[0] for p in cfg.get("enabledPlugins", {})}
        hooked = (any(name in h["command"] for h in hooks(cfg))
                  or name in plugin_names)
        fresh = meta["installed"] >= grace
        if hooked:
            row("skill", name, "hook", "none", None, seen,
                "active (hook-activated; invocations cannot show this)")
        elif meta.get("user_only"):
            # The model is forbidden from calling it, so a transcript count of
            # zero is a rule, not a verdict. Nothing here can measure whether
            # the human uses it - say so instead of implying disuse.
            row("skill", name, "user-only", "none", None, seen,
                "user-invoked only — NOT MEASURABLE from transcripts")
            findings.append(f"skill `{name}` is user-invoked only; this tool "
                            f"cannot tell used from unused. Judge by hand.")
        elif fresh:
            row("skill", name, "model", "invocations", used, seen,
                "new (grace period)")
        elif used == 0:
            row("skill", name, "model", "invocations", 0, seen, "NEVER INVOKED")
            findings.append(f"skill `{name}` never invoked "
                            f"(installed {meta['installed']})")
        elif seen and seen < cutoff:
            row("skill", name, "model", "invocations", used, seen,
                f"stale (last {seen})")
            findings.append(f"skill `{name}` unused since {seen}")
        else:
            row("skill", name, "model", "invocations", used, seen, "active")

    for name, meta in servers.items():
        used = counts["mcp"][f"mcp__{name}"]
        seen = last.get(f"mcp:mcp__{name}", "")
        if not meta["approved"]:
            row("mcp", name, "on-call", "calls", used, seen,
                "NOT APPROVED — tools unavailable")
            findings.append(f"MCP `{name}` declared but not approved "
                            f"({meta['scope']}) — its tools are dead")
        elif used == 0:
            row("mcp", name, "on-call", "calls", 0, seen, "NEVER CALLED")
            findings.append(f"MCP `{name}` never called ({meta['scope']})")
        else:
            row("mcp", name, "on-call", "calls", used, seen, "active")

    agents_dir = CL / "agents"
    for f in (sorted(os.listdir(agents_dir)) if agents_dir.exists() else []):
        name = f[:-3] if f.endswith(".md") else f
        used = counts["agent"][name]
        row("agent", name, "spawned", "spawns", used,
            last.get(f"agent:{name}", ""),
            "active" if used else "NEVER SPAWNED")
        if not used:
            findings.append(f"agent `{name}` never spawned")

    # Hooks are installed tools too. Omitting them left rtk - which fires on
    # every Bash call - absent from the inventory, so the sweep re-proposed it
    # as a fresh discovery. Anything that runs is a row.
    hk = hooks(cfg)
    for h in hk:
        binary = h["command"].strip('"').split()[0].strip('"')
        name = os.path.basename(binary).split(".")[0] or binary
        # last_used is a DATE column. The hook event belongs in status - putting
        # it in last_used made 'SessionStart' sort as a future date.
        status = (f"active ({h['event']} hook)" if h["reachable"]
                  else f"MISSING BINARY ({h['event']})")
        if not h["reachable"]:
            findings.append(f"hook on {h['event']} points at a missing binary: "
                            f"{h['command'][:60]}")
        row("hook", name, "hook", "reachability", h["reachable"], "", status)

    # Orphan check: the failure mode that bit us 4x. Artifacts from a plugin
    # that is no longer enabled still load into every session.
    enabled = set(cfg.get("enabledPlugins", {}))
    for d in ("commands", "agents"):
        p = CL / d
        if p.exists() and any(p.iterdir()):
            n = sum(1 for _ in p.rglob("*.md"))
            if n:
                row("artifact", f"~/.claude/{d}", "always-on", "file-count", n,
                    "", f"{n} md files loading every session")

    OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "sessions_scanned": sessions,
        "enabled_plugins": sorted(enabled),
        "rows": rows,
        "findings": findings,
    }
    (OUT / "inventory.json").write_text(json.dumps(payload, indent=2))

    md = [f"# Inventory", "",
          f"Generated {payload['generated']} from {sessions} sessions.", "",
          f"**{len(findings)} findings.**", ""]
    if findings:
        md += ["## Findings", ""] + [f"- {f}" for f in findings] + [""]
    md += ["## What is installed", "",
           "`observable: none` means this tool's use cannot be seen from here. "
           "A blank measure is not evidence of disuse.", "",
           "| Kind | Name | Activation | Measure | Last used | Status |",
           "|---|---|---|---:|---|---|"]
    for r in sorted(rows, key=lambda x: (x["kind"], str(x["value"]))):
        link = (f"[[{r['name']}]]" if r["kind"] in ("skill", "mcp")
                else f"`{r['name']}`")
        measure = "not measurable" if r["observable"] == "none" else f"{r['value']}"
        md.append(f"| {r['kind']} | {link} | {r['activation']} | {measure} | "
                  f"{r['last_used']} | {r['status']} |")
    md += ["", "---", "", "See [[ledger]] for adopt/remove decisions."]
    (OUT / "inventory.md").write_text("\n".join(md) + "\n")

    print(f"sessions scanned : {sessions}")
    print(f"rows             : {len(rows)}")
    print(f"findings         : {len(findings)}")
    for f in findings[:15]:
        print(f"  - {f}")
    if len(findings) > 15:
        print(f"  ... and {len(findings) - 15} more (see inventory/inventory.md)")


if __name__ == "__main__":
    sys.exit(main())
