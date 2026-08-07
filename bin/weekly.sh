#!/usr/bin/env bash
# The weekly loop, run by hand. Everything here is local by necessity:
# reconcile.py reads ~/.claude, which no CI runner has.
#
#   ./bin/weekly.sh              reconcile + sweep (cached stars)
#   ./bin/weekly.sh --refresh    also re-pull stars from GitHub
#
# Output lands in inventory/ (gitignored where it maps this machine).
set -euo pipefail
cd "$(dirname "$0")/.."

REFRESH="${1:-}"

echo "══ 1/5  reconcile — installed vs. invoked ══"
python3 bin/reconcile.py

echo
echo "══ 2/5  churn — fix:feat, the outcome metric ══"
# Edit this list to match the repos you actually ship.
REPOS=(~/GitHub/JJB/HawaiiFarming/aloha-app ~/GitHub/JJB/HawaiiFarming/aloha-data-migrations)
EXISTING=()
for r in "${REPOS[@]}"; do [ -d "$r/.git" ] && EXISTING+=("$r"); done
if [ ${#EXISTING[@]} -gt 0 ]; then
  python3 bin/churn.py "${EXISTING[@]}" > inventory/churn.md
  grep -E '^\*\*fix:feat' inventory/churn.md || true
else
  echo "  (no repos configured — edit REPOS in bin/weekly.sh)"
fi

echo
echo "══ 3/5  sweep — stars to candidates ══"
python3 bin/sweep.py ${REFRESH}

echo
echo "══ 4/5  pages — ledger to wiki ══"
python3 bin/pages.py

echo
echo "══ 5/5  lint — vault health ══"
python3 bin/lint.py || true

echo
echo "── next ──"
echo "  read   inventory/candidates.md"
echo "  gate   python3 bin/gate.py <repo-path> --stack <stack>"
echo "  record every decision in ledger.md, including the noes"
