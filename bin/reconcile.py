#!/usr/bin/env python3
"""Reconcile: diff what the wiki claims against what is actually installed and used.

This is the core loop. Catalogs on the internet know what exists; only this
knows what YOU have, whether it still works, and whether anything invokes it.

Emits inventory/inventory.json (machine) and inventory/inventory.md (Obsidian).

Usage:
    python3 bin/reconcile.py [--since-days 90]
"""
import argparse, json, os, re, shutil, subprocess, sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

HOME = Path.home()
CL = HOME / ".claude"
OUT = Path(__file__).resolve().parent.parent / "inventory"

# ponytail: regex scan over 1GB of transcripts beats json.loads per line by ~20x.
# Upgrade to a real parser only if a field we need stops being greppable.
RE_SKILL = re.compile(r'"skill"\s*:\s*"([a-zA-Z0-9_:.-]+)"')
# The class MUST carry "-". Without it every hyphenated server name matched
# nothing, so ag-mcp reported NEVER CALLED on 11 real calls and context-mode was
# invisible on 3,539. A zero the scanner never computed reads exactly like a
# measured one - the same failure as BLOCKED shipping as PASS.
RE_MCP = re.compile(r'"name"\s*:\s*"(mcp__[a-zA-Z0-9_.-]+)"')
RE_AGENT = re.compile(r'"subagent_type"\s*:\s*"([a-zA-Z0-9_-]+)"')
RE_DAY = re.compile(r'"timestamp"\s*:\s*"(\d{4}-\d{2}-\d{2})')
# Hook firings appear as the script name inside hook_success / hook records.
# Matched on lines already known to mention a hook, so a stray .py in prose
# cannot be counted as one.
RE_HOOK = re.compile(r'([A-Za-z0-9_.-]+\.(?:mjs|js|cjs|py|sh|ts))')
RE_SCRIPT = re.compile(r'[^\s"\']+\.(?:mjs|js|cjs|py|sh|ts)\b')


def scan_usage():
    """Count invocations and last-used day per skill / mcp server / subagent."""
    counts = {"skill": Counter(), "mcp": Counter(), "agent": Counter(),
              "hook": Counter()}
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
                    # Hooks were carried as observable:"reachability" - does the
                    # file exist - while every firing was sitting right here. One
                    # plugin's stop hook fired 136 times in a single session and
                    # the inventory could not see one of them.
                    if '"hook' in line:
                        for n in RE_HOOK.findall(line):
                            counts["hook"][n] += 1
                            last[f"hook:{n}"] = max(last[f"hook:{n}"], day)
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


def repos():
    """Repos to inventory, from repos.txt (gitignored - the paths are private)."""
    f = OUT.parent / "repos.txt"
    if not f.exists():
        return []
    out = []
    for line in f.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        path, _, stack = line.partition("|")
        p = Path(path.strip())
        if (p / ".git").is_dir():
            out.append((p, stack.strip() or "global"))
    return out


def project_tooling(repo: Path):
    """Tooling installed INSIDE a repo, which the global harness never shows.

    A machine-wide inventory reports a clean harness while each repo quietly
    accumulates its own skills, agents and MCP servers. For a single stack that
    is harmless; across frontend + data-science + trading it hides most of the
    surface.
    """
    found = []
    cl = repo / ".claude"
    for sub, kind in (("skills", "skill"), ("agents", "agent"),
                      ("commands", "command")):
        d = cl / sub
        if d.is_dir():
            for item in sorted(os.listdir(d)):
                if item.startswith("."):
                    continue
                found.append((kind, item.removesuffix(".md")))
    mcpf = repo / ".mcp.json"
    if mcpf.exists():
        try:
            for n in json.loads(mcpf.read_text()).get("mcpServers", {}):
                found.append(("mcp", n))
        except ValueError:
            pass
    for sf in ("settings.json", "settings.local.json"):
        p = cl / sf
        if p.exists():
            try:
                for n in json.loads(p.read_text()).get("enabledPlugins", {}):
                    found.append(("plugin", n.split("@")[0]))
            except ValueError:
                pass
    return found


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


