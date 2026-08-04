#!/bin/sh
# Re-verify from scratch all computational claims backing proofs/proof_t6_t7.md
# (the theorems t(6)=2 and t(7)=2 for Erdős problem #616).
#
#   sh verify_t6t7.sh
#
# Pure Python 3 stdlib, no dependencies. Runtime: ~1 min for steps 1-2,
# up to ~10 min for the randomized falsification step 3.
# (The sibling script ./verify.sh independently verifies the companion
#  small-r pack: t(r)=1 for r<=5, t(r)>=2 for r>=6, monotonicity.)
set -e
cd "$(dirname "$0")/code"
OUT="${TMPDIR:-/tmp}"

echo "== 1/4 classify_minimal.py: exhaustive MEIF classification (Lemmas 5 & 6) =="
python3 classify_minimal.py | tee "$OUT/erdos616_classify.out"
grep -q "ALL CLASSIFICATION CHECKS PASSED" "$OUT/erdos616_classify.out"

echo "== 2/4 gadget_check.py: lower-bound gadgets + Theorem 1 key-step extension check =="
python3 gadget_check.py | tee "$OUT/erdos616_gadget.out"
grep -q "ALL GADGET CHECKS PASSED" "$OUT/erdos616_gadget.out"

echo "== 3/5 random_maximal_search.py: randomized falsification (failure-power check) =="
python3 random_maximal_search.py | tee "$OUT/erdos616_random.out"
grep -q "NO COUNTEREXAMPLE FOUND" "$OUT/erdos616_random.out"

echo "== 4/5 planted_m5_search_r7.py: Case-B-flavored falsification at r=7 =="
python3 planted_m5_search_r7.py | tee "$OUT/erdos616_m5.out"
grep -q "NO COUNTEREXAMPLE FOUND" "$OUT/erdos616_m5.out"

echo "== 5/5 checker_crossval.py: DFS checker vs literal-definition oracle (400 families) =="
python3 checker_crossval.py | tee "$OUT/erdos616_crossval.out"
grep -q "CHECKER CROSS-VALIDATION PASSED" "$OUT/erdos616_crossval.out"

echo
echo "ALL t(6)/t(7) VERIFICATIONS PASSED"
