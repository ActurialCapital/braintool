#!/usr/bin/env python3
"""Sweep: pull starred repos, keep the agent-tooling ones, drop what is already known.

Deliberately dumb: keyword relevance + freshness signals, no classifier. Every
decision it makes must be auditable by reading one line of this file. The
expensive judgement (fit, security) happens later, on the shortlist only.

Usage:
    python3 bin/sweep.py --refresh        # re-fetch from GitHub (~11 API pages)
    python3 bin/sweep.py                  # re-rank the cached pull
"""
import argparse, json, re, subprocess, sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "inventory" / "stars.json"
OUT = ROOT / "inventory" / "candidates.md"

# Relevance: does this repo plausibly change my harness?
KEYWORDS = {
    "high": ["mcp server", "mcp-server", "claude code", "claude-code", "agent skill",
             "agentskills", "skill", "subagent", "agent harness", "coding agent",
             "context window", "prompt caching", "llm wiki", "second brain",
             "agent memory", "tool use", "slash command", "hooks"],
    "med": ["agent", "llm", "rag", "eval", "knowledge graph", "codegen",
            "developer tool", "cli", "orchestration", "workflow"],
}
# Things I already decided on, or that are not harness tooling.
NOISE = ["awesome-", "tutorial", "course", "book", "roadmap", "interview",
         "cheatsheet", "papers", "collection of", "curated list"]


def fetch(user=None):
    """Page through starred repos via gh. Costs ~11 requests.

    `user/starred` needs a USER token. In GitHub Actions the default
    GITHUB_TOKEN is a repo-scoped installation token with no user identity, so
    that endpoint returns 'Resource not accessible by integration'. Star lists
    are public, so fall back to `users/<login>/starred`, which any token reads.
    """
    endpoint = f"users/{user}/starred" if user else "user/starred"
    repos, page = [], 1
    while True:
        out = subprocess.run(
            ["gh", "api", f"{endpoint}?per_page=100&page={page}",
             "--jq", ".[] | {full_name, description, stargazers_count, pushed_at, "
                     "archived, license: (.license.spdx_id // null), "
                     "topics, html_url, language}"],
            capture_output=True, text=True)
        if out.returncode and page == 1 and not user:
            # No user identity on this token - retry against the public endpoint.
            login = subprocess.run(
                ["gh", "api", "user", "--jq", ".login"],
                capture_output=True, text=True).stdout.strip()
            if login:
                print(f"user/starred unavailable; falling back to users/{login}/starred")
                return fetch(user=login)
            print("ERROR: cannot resolve a GitHub user for the star sweep.\n"
                  "  In Actions, set STARS_USER to the account whose stars to sweep.",
                  file=sys.stderr)
            return []
        if out.returncode or not out.stdout.strip():
            break
        batch = [json.loads(l) for l in out.stdout.strip().splitlines() if l.strip()]
        if not batch:
            break
        repos += batch
        page += 1
        if page > 20:  # ponytail: hard stop; 2000 stars is well past any real account
            break
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(repos, indent=2))
    return repos


def known_names():
    """Already installed, or already decided on. Neither is a candidate.

    Dedupe against inventory.json first - what is on disk is ground truth.
    Wiki/ledger mentions are the secondary source.
    """
    seen = set()
    inv = ROOT / "inventory" / "inventory.json"
    try:
        data = json.loads(inv.read_text())
        for row in data.get("rows", []):
            seen.add(row["name"].lower().replace("mcp__", "").strip())
        # Plugins are not rows - they are their own list, and missing them
        # let ponytail (installed and running) surface as a fresh candidate.
        for p in data.get("enabled_plugins", []):
            seen.add(p.split("@")[0].lower().strip())
    except (OSError, ValueError):
        pass
    for f in [ROOT / "ledger.md", *(ROOT / "wiki").rglob("*.md")]:
        try:
            for m in re.findall(r"\[\[([^\]]+)\]\]|`([^`]+)`", f.read_text()):
                seen.add((m[0] or m[1]).lower().strip())
        except OSError:
            continue
    return seen


def score(repo):
    """Relevance + freshness. Returns (points, reasons) or (0, _) to drop.

    A 'high' keyword is REQUIRED. Without it, 'agent' + 'active' matched half
    of a 1056-star account on the first run - that is a phone book, not a
    shortlist. The whole point is to adopt almost nothing.
    """
    text = f"{repo['full_name']} {repo.get('description') or ''} " \
           f"{' '.join(repo.get('topics') or [])}".lower()
    pts, why = 0, []
    for kw in KEYWORDS["high"]:
        if kw in text:
            pts += 3
            why.append(kw)
            break
    if not pts:
        return 0, ["no harness keyword"]
    for kw in KEYWORDS["med"]:
        if kw in text:
            pts += 1
            why.append(kw)
            break
    if any(n in text for n in NOISE):
        pts -= 3
        why.append("noise")
    if repo.get("archived"):
        pts -= 5
        why.append("ARCHIVED")
    pushed = (repo.get("pushed_at") or "")[:10]
    if pushed:
        stale_days = (date.today() - date.fromisoformat(pushed)).days
        if stale_days > 365:
            pts -= 3
            why.append(f"abandoned {stale_days}d")
        elif stale_days < 30:
            pts += 1
            why.append("active")
    # Star count is popularity, not fit, and popularity is what got four
    # unused frameworks installed. Worth at most one point.
    if repo.get("stargazers_count", 0) > 1000:
        pts += 1
        why.append("popular")
    if not repo.get("license"):
        pts -= 1
        why.append("no license")
    return pts, why


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--user", default=None,
                    help="sweep this account's public stars "
                         "(needed in CI, where the token has no user identity)")
    args = ap.parse_args()

    if args.refresh or not CACHE.exists():
        repos = fetch(args.user)
        print(f"fetched {len(repos)} starred repos")
    else:
        repos = json.loads(CACHE.read_text())
        print(f"{len(repos)} starred repos from cache "
              f"(--refresh to re-pull)")

    known = known_names()
    ranked = []
    for r in repos:
        short = r["full_name"].split("/")[-1].lower()
        if short in known or r["full_name"].lower() in known:
            continue
        pts, why = score(r)
        if pts > 0:
            ranked.append((pts, r, why))
    ranked.sort(key=lambda x: (-x[0], -x[1]["stargazers_count"]))

    md = ["# Candidates", "",
          f"Swept {len(repos)} stars on {date.today()}. "
          f"{len(ranked)} relevant, {len(repos) - len(ranked)} filtered out.", "",
          "Nothing here is adopted. Shortlist entries go through "
          "`bin/gate.py` (security) and a fit check against `wiki/stacks/` "
          "before they reach a PR.", "",
          "| Score | Repo | ⭐ | Last push | License | Why | What |",
          "|---:|---|---:|---|---|---|---|"]
    for pts, r, why in ranked[:args.top]:
        desc = (r.get("description") or "")[:80].replace("|", "/")
        md.append(f"| {pts} | [{r['full_name']}]({r['html_url']}) | "
                  f"{r['stargazers_count']} | {(r.get('pushed_at') or '')[:10]} | "
                  f"{r.get('license') or '—'} | {', '.join(why)} | {desc} |")
    OUT.write_text("\n".join(md) + "\n")

    print(f"relevant  : {len(ranked)}")
    print(f"filtered  : {len(repos) - len(ranked)}")
    print(f"written   : {OUT}")
    for pts, r, why in ranked[:10]:
        print(f"  {pts:3}  {r['full_name']:48} ⭐{r['stargazers_count']:<7} "
              f"{', '.join(why)}")


if __name__ == "__main__":
    sys.exit(main())