def hook_target(command: str, root: str = "") -> str:
    """The script a hook actually runs, not the interpreter that launches it.

    Three shapes, all real, all previously mishandled:
      python3 /path/session_log.py            -> read the interpreter, called it missing
      node "${CLAUDE_PLUGIN_ROOT}/x/y.mjs"    -> unexpanded variable, called it missing
      command -v node && node "…/z.js" || …   -> picked ">/dev/null", named the hook "null"
    A script path is the only thing worth finding, so look for one directly.
    """
    cmd = command.replace("${CLAUDE_PLUGIN_ROOT}", root) if root else command
    m = RE_SCRIPT.search(cmd)
    if m:
        return m.group(0).strip('"\'')
    parts = [p.strip('"') for p in cmd.split() if p.strip('"')]
    return parts[0] if parts else ""


def reachable(command: str, root: str = ""):
    """True / False / None, where None means 'cannot be determined from here'.

    Some hooks build their path from shell variables at run time - claude-mem
    resolves its through `$_E`, three levels of indirection deep. Calling that
    MISSING BINARY was a verdict on a hook that had fired 7,324 times. An
    unresolvable path is an unknown, and unknowns say so.
    """
    t = hook_target(command, root)
    if not t:
        return False
    if "$" in t or "{" in t:
        return None
    # A bare name is on PATH or it is not; a path either exists or it does not.
    return os.path.exists(t) if "/" in t else bool(shutil.which(t))


def plugin_hooks():
    """Hooks declared by PLUGINS, which settings.json never mentions.

    The gap that made this worth fixing: reading settings.json alone reported 3
    hooks while 5 plugin hooks fired ~150 times in a single session. Hooks are
    the highest-leverage surface in the harness - they run unconditionally, in
    every session - and they were the least visible.
    """
    out = []
    root = CL / "plugins" / "marketplaces"
    if not root.exists():
        return out
    # Three shapes in the wild, and missing one hides a hook that runs in every
    # session: claude-mem declares under plugin/hooks/, caveman inside its
    # plugin.json, the rest at hooks/hooks.json. The .codex- and .cursor-
    # variants describe other harnesses and are deliberately skipped.
    files = (list(root.glob("*/hooks/hooks.json"))
             + list(root.glob("*/plugin/hooks/hooks.json"))
             + list(root.glob("*/.claude-plugin/plugin.json")))
    for f in sorted(files):
        try:
            cfg = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        if "hooks" not in cfg:
            continue
        plugin = f.relative_to(root).parts[0]
        out += [dict(h, plugin=plugin) for h in hooks(cfg, str(f.parent.parent))]
    return out


