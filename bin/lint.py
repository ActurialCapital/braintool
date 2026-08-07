#!/usr/bin/env python3
"""Lint the vault: broken wikilinks, orphan pages, stale verified_at.

The piece that was missing. The repo had 45 broken wikilinks out of 46 and
nothing said so - the folder structure looked like a wiki without being one.

Local-only files (gitignored: inventory/, wiki/stacks/) are checked separately,
because their links are allowed to point at private pages that never ship.

Usage:
    python3 bin/lint.py            # public vault
    python3 bin/lint.py --all      # include gitignored local pages
"""
import argparse, re, subprocess, sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[\[([^\]|#]+)")
FENCE = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`\n]*`")
STALE_DAYS = 90


def prose(body: str) -> str:
    """Strip code before looking for links. `[[wikilinks]]` written inside
    backticks is documentation about the syntax, not a link to follow."""
    return INLINE_CODE.sub("", FENCE.sub("", body))


def tracked():
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "*.md"],
                         capture_output=True, text=True).stdout.split()
    return [ROOT / f for f in out]


def all_md():
    return [p for p in ROOT.rglob("*.md") if ".git" not in p.parts]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true",
                    help="include gitignored local pages")
    args = ap.parse_args()

    files = all_md() if args.all else tracked()
    pages = {p.stem for p in (all_md() if args.all else tracked())}

    broken, linked, stale, undated = [], set(), [], []
    for f in files:
        body = f.read_text(errors="replace")
        for target in LINK.findall(prose(body)):
            t = target.strip()
            linked.add(t)
            if t not in pages:
                broken.append((f.relative_to(ROOT), t))
        m = re.search(r"^verified_at:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", body, re.M)
        if m:
            age = (date.today() - date.fromisoformat(m.group(1))).days
            if age > STALE_DAYS:
                stale.append((f.relative_to(ROOT), m.group(1), age))
        elif (f.parent.name in ("tools", "stacks", "patterns")
              and f.stem != "EXAMPLE"):
            undated.append(f.relative_to(ROOT))

    orphans = [p for p in (all_md() if args.all else tracked())
               if p.stem not in linked
               and p.stem not in ("README", "ledger", "EXAMPLE")
               and p.parent.name in ("tools", "stacks", "patterns")]

    print(f"pages: {len(pages)}   links: {len(linked)}   "
          f"scope: {'all (incl. local)' if args.all else 'tracked only'}\n")
    print(f"broken wikilinks : {len(broken)}")
    for f, t in broken[:20]:
        print(f"  {f} -> [[{t}]]")
    if len(broken) > 20:
        print(f"  ... and {len(broken) - 20} more")
    print(f"\norphan pages (nothing links here) : {len(orphans)}")
    for p in orphans[:10]:
        print(f"  {p.relative_to(ROOT)}")
    print(f"\nstale (verified_at > {STALE_DAYS}d) : {len(stale)}")
    for f, d, age in stale:
        print(f"  {f} — {d} ({age}d)")
    print(f"\nmissing verified_at : {len(undated)}")
    for p in undated:
        print(f"  {p}")

    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
