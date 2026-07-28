#!/bin/bash
# Spot-verification for the round-2 FOREST computation (runs in ~3-4 minutes).
#
#  1. Rebuilds the forest checker from the bundled nauty 2.8.9 source.
#  2. Re-runs the full end-to-end validation at TOTAL=12: explicit
#     enumeration of all 2,948 forests on <= 12 vertices, brute-force
#     2^n subset counts == product of component polynomials, counts ==
#     OEIS A005195, and bit-exact reproduction of every mini FCHECK line
#     (counts + FNV hash) by an independent Python implementation.
#  3. Re-runs Lane A (structural closure over the 149 non-log-concave
#     trees): must terminate CLOSED at level 3 with the banked counts.
#  4. Rebuilds the q-sets (deterministic; includes the Euler-transform and
#     A005195 cross-checks) and compares a digest against the banked one.
#  5. Re-runs two banked sweep chunks (k=26 chunk 0/8, k=29 chunk 5/96)
#     and compares their FCHECK lines (counts + hash) with the banked logs.
#  6. Re-aggregates all 186 banked chunk logs (per-order tree counts must
#     equal A000055, checks must equal trees x |q-set|, 0 non-unimodal)
#     and re-verifies the non-log-concave product census in Python.
# Exits nonzero on any mismatch.
set -euo pipefail
cd "$(dirname "$0")"

echo "== step 1: rebuild forest checker from source =="
if [ ! -f nauty2_8_9/gtools.o ]; then
    (cd nauty2_8_9 && ./configure -q && make gtools.o) > /dev/null
fi
gcc -O3 -march=native -include forest_plugin_decl.h \
    -DOUTPROC=forest_check_tree -DSUMMARY=forest_summary \
    -DPLUGIN_INIT='{ forest_init(); }' \
    -o gentreeg_forest_verify nauty2_8_9/gentreeg.c forest_check_plugin.c \
    nauty2_8_9/gtools.o
echo "ok"

echo "== step 2: end-to-end validation at TOTAL=12 =="
python3 test_small_end_to_end.py | tail -3

echo "== step 3: Lane A structural closure =="
python3 lane_a_closure.py > /tmp/lane_a_verify_$$.txt
grep -q "LANE_A_STATUS CLOSED" /tmp/lane_a_verify_$$.txt \
    || { echo "FAIL: closure did not close"; exit 1; }
grep -q "level 2: all 11175 products UNIMODAL" /tmp/lane_a_verify_$$.txt \
    || { echo "FAIL: level-2 count"; exit 1; }
grep -q -- "-> |H_2| = 97" /tmp/lane_a_verify_$$.txt \
    || { echo "FAIL: H_2 size"; exit 1; }
grep -q "level 3: all 10823 products UNIMODAL" /tmp/lane_a_verify_$$.txt \
    || { echo "FAIL: level-3 count"; exit 1; }
grep -q -- "-> |H_3| = 0" /tmp/lane_a_verify_$$.txt \
    || { echo "FAIL: H_3 not empty"; exit 1; }
rm -f /tmp/lane_a_verify_$$.txt
echo "ok: closure CLOSED (11175 pairs + 10823 triples all unimodal, H_3 empty)"

echo "== step 4: q-set rebuild (Euler + A005195 cross-checks inside) =="
before=$(cat qsets/qset_digest.txt)
python3 build_qsets.py > /dev/null
after=$(shasum -a 256 qsets/qset_k*.txt | shasum -a 256 | cut -d' ' -f1)
[ "$before" = "$after" ] || { echo "FAIL: q-set digest changed"; exit 1; }
echo "ok: digest $after"

echo "== step 5: re-run banked chunks k=26 0/8 and k=29 5/96 =="
for spec in "26 0 8" "29 5 96"; do
    set -- $spec
    QSET_FILE="qsets/qset_k$1.txt" ./gentreeg_forest_verify -q "$1" "$2/$3" \
        > /dev/null 2> /tmp/fverify_$$.txt
    banked=$(grep "^FCHECK" "logs/task_$1_$2_$3.done" | sed 's/ gentreeg_nout=.*//')
    fresh=$(grep "^FCHECK" /tmp/fverify_$$.txt | sed 's/ gentreeg_nout=.*//')
    [ "$banked" = "$fresh" ] || { echo "FAIL: chunk $1 $2/$3 mismatch"; \
        echo "banked: $banked"; echo "fresh:  $fresh"; exit 1; }
    echo "ok: chunk $1 $2/$3 reproduces banked counts and hash"
done
rm -f /tmp/fverify_$$.txt

echo "== step 6: aggregate all banked chunks + non-LC census recheck =="
python3 aggregate_forest_sweep.py | tail -4
python3 recheck_nonlc_products.py | tail -1

echo "VERIFY PASSED"
