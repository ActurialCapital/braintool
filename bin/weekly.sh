#!/usr/bin/env bash
# Hygiene: what is installed, what it costs, whether the vault is sound.
# Local by necessity - reconcile.py reads ~/.claude, which no CI runner has.
#
#   ./bin/weekly.sh          the weekly pass
#
# Discovery (sweeping starred repos) is a SEPARATE command on purpose:
#   ./bin/discover.sh        when you are actually shopping
#
# Scoreboard so far: hygiene found four dead frameworks, a silently unapproved
# MCP hiding 32 tools, and ~17.7M of orphans. Discovery produced 110 candidates
# and zero adoptions. They do not deserve the same cadence.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "══ 1/4  reconcile — installed vs. observable ══"
python3 bin/reconcile.py

echo
echo "══ 2/4  churn — the outcome metric, recorded ══"
# Repo paths live in repos.txt (gitignored). Hardcoding them here published
# private paths in a public repo - twice. See repos.txt.example.
EXISTING=()
if [ -f repos.txt ]; then
  while IFS= read -r r; do
    [ -z "$r" ] && continue
    case "$r" in \#*) continue ;; esac
    [ -d "$r/.git" ] && EXISTING+=("$r")
  done < repos.txt
fi
if [ ${#EXISTING[@]} -gt 0 ]; then
  python3 bin/churn.py "${EXISTING[@]}" --record > inventory/churn.md
  grep -E '^\*\*fix:feat' inventory/churn.md || true
  echo "  recorded to inventory/churn.jsonl ($(wc -l < inventory/churn.jsonl | tr -d ' ') points)"
else
  echo "  (no repos configured — cp repos.txt.example repos.txt and edit)"
fi

echo
echo "══ 3/4  pages — ledger to wiki ══"
python3 bin/pages.py

echo
echo "══ 4/4  lint — vault health ══"
python3 bin/lint.py || true

echo
echo "── next ──"
echo "  history  python3 bin/churn.py --history"
echo "  shop     ./bin/discover.sh"
echo "  record   every decision in ledger.md, including the noes"