def hooks(cfg, root: str = ""):
    """One row per (event, script). A plugin declaring nine matchers for the
    same script is one hook, not nine."""
    out, seen = [], set()
    for ev, arr in cfg.get("hooks", {}).items():
        if not isinstance(arr, list):
            continue
        for m in arr:
            for h in m.get("hooks", []):
                c = h.get("command", "")
                key = (ev, hook_target(c, root))
                if not c or key in seen:
                    continue
                seen.add(key)
                out.append({"event": ev, "command": c, "plugin": "",
                            "root": root, "reachable": reachable(c, root)})
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

    def row(kind, name, activation, observable, value, last_seen, status,
            scope="global"):
        """One installed thing.

        `observable` is the field that matters. It says HOW this tool's use can
        be seen - or that it cannot be. A count of 0 under observable='none'
        means "not measurable", not "unused". Conflating those two produced
        three separate wrong findings before this field existed: hooks (rtk),
        plugin-activated skills (caveman), and disable-model-invocation
        skills (zoom-out) were all reported as dead while running fine.
        """
        rows.append({"kind": kind, "name": name, "scope": scope,
                     "activation": activation, "observable": observable,
                     "value": value, "last_used": last_seen or "-",
                     "status": status})

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
    # One row per SCRIPT, not per event. Firings are counted by filename, so a
    # script wired to five events was printing the same 7,324 on five rows as
    # though each event had fired that many times.
    by_script = {}
    for h in hooks(cfg) + plugin_hooks():
        base = os.path.basename(hook_target(h["command"], h.get("root", "")))
        cur = by_script.setdefault(base, dict(h, events=[]))
        if h["event"] not in cur["events"]:
            cur["events"].append(h["event"])
    for h in by_script.values():
        target = hook_target(h["command"], h.get("root", ""))
        base = os.path.basename(target)
        name = base.split(".")[0] or target
        scope = f"plugin:{h['plugin']}" if h["plugin"] else "global"
        h["event"] = ", ".join(h["events"])
        # Firings are only countable when the hook runs a SCRIPT - the transcript
        # records the filename. A hook that shells out to a binary leaves no name
        # to match, and reporting 0 for it would be the MCP false-zero all over
        # again: rtk fires on every Bash call and would have read "0 firings".
        countable = bool(RE_SCRIPT.search(base))
        fired = counts["hook"].get(base, 0) if countable else None
        seen = last.get(f"hook:{base}", "") if countable else ""
        # last_used is a DATE column. The hook event belongs in status - putting
        # it in last_used made 'SessionStart' sort as a future date.
        if h["reachable"] is False:
            status = f"MISSING BINARY ({h['event']})"
            findings.append(f"hook on {h['event']} points at a missing binary: "
                            f"{h['command'][:60]}")
        elif h["reachable"] is None and not fired:
            # Unresolvable path AND never seen firing: nothing is known here.
            status = f"declared ({h['event']} hook; path not resolvable)"
        elif not countable:
            status = f"active ({h['event']} hook; firings not countable)"
        elif fired:
            status = f"active ({h['event']} hook, {fired} firings)"
        else:
            # Reachable but never seen firing. Not the same as unused: a hook on
            # a rare event is doing its job by staying quiet.
            status = f"installed ({h['event']} hook, no firing observed)"
        row("hook", name, scope, "firings" if countable else "none",
            fired, seen, status)

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

    # ── per-repo tooling ────────────────────────────────────────────────
    stacks = OUT.parent / "wiki" / "stacks"
    STACK_MARK = "<!-- generated above; your notes below survive -->"
    for repo, stack_type in repos():
        items = project_tooling(repo)
        for kind, name in items:
            # Usage counters are machine-wide; a project skill named the same
            # as a global one cannot be told apart. Say so rather than guess.
            row(kind, name, "project", "none", None, "",
                f"installed in {repo.name} — usage not attributable per repo",
                scope=repo.name)
        if items:
            findings.append(f"{repo.name}: {len(items)} project-level tools "
                            f"the global harness does not show")
        stacks.mkdir(parents=True, exist_ok=True)
        page = stacks / f"{repo.name}.md"
        old = page.read_text() if page.exists() else ""
        tail = old.split(STACK_MARK, 1)[1] if STACK_MARK in old else (
            "\n## What it actually is\n\n_Describe the stack._\n\n"
            "## Fit filter\n\n_The standing noes. Anything matching these is "
            "rejected without a scan._\n")
        # Ledger decisions that apply here: global ones plus this stack type.
        applicable = []
        for ln in (OUT.parent / "ledger.md").read_text().splitlines():
            if not ln.startswith("|") or ln.count("|") < 6:
                continue
            c = [x.strip() for x in ln.strip("|").split("|")]
            if len(c) < 6 or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", c[0]):
                continue
            if c[2] == stack_type or (c[2] == "global" and stack_type != "global"):
                applicable.append((c[1], c[2], c[3]))
        scoped = [a for a in applicable if a[1] != "global"]
        body = [f"---", f"verified_at: {date.today().isoformat()}",
                f"repo: {repo}", f"stack_type: {stack_type}", f"---", "",
                f"# Stack: {repo.name}", "",
                f"Stack type: **{stack_type}** — ledger decisions scoped to "
                f"this type apply here.", "",
                f"**{len(items)} project-level tool(s)** installed in this repo:",
                ""]
        if items:
            body += ["| Kind | Name |", "|---|---|"]
            for k, n in items:
                # Link only when a page exists. A wikilink to nothing is a
                # phantom node in the graph - 45 of them is how this vault
                # started.
                wiki = OUT.parent / "wiki"
                has_page = ((wiki / "tools" / f"{n}.md").exists()
                            or (wiki / "local" / f"{n}.md").exists())
                body.append(f"| {k} | {'[[' + n + ']]' if has_page else '`' + n + '`'} |")
        else:
            body += ["_none — this repo uses only the global harness._"]
        if scoped:
            body += ["", "## Decisions scoped to this stack", "",
                     "| Tool | Scope | Decision |", "|---|---|---|"]
            body += [f"| {t} | {sc} | {d} |" for t, sc, d in scoped]
        else:
            body += ["", "## Decisions scoped to this stack", "",
                     "_None yet — every decision so far was global. When a tool "
                     "is right here and wrong elsewhere, that is a scoped row._"]
        body += ["", f"{len(applicable) - len(scoped)} global decision(s) also "
                 f"apply; see [[ledger]].", "", "Back to [[MAP]].", "", STACK_MARK]
        page.write_text("\n".join(body) + tail)

    # Local pages for everything installed that has no public page. Public
    # pages come from the ledger (decisions); these come from disk (facts).
    # Two folders, never the same name twice, so every [[link]] resolves and
    # the graph is complete without publishing a private tool name.
    LOCAL = OUT.parent / "wiki" / "local"
    LOCAL.mkdir(parents=True, exist_ok=True)
    pub = OUT.parent / "wiki" / "tools"
    LOCAL_MARK = "<!-- generated above; your notes below survive -->"
    for rw in rows:
        nm = rw["name"]
        if (pub / f"{nm}.md").exists() or "/" in nm:
            continue
        page = LOCAL / f"{nm}.md"
        old = page.read_text() if page.exists() else ""
        tail = old.split(LOCAL_MARK, 1)[1] if LOCAL_MARK in old else "\n"
        measure = ("not measurable" if rw["observable"] == "none"
                   else f"{rw['value']} ({rw['observable']})")
        body = ["---", f"verified_at: {date.today().isoformat()}",
                f"kind: {rw['kind']}", f"scope: {rw['scope']}",
                f"activation: {rw['activation']}", "---", "",
                f"# {nm}", "",
                f"| | |", f"|---|---|",
                f"| kind | {rw['kind']} |",
                f"| scope | {rw['scope']} |",
                f"| activation | {rw['activation']} |",
                f"| measure | {measure} |",
                f"| last used | {rw['last_used']} |",
                f"| status | {rw['status']} |", "",
                "_No ledger decision yet. Installed, observed, undecided._", "",
                LOCAL_MARK]
        page.write_text("\n".join(body) + tail)

    # A single entry point for "which repo is which" in Obsidian. Local only:
    # the list of repos is itself private.
    if repos():
        idx = ["---", f"verified_at: {date.today().isoformat()}", "---", "",
               "# Repo map", "",
               "Every repo this brain watches. Each page lists the tooling "
               "installed *in that repo* — the surface the global harness "
               "does not show.", "",
               "| Repo | Stack type | Project-level tools | Stack page |",
               "|---|---|---:|---|"]
        for repo, stack_type in repos():
            n = len(project_tooling(repo))
            idx.append(f"| {repo.name} | {stack_type} | {n} | [[{repo.name}]] |")
        idx += ["", "## How scope works", "",
                "- **Global** — `~/.claude`, shared by every repo. Rot here "
                "costs context in every session.",
                "- **Per repo** — `<repo>/.claude/` and `.mcp.json`. Invisible "
                "from anywhere else.",
                "",
                "A tool useful everywhere belongs global. A tool useful to one "
                "stack belongs in that repo. A tool useful nowhere belongs in "
                "the ledger as a no.", ""]
        (stacks / "MAP.md").write_text("\n".join(idx))

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
           "| Scope | Kind | Name | Activation | Measure | Last used | Status |",
           "|---|---|---|---|---:|---|---|"]
    for r in sorted(rows, key=lambda x: (x["scope"] != "global", x["scope"],
                                         x["kind"], str(x["value"]))):
        link = (f"[[{r['name']}]]" if r["kind"] in ("skill", "mcp")
                else f"`{r['name']}`")
        measure = "not measurable" if r["observable"] == "none" else f"{r['value']}"
        md.append(f"| {r['scope']} | {r['kind']} | {link} | {r['activation']} | "
                  f"{measure} | {r['last_used']} | {r['status']} |")
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
