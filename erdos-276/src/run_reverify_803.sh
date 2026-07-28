#!/bin/bash
# C3: independent re-verification that all 803 sieve survivors n <= 200000 have
# no prime factor <= 2*10^6 nor among the 5 large Table-2 primes.
# Path independence: exact bignum terms (Python iteration) + GMP trial division,
# vs. the sieve's uint64 recurrence mod p.
set -u
cd "$(dirname "$0")/.."
XF=$(python3 - <<'EOF'
from pathlib import Path
surv = [int(l) for l in Path("results/survivors.txt").read_text().split() if int(l) <= 200000]
assert len(surv) == 803
print(" ".join(f"results/xvals/x_{n}.txt" for n in surv))
EOF
)
src/certify 2       666666  $XF > results/reverify803_A.log 2>&1 &
P1=$!
src/certify 666667  1333333 $XF > results/reverify803_B.log 2>&1 &
P2=$!
src/certify 1333334 2000000 $XF > results/reverify803_C.log 2>&1 &
P3=$!
wait $P1; E1=$?
wait $P2; E2=$?
wait $P3; E3=$?
for p in 35239681 764940961 8288823481 10783342081 571385160581761; do
  src/certify $p $p $XF >> results/reverify803_big.log 2>&1 || E1=99
done
echo "reverify803 exits: A=$E1 B=$E2 C=$E3 (0=clean)" >> results/certify_status.log
echo "REVERIFY-COMPLETE exits $E1 $E2 $E3"
