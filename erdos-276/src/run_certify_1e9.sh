#!/bin/bash
# Certify the 10 smallest survivors have no prime factor <= 10^9.
# 3 parallel range-split certify processes. Logs to results/certify_1e9_{A,B,C}.log
set -u
cd "$(dirname "$0")/.."
XF=""
for n in 123 515 719 735 987 1143 1199 1383 1799 1815; do
  XF="$XF results/xvals/x_$n.txt"
done
rm -f results/certify_status.log
src/certify 2         400000000  $XF > results/certify_1e9_A.log 2>&1 &
P1=$!
src/certify 400000001 700000000  $XF > results/certify_1e9_B.log 2>&1 &
P2=$!
src/certify 700000001 1000000000 $XF > results/certify_1e9_C.log 2>&1 &
P3=$!
wait $P1; E1=$?
wait $P2; E2=$?
wait $P3; E3=$?
echo "exits: A=$E1 B=$E2 C=$E3" >> results/certify_status.log
echo "RUN1-COMPLETE exits $E1 $E2 $E3"
