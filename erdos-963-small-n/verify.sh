#!/bin/sh
# Re-verifies every claim in proof_smalln.md (exact f(n), n <= 27) from scratch.
# Deterministic; pure-stdlib Python 3. Runtime ~15-25 min, dominated by the two
# m=7 k=4 refutations. (Not to be confused with ./verify.sh, which checks the
# separate asymptotic write-up proof_main.md.)
set -e
cd "$(dirname "$0")"
PY="python3 -W ignore"

echo "== 1. Full enumeration of all valid patterns, m<=4 (h(1)..h(4)) =="
$PY search963.py h-exact 1 2 3 4

echo "== 2. Lower-bound refutations, fast engine =="
$PY search963.py refute h 5 3        # h(5) >= 3
$PY search963.py refute h 6 3        # h(6) >= 3
$PY search963.py refute h 7 4        # h(7) >= 4   (the key run, ~6 min)

echo "== 3. Direct f-mode refutations in dimension n (no reduction theorem) =="
$PY search963.py refute f 2 1
$PY search963.py refute f 3 1
$PY search963.py refute f 4 2
$PY search963.py refute f 5 2
$PY search963.py refute f 6 2
$PY search963.py refute f 7 2
$PY search963.py refute f 8 3        # f(8) >= 3 certified in dimension 8
$PY search963.py refute f 9 3        # f(9) >= 3 certified in dimension 9

echo "== 4. Independent engine (different arithmetic/order/keys; no root symmetry) =="
$PY verify_independent.py h 4 3 --nosym
$PY verify_independent.py h 5 3 --nosym
$PY verify_independent.py h 6 3 --nosym
$PY verify_independent.py f 8 3 --nosym
$PY verify_independent.py f 9 3 --nosym   # ~45 s; f-mode k=3 certified with NO root reduction
$PY verify_independent.py h 7 4      # independent h(7) >= 4 (~10-15 min)

echo "== 5. Upper-bound witnesses by direct subset-sum enumeration =="
$PY verify_witnesses.py

echo "== 6. Randomized falsifier (no random set may beat the table) =="
$PY falsifier.py falsify 3000 963

echo "ALL SMALL-N CHECKS PASSED"
