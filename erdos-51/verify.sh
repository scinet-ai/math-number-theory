#!/bin/bash
# Re-verifies every computational claim of the Erdős #51 workspace from scratch.
# Total runtime: a few minutes (the big sieve itself is NOT re-run here; its
# output data/run_full.txt is re-certified independently in steps 5-6, and can
# be fully regenerated with:  ./sieve_fmin 194000000000 > data/run_full.txt).
set -e
cd "$(dirname "$0")"

echo "== 1. build the sieve"
cc -O2 -o sieve_fmin sieve_fmin.c -lm

echo "== 2. invphi selftest (vs brute-forced complete fibers, m <= 300)"
python3 invphi.py --selftest

echo "== 3. Theorem 1 instances k=1..40 (exhaustive inverse-totient fibers)"
python3 check_theorems.py 40 | tail -2

echo "== 4. independent numpy cross-check of the sieve table at N=1e7"
python3 verify_indep.py 10000000

echo "== 5. certification-lemma (Lemma C) constants"
python3 - <<'EOF'
from math import prod
P = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
assert prod(P[:10]) == 6469693230          # 29#
assert prod(p - 1 for p in P[:10]) == 1021870080
assert prod(P) == 200560490130             # 31#
assert prod(p - 1 for p in P) == 30656102400   # phi(31#)
N = 194000000000
A = N * 1021870080 // 6469693230
assert A == min(A, 30656102400), A
print("Lemma C constants OK; A_max(N=1.94e11) =", A)
EOF

echo "== 6. re-certify records of the full run via exact inverse totient"
if [ -f data/run_full.txt ]; then
    python3 verify_records.py data/run_full.txt
else
    # data/run_full.txt (87 MB) is not shipped in this repo. Regenerate it with
    #     ./sieve_fmin 194000000000 > data/run_full.txt 2> data/run_full.log
    # (~65 min single-core, ~4.2 GB RAM) and re-run ./verify.sh for the full leg.
    echo "NOTE: data/run_full.txt not present (87 MB, not shipped; regenerate as above)."
    echo "Falling back to re-certifying the bundled N=1e9 run instead:"
    python3 verify_records.py data/run_1e9.txt
fi

echo "ALL CHECKS PASSED"
