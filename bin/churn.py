#!/usr/bin/env python3
"""Churn: measure the feat -> 10x fix pattern, per repo and per scope.

A high fix:feat ratio means work is not landing right the first time. This is
the outcome signal the harness is ultimately judged on - a tool that raises
throughput but doubles the fix ratio is not helping.

Usage:
    python3 bin/churn.py <repo> [<repo> ...] [--since "6 months ago"]
"""
import argparse, re, subprocess, sys
from collections import defaultdict
from pathlib import Path

CC = re.compile(r"^(feat|fix|refactor|chore|docs|test|perf|style)(?:\(([^)]+)\))?!?:", re.I)


def analyse(repo, since):
    out = subprocess.run(
        ["git", "-C", repo, "log", f"--since={since}", "--format=%ad|%s", "--date=short"],
        capture_output=True, text=True)
    if out.returncode:
        return None
    kinds = defaultdict(int)
    scopes = defaultdict(lambda: defaultdict(int))
    for line in out.stdout.splitlines():
        if "|" not in line:
            continue
        _, subj = line.split("|", 1)
        m = CC.match(subj.strip())
        if not m:
            kinds["(non-conventional)"] += 1
            continue
        kinds[m.group(1).lower()] += 1
        scopes[m.group(2) or "(none)"][m.group(1).lower()] += 1
    return kinds, scopes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repos", nargs="+")
    ap.add_argument("--since", default="6 months ago")
    ap.add_argument("--min-feats", type=int, default=3)
    args = ap.parse_args()

    print(f"# Churn — since {args.since}\n")
    for repo in args.repos:
        res = analyse(repo, args.since)
        if not res:
            print(f"## {Path(repo).name}\n\nnot a git repo\n")
            continue
        kinds, scopes = res
        feats, fixes = kinds.get("feat", 0), kinds.get("fix", 0)
        ratio = fixes / feats if feats else 0
        print(f"## {Path(repo).name}\n")
        print(f"**fix:feat = {ratio:.2f}** ({fixes} fixes / {feats} feats)\n")
        rows = []
        for scope, d in scopes.items():
            f, x = d.get("feat", 0), d.get("fix", 0)
            if f >= args.min_feats:
                rows.append((x / f, scope, f, x))
        if rows:
            print("| Scope | feat | fix | ratio |")
            print("|---|---:|---:|---:|")
            for r, scope, f, x in sorted(rows, reverse=True)[:10]:
                print(f"| {scope} | {f} | {x} | **{r:.2f}** |")
        print()


if __name__ == "__main__":
    sys.exit(main())
