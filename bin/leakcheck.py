#!/usr/bin/env python3
"""Leakcheck: refuse to publish private names. Runs before every commit.

This repo maps a machine and the private repos on it, and it has leaked twice:
inventory/inventory.md (private module names), then churn.jsonl (repo + scope
names). Both times a human eye caught it after the push. Both times the fix was
a new gitignore line, which is a fix for that file, not for the class.

Patterns live in .leakpatterns (gitignored - the private names themselves must
not be published by the thing that checks for them).

Exit 1 blocks the commit.

Usage:
    python3 bin/leakcheck.py           # check tracked + staged files
    python3 bin/leakcheck.py --install # install as a git pre-commit hook
"""
import re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS_FILE = ROOT / ".leakpatterns"

HOOK = """#!/bin/sh
exec python3 "$(git rev-parse --show-toplevel)/bin/leakcheck.py"
"""


def patterns():
    if not PATTERNS_FILE.exists():
        return []
    out = []
    for line in PATTERNS_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def staged_and_tracked():
    files = set()
    # --diff-filter=d excludes deletions: a file staged for REMOVAL still
    # exists in the working tree, and reading it flags content that is on its
    # way out of the repo.
    for cmd in (["git", "-C", str(ROOT), "ls-files"],
                ["git", "-C", str(ROOT), "diff", "--cached", "--name-only",
                 "--diff-filter=d"]):
        files.update(subprocess.run(cmd, capture_output=True, text=True)
                     .stdout.split())
    return [ROOT / f for f in sorted(files) if (ROOT / f).is_file()]


def main():
    if "--install" in sys.argv:
        hook = ROOT / ".git" / "hooks" / "pre-commit"
        hook.write_text(HOOK)
        hook.chmod(0o755)
        print(f"installed {hook}")
        return 0

    pats = patterns()
    if not pats:
        print("leakcheck: no .leakpatterns file — nothing to check", file=sys.stderr)
        return 0

    # Word boundaries: 'orchestra' must not match 'orchestration', or the
    # guard fires on its own source and gets switched off.
    rx = re.compile("|".join(rf"\b{re.escape(p)}\b" if p[0].isalnum()
                             else re.escape(p) for p in pats), re.I)
    hits = []
    for f in staged_and_tracked():
        if f.name in (".leakpatterns", "leakcheck.py"):
            continue
        try:
            body = f.read_text(errors="replace")
        except OSError:
            continue
        for i, line in enumerate(body.splitlines(), 1):
            m = rx.search(line)
            if m:
                hits.append((f.relative_to(ROOT), i, m.group(0)))

    if hits:
        print("LEAK: private names in files that would be published\n",
              file=sys.stderr)
        for f, i, tok in hits[:30]:
            print(f"  {f}:{i}  matches '{tok}'", file=sys.stderr)
        print(f"\n{len(hits)} hit(s). Either gitignore the file or scrub the name.",
              file=sys.stderr)
        return 1

    print(f"leakcheck: clean ({len(staged_and_tracked())} files, "
          f"{len(pats)} patterns)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
