#!/bin/bash
# C4: pairwise coprimality of all 803 escape terms (322,003 gcds), 3-way split.
set -u
cd "$(dirname "$0")/.."
XF=$(python3 -c "
from pathlib import Path
s=[int(l) for l in Path('results/survivors.txt').read_text().split() if int(l)<=200000]
assert len(s)==803
print(' '.join(f'results/xvals/x_{n}.txt' for n in s))")
src/pairgcd 0 3 $XF > results/pairgcd_0.log 2>&1 &
P1=$!
src/pairgcd 1 3 $XF > results/pairgcd_1.log 2>&1 &
P2=$!
src/pairgcd 2 3 $XF > results/pairgcd_2.log 2>&1 &
P3=$!
wait $P1; E1=$?
wait $P2; E2=$?
wait $P3; E3=$?
echo "pairgcd exits: $E1 $E2 $E3" >> results/certify_status.log
echo "PAIRGCD-COMPLETE exits $E1 $E2 $E3"
