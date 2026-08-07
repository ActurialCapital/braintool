#!/usr/bin/env python3
"""Generate wiki/tools/<name>.md from the ledger. The agent maintains the wiki.

Only tools the LEDGER mentions get a page. Pages are public, so they are built
from public facts: what the tool is, what was decided, why, and the evidence.

Deliberately NOT generated from inventory.json - that lists private MCP servers
and project-scoped tools, and those names do not belong in a public repo. The
inventory table is local and gitignored; these pages are the publishable half.

Usage:
    python3 bin/pages.py            # write missing pages
    python3 bin/pages.py --force    # rewrite all; notes below the marker still survive
"""
import argparse, re, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "wiki" / "tools"
MARK = "<!-- generated above; hand-written notes below survive --force -->"


def ledger_rows():
    """(tool, decision, evidence, reason) for every [[tool]] the ledger names."""
    body = (ROOT / "ledger.md").read_text()
    rows = {}
    for line in body.splitlines():
        if not line.startswith("|") or line.count("|") < 5:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5 or cells[0] in ("Date", "---"):
            continue
        d, tool, decision, evidence, reason = cells[:5]
        m = re.match(r"\[\[([^\]]+)\]\]|`([^`]+)`", tool)
        if not m:
            continue
        name = (m.group(1) or m.group(2)).strip()
        rows.setdefault(name, []).append((d, decision, evidence, reason))
    return rows


def render(name, entries):
    latest = entries[-1]
    decision = re.sub(r"\*\*", "", latest[1])
    out = [f"---",
           f"verified_at: {latest[0]}",
           f"status: {decision}",
           f"---", "",
           f"# {name}", "",
           f"**{decision}** as of {latest[0]}.", "",
           "## Decisions", "",
           "| Date | Decision | Evidence | Reason |",
           "|---|---|---|---|"]
    for d, dec, ev, why in entries:
        out.append(f"| {d} | {dec} | {ev} | {why} |")
    out += ["", "## Re-evaluate when", "",
            "- the evidence above changes (invocations, health, churn)",
            "- a sweep surfaces a replacement that scores higher on fit",
            "- `verified_at` is more than 90 days old", "",
            MARK, ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    TOOLS.mkdir(parents=True, exist_ok=True)
    rows = ledger_rows()
    written = kept = 0
    for name, entries in sorted(rows.items()):
        p = TOOLS / f"{name}.md"
        new = render(name, entries)
        if p.exists():
            # Anything below the marker is yours - typed in Obsidian, usually.
            # ALWAYS preserved, including under --force. --force means "rewrite
            # even if the generated half is unchanged", never "discard notes".
            old = p.read_text()
            tail = old.split(MARK, 1)[1] if MARK in old else ""
            new = new.rstrip("\n") + tail
            if new == old and not args.force:
                kept += 1
                continue
        p.write_text(new)
        written += 1
    print(f"tool pages: {written} written, {kept} unchanged, {len(rows)} total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
