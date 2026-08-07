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

# Static red flags worth catching before any scanner runs. Cheap, and they map
# to the documented attack classes: tool poisoning, rug pulls, name shadowing.
RED_FLAGS = [
    ("curl | sh", "pipes a remote script straight into a shell"),
    ("curl|sh", "pipes a remote script straight into a shell"),
    ("eval(", "evaluates dynamic code"),
    ("~/.ssh", "touches SSH keys"),
    ("~/.aws", "touches AWS credentials"),
    (".env", "reads env files"),
    ("base64 -d", "decodes obfuscated payload"),
    ("os.environ", "reads environment"),
    ("subprocess", "spawns processes"),
]


def find_scanner():
    for cmd, name in SCANNERS:
        if shutil.which(cmd[0]):
            return cmd, name
    return None, None


def static_scan(path: Path):
    """Grep the tree for red flags. Not a substitute for a real scanner."""
    hits = []
    exts = {".md", ".py", ".js", ".mjs", ".ts", ".sh", ".json", ".yaml", ".yml"}
    for f in path.rglob("*"):
        if not f.is_file() or f.suffix not in exts or ".git" in f.parts:
            continue
        try:
            body = f.read_text(errors="replace")
        except OSError:
            continue
        for token, why in RED_FLAGS:
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
        if could_not_run:
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
