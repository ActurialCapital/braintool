#!/usr/bin/env bash
# Discovery: sweep starred repos for candidates. Run when shopping, not weekly.
#
#   ./bin/discover.sh              re-rank the cached pull
#   ./bin/discover.sh --refresh    re-pull stars from GitHub (~11 API calls)
#
# Nothing here is adopted. Every candidate still needs:
#   python3 bin/gate.py <path> --stack <stack>     security + fit
#   a row in ledger.md                             including the no
set -euo pipefail
cd "$(dirname "$0")/.."

python3 bin/sweep.py "${1:-}"

echo
echo "── read inventory/candidates.md ──"
echo "  Of 1057 stars, ~110 pass the keyword filter and 0 have been adopted."
echo "  That ratio is the point, not a failure. Adopt almost nothing."
