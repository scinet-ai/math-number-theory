#!/bin/bash
# Spot-verification of the computed Owings thresholds (target: well under 5 min).
# Re-checks, from scratch where cheap:
#   1. n(2) = 14 by SAT-free exhaustive enumeration of all 2^14 colourings.
#   2. The lower-bound witnesses with the independent clique-based checker.
#   3. The stored DRAT unsatisfiability certificates with drat-trim,
#      after regenerating each boundary CNF deterministically and comparing
#      it byte-for-byte against the certified copy.
# Exits nonzero on any mismatch.
set -euo pipefail
cd "$(dirname "$0")"

command -v kissat >/dev/null || { echo "kissat not found (brew install kissat)"; exit 2; }
DRAT=tools/drat-trim/drat-trim
[ -x "$DRAT" ] || { echo "building drat-trim"; cc -O2 -o "$DRAT" tools/drat-trim/drat-trim.c; }

echo "== 1. exhaustive SAT-free confirmation of n(2) = 14"
python3 code/exhaustive_check_n2.py

echo "== 2. independent re-check of lower-bound witnesses"
python3 code/check_coloring.py 2 results/witness_k2_n13.txt
python3 code/check_coloring.py 3 results/witness_k3_n45.txt
python3 code/check_coloring.py 4 results/witness_k4_n64.txt

echo "== 3. DRAT certificates"
for dir in certificates/k*/; do
    k=$(basename "$dir" | tr -d 'k')
    cnf=$(ls "$dir"/*.cnf)
    proof=$(ls "$dir"/*.drat)
    n=$(basename "$cnf" | sed -E 's/.*_n([0-9]+)\.cnf/\1/')
    if [ -f "$dir/from_lazy_pool" ]; then
        echo "-- k=$k n=$n: lazy-pool CNF; checking every clause is a genuine constraint"
        python3 code/audit_pool_cnf.py "$k" "$n" "$cnf"
    else
        echo "-- k=$k n=$n: regenerating CNF and comparing to certified copy"
        python3 code/generate_cnf.py "$n" "$k" "/tmp/owings_regen_k${k}_n${n}.cnf" >/dev/null
        cmp "/tmp/owings_regen_k${k}_n${n}.cnf" "$cnf"
        rm -f "/tmp/owings_regen_k${k}_n${n}.cnf"
    fi
    "$DRAT" "$cnf" "$proof" | grep -q "s VERIFIED" \
        && echo "   drat-trim: s VERIFIED" \
        || { echo "   drat-trim FAILED on k=$k"; exit 1; }
done

echo "ALL CHECKS PASSED"
