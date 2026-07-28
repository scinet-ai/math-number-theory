#!/bin/bash
# Certify x_719, x_1799, x_1815, x_1827, x_1887 have no prime factor in (10^9, 10^11].
# 3 parallel range-split certify processes (ranges balanced by prime count).
set -u
cd "$(dirname "$0")/.."
XF="results/xvals/x_719.txt results/xvals/x_1799.txt results/xvals/x_1815.txt results/xvals/x_1827.txt results/xvals/x_1887.txt"
src/certify 1000000001   34000000000  $XF > results/certify_1e11_A.log 2>&1 &
P1=$!
src/certify 34000000001  69000000000  $XF > results/certify_1e11_B.log 2>&1 &
P2=$!
src/certify 69000000001  100000000000 $XF > results/certify_1e11_C.log 2>&1 &
P3=$!
wait $P1; E1=$?
wait $P2; E2=$?
wait $P3; E3=$?
echo "1e11 exits: A=$E1 B=$E2 C=$E3" >> results/certify_status.log
echo "RUN2-COMPLETE exits $E1 $E2 $E3"
