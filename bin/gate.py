#!/usr/bin/env python3
"""Gate: security + fit check on a shortlisted candidate. Run before adoption.

Do NOT write a scanner. Snyk's ToxicSkills audit (Feb 2026) found 1,467 malicious
payloads across 3,984 skills - a 36% flaw rate - and ClawHavoc poisoned 1,184
skills on ClawHub. That work is done; this wraps it.

Scanners tried in order, first one present wins:
    snyk-agent-scan             (installed)
    uvx snyk-agent-scan@latest  (no install needed)
    mcp-scan                    (deprecated name, still works)

Exit code IS the verdict:
    0 = pass
    1 = concerns - the scanner ran and found something
    2 = BLOCKED - the scanner could not run. Never treat this as a soft warning.

Usage:
    python3 bin/gate.py <repo-url-or-path> [--stack <stack>]
"""
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_env():
    """Read SNYK_TOKEN from this repo's .env (gitignored). A shell export does
    not reach a subprocess spawned by a tool or by CI, so read the file."""
    f = ROOT / ".env"
    if not f.exists():
        return
    for line in f.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip("'\""))


load_env()

SCANNERS = [
    (["snyk-agent-scan", "scan"], "snyk-agent-scan"),
    (["uvx", "snyk-agent-scan@latest", "scan"], "uvx snyk-agent-scan"),
    (["mcp-scan", "scan"], "mcp-scan (deprecated name)"),
]

# Static red flags. Split by file class: a SKILL.md that *mentions* .env while
# teaching secret hygiene is not a finding. Scanning prose for code tokens
# produced 10 false positives out of 11 on the first real candidate, which is
# how a gate trains you to click past it.
CODE_EXTS = {".py", ".js", ".mjs", ".cjs", ".ts", ".sh", ".bash", ".zsh"}
DOC_EXTS = {".md", ".markdown", ".txt", ".json", ".yaml", ".yml"}

CODE_FLAGS = [
    ("eval(", "evaluates dynamic code"),
    ("exec(", "executes dynamic code"),
    ("~/.ssh", "touches SSH keys"),
    ("~/.aws", "touches AWS credentials"),
    (".env", "reads env files"),
    ("base64 -d", "decodes obfuscated payload"),
    ("os.environ", "reads environment"),
    ("subprocess", "spawns processes"),
    ("child_process", "spawns processes"),
]
# In docs, only things that are dangerous *as instructions to follow*.
DOC_FLAGS = [
    ("curl | sh", "tells the user to pipe a remote script into a shell"),
    ("curl|sh", "tells the user to pipe a remote script into a shell"),
    ("curl | bash", "tells the user to pipe a remote script into a shell"),
    ("base64 -d", "decodes obfuscated payload"),
]


def find_scanner():
    for cmd, name in SCANNERS:
        if shutil.which(cmd[0]):
            return cmd, name
    return None, None


def static_scan(path: Path):
    """Grep the tree for red flags. Not a substitute for a real scanner."""
    hits = []
    for f in path.rglob("*"):
        if not f.is_file() or ".git" in f.parts:
            continue
        if f.suffix in CODE_EXTS:
            flags = CODE_FLAGS
        elif f.suffix in DOC_EXTS:
            flags = DOC_FLAGS
        else:
            continue
        try:
            body = f.read_text(errors="replace")
        except OSError:
            continue
        for token, why in flags:
            if token in body:
                hits.append((str(f.relative_to(path)), token, why))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="repo URL or local path")
    ap.add_argument("--stack", help="fit-check against wiki/stacks/<name>.md")
    args = ap.parse_args()

    print(f"# Gate — {args.target}\n")

    cmd, name = find_scanner()
    if cmd:
        print(f"scanner: {name}")
        r = subprocess.run(cmd + [args.target], capture_output=True, text=True)
        blob = (r.stdout + r.stderr)
        print(blob[-3000:])
        # A scanner that could not RUN must never be reported as a finding.
        # "unauthenticated" and "found nothing" are opposite facts; conflating
        # them turns a blocked gate into a soft warning you learn to ignore.
        could_not_run = any(s in blob for s in (
            "SNYK_TOKEN", "not authenticated", "No such file", "command not found",
            "Usage:", "error: unrecognized", "login"))
        # "scanned zero items" exits 0 and looks identical to "scanned and
        # clean". On a repo full of skills/*/SKILL.md the scanner reported
        # 'no mcp servers or skills found' - a layout mismatch, not a clean
        # bill of health. Anything not actually examined is inconclusive.
        # Normalise whitespace first: the scanner hard-wraps its output, so the
        # phrase arrives as "...or skills\nfound" and an exact match misses it.
        flat = " ".join(blob.lower().split())
        scanned_nothing = "no mcp servers or skills found" in flat
        if could_not_run:
            verdict = 2
        elif scanned_nothing:
            print("\n!! scanner examined NOTHING — layout not recognised.\n"
                  "   This is inconclusive, not clean. Point it at the "
                  "installed location (e.g. ~/.claude/skills/<name>) instead.")
            verdict = 2
        else:
            verdict = 0 if r.returncode == 0 else 1
    else:
        print("scanner: NONE AVAILABLE")
        verdict = 2

    p = Path(args.target)
    if p.exists():
        hits = static_scan(p)
        print(f"\n## Static red flags: {len(hits)}\n")
        for f, token, why in hits[:25]:
            print(f"- `{f}` — `{token}` ({why})")
        if hits:
            verdict = max(verdict, 1)
    else:
        print("\n(target is not a local path — clone it first for static scan)")

    if args.stack:
        sf = ROOT / "wiki" / "stacks" / f"{args.stack}.md"
        print(f"\n## Fit vs {args.stack}\n")
        print(f"Read {sf} and answer: does this help THIS stack, or is it "
              f"popular? Four frameworks were adopted on popularity and "
              f"invoked zero times.")

    label = ["PASS", "CONCERNS — read the findings above",
             "BLOCKED — scanner did not run; do not adopt"][verdict]
    print(f"\nverdict: {label}")
    if verdict == 2:
        print("  fix: export SNYK_TOKEN=... (https://app.snyk.io/account)")
        print("  the scanner itself needs no install — uvx fetches it")
    return verdict


if __name__ == "__main__":
    sys.exit(main())
