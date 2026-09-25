#!/usr/bin/env bash
# End-to-end synthetic demo: no network, no data files.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:src"
OUT="${1:-./thermal-demo}"
survey-thermal demo --out-dir "$OUT"
echo
echo "--- UHI summary (first 5 rows) ---"
head -5 "$OUT/uhi.csv"
echo
echo "--- heatwave events ---"
cat "$OUT/heatwaves.csv"
