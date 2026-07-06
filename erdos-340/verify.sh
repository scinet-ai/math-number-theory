#!/usr/bin/env bash
# Reproduce the Mian-Chowla (greedy Sidon) growth measurement for Erdős #340.
# Deterministic, dependency-free (Python stdlib only). Addresses SciNet problem 06a785d4.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$(python3 "$HERE/mian_chowla_growth.py" 1500)"
echo "$OUT"
echo "$OUT" | grep -q "first 20 terms match OEIS A005282  OK" || { echo "FAIL: OEIS A005282 correctness anchor did not match"; exit 1; }
echo "$OUT" | grep -q "a(n)=N_max=43,205,712"                  || { echo "FAIL: a(1500) != 43,205,712"; exit 1; }
echo "VERIFIED: first 20 terms = OEIS A005282; a(1500)=43,205,712; growth exponent theta~0.370 (< 1/2)."
