#!/usr/bin/env python3
"""Churn: the outcome metric. fix:feat per repo and scope, recorded over time.

A high fix:feat means work is not landing right the first time. This is what
the harness is ultimately judged on - a tool that raises throughput while
doubling the fix ratio is not helping.

The history is the point. A single ratio says nothing; a ratio moving after a
tooling decision is evidence. --record appends one row per repo per run to
inventory/churn.jsonl, and --history prints that series with ledger decisions
overlaid on the same timeline.

It does NOT claim causation. Decisions and churn are shown together; reading
them is your job.

Usage:
    python3 bin/churn.py <repo> [<repo> ...]           # report now
    python3 bin/churn.py <repo> ... --record           # also append to history
    python3 bin/churn.py --history                     # series + decision markers
"""
import argparse, json, re, subprocess, sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HIST = ROOT / "inventory" / "churn.jsonl"
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


def record(repo, kinds, scopes, since):
    HIST.parent.mkdir(parents=True, exist_ok=True)
    feats, fixes = kinds.get("feat", 0), kinds.get("fix", 0)
    row = {
        "date": date.today().isoformat(),
        "repo": Path(repo).name,
        "since": since,
        "feat": feats,
        "fix": fixes,
        "ratio": round(fixes / feats, 3) if feats else None,
        "scopes": {s: {"feat": d.get("feat", 0), "fix": d.get("fix", 0)}
                   for s, d in scopes.items() if d.get("feat", 0) >= 3},
    }
    with HIST.open("a") as fh:
        fh.write(json.dumps(row) + "\n")
    return row


def decisions():
    """Ledger rows as (date, tool, decision) - the markers on the timeline."""
    out = []
    for line in (ROOT / "ledger.md").read_text().splitlines():
        if not line.startswith("|") or line.count("|") < 5:
            continue
        c = [x.strip() for x in line.strip("|").split("|")]
        if len(c) < 3 or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", c[0]):
            continue
        tool = re.sub(r"\[\[|\]\]|`", "", c[1])
        out.append((c[0], tool, re.sub(r"\*\*", "", c[2])))
    return sorted(out)


def show_history():
    if not HIST.exists():
        print("no history yet — run with --record")
        return 1
    rows = [json.loads(l) for l in HIST.read_text().splitlines() if l.strip()]
    marks = defaultdict(list)
    for d, tool, dec in decisions():
        marks[d].append(f"{tool} {dec}")

    print("# Churn history\n")
    print("Decisions and churn on one timeline. Correlation is not causation —")
    print("read it, do not let it conclude for you.\n")
    by_repo = defaultdict(list)
    for r in rows:
        by_repo[r["repo"]].append(r)
    for repo, series in sorted(by_repo.items()):
        print(f"## {repo}\n")
        print("| Date | feat | fix | ratio | Δ | decisions that day |")
        print("|---|---:|---:|---:|---:|---|")
        prev = None
        for r in series:
            ratio = r["ratio"]
            delta = "—" if prev is None or ratio is None else f"{ratio - prev:+.2f}"
            note = "; ".join(marks.get(r["date"], [])) or ""
            print(f"| {r['date']} | {r['feat']} | {r['fix']} | "
                  f"{ratio if ratio is not None else '—'} | {delta} | {note} |")
            prev = ratio
        print()
    if len(rows) < 3:
        print(f"_{len(rows)} data point(s). A trend needs several weeks; "
              f"do not read a direction into this yet._")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repos", nargs="*")
    ap.add_argument("--since", default="6 months ago")
    ap.add_argument("--min-feats", type=int, default=3)
    ap.add_argument("--record", action="store_true", help="append to churn.jsonl")
    ap.add_argument("--history", action="store_true", help="print the series")
    args = ap.parse_args()

    if args.history:
        return show_history()
    if not args.repos:
        ap.error("give at least one repo, or use --history")

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
        rows = [(d.get("fix", 0) / d["feat"], s, d["feat"], d.get("fix", 0))
                for s, d in scopes.items() if d.get("feat", 0) >= args.min_feats]
        if rows:
            print("| Scope | feat | fix | ratio |")
            print("|---|---:|---:|---:|")
            for r, scope, f, x in sorted(rows, reverse=True)[:10]:
                print(f"| {scope} | {f} | {x} | **{r:.2f}** |")
        print()
        if args.record:
            record(repo, kinds, scopes, args.since)
    return 0


if __name__ == "__main__":
    sys.exit(main())
