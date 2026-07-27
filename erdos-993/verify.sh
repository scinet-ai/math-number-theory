#!/bin/bash
# Spot-verification for the order-30 unimodality sweep (runs in ~2-3 minutes).
#
# What it does:
#   1. Rebuilds the checker from source (requires the bundled nauty source
#      to be configured: cd nauty2_8_9 && ./configure && make gtools.o).
#   2. Cross-checks the dynamic program against an independent brute force
#      on every tree with at most 10 vertices.
#   3. Reproduces the published Kadrawi--Levit--Yosef--Mizrachi record on a
#      known chunk of order 26 containing both non-log-concave trees: the
#      full order-26 sweep must find exactly 2 non-log-concave and 0
#      non-unimodal trees; here we re-run the full order 26 (about 3 min
#      single-core) and compare counts, sequences, and the run hash.
#   4. Re-runs one banked order-30 chunk (chosen by $1, default 137) and
#      compares its CHECK line against the banked log, certifying that the
#      banked result is reproducible bit-for-bit.
# Exits nonzero on any mismatch.
set -euo pipefail
cd "$(dirname "$0")"

CHUNK=${1:-137}

echo "== step 1: rebuild checker from source =="
if [ ! -f nauty2_8_9/gtools.o ]; then
    (cd nauty2_8_9 && ./configure -q && make gtools.o) > /dev/null
fi
gcc -o gentreeg_independence_verify -O3 -march=native -include plugin_decl.h \
    -DOUTPROC=check_tree -DSUMMARY=check_summary \
    nauty2_8_9/gentreeg.c independence_check_plugin.c nauty2_8_9/gtools.o
gcc -o gentreeg_independence_verify_debug -O3 -march=native -include plugin_decl.h \
    -DOUTPROC=check_tree -DSUMMARY=check_summary -DPRINT_ALL_SEQUENCES \
    nauty2_8_9/gentreeg.c independence_check_plugin.c nauty2_8_9/gtools.o
echo "ok"

echo "== step 2: brute-force cross-check, all trees on <= 10 vertices =="
python3 brute_force_crosscheck.py 1 10 ./gentreeg_independence_verify_debug

echo "== step 3: reproduce the published order-26 record =="
./gentreeg_independence_verify -q 26 > verify_order26_exceptions.txt 2> verify_order26_summary.txt
grep -q "CHECK trees=279793450 nonunimodal=0 nonlogconcave=2 hash=65b36344eebd45c3" \
    verify_order26_summary.txt || { echo "FAIL: order-26 summary mismatch"; exit 1; }
diff <(sort verify_order26_exceptions.txt) <(sort results/order26_exceptions.txt) \
    || { echo "FAIL: order-26 exception trees differ"; exit 1; }
echo "ok: 279,793,450 trees, 0 non-unimodal, exactly the 2 published non-log-concave trees"

echo "== step 4: re-run banked order-30 chunk ${CHUNK}/240 =="
[ -f "logs/chunk30_${CHUNK}.done" ] || { echo "FAIL: chunk ${CHUNK} not banked"; exit 1; }
./gentreeg_independence_verify -q 30 ${CHUNK}/240 > /dev/null 2> verify_chunk30.txt
banked=$(grep "^CHECK" "logs/chunk30_${CHUNK}.done" | sed 's/ cpu=.*//')
fresh=$(grep "^CHECK" verify_chunk30.txt | sed 's/ cpu=.*//')
[ "$banked" = "$fresh" ] || { echo "FAIL: chunk ${CHUNK} mismatch"; echo "banked: $banked"; echo "fresh:  $fresh"; exit 1; }
echo "ok: chunk ${CHUNK} reproduces banked counts and hash: $fresh"

echo "== step 5: aggregate all banked chunks against OEIS A000055(30) =="
python3 aggregate_order30.py

echo "VERIFY PASSED"
