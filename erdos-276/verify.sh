#!/bin/bash
# Spot-verification for the erdos-276 workspace (target < 5 min). Nonzero exit on
# any mismatch. Assumes: clang, Homebrew gmp + primesieve, python3.
set -e
cd "$(dirname "$0")"
FAIL=0

echo "== [1/6] Stage A: full transcription + construction certificate (~30 s)"
python3 src/stage_a_transcription_check.py > /dev/null || { echo "FAIL stage A"; FAIL=1; }

echo "== [2/6] Survivor recount from stored bitmaps"
python3 - <<'EOF' || FAIL=1
from pathlib import Path
R = Path("results")
N = 1_000_000
bm = bytearray((N + 1 + 7) // 8)
for i in range(3):
    part = (R / f"bitmap_{i}.bin").read_bytes()
    assert len(part) == len(bm)
    for j, b in enumerate(part):
        bm[j] |= b
surv = [n for n in range(N + 1) if not (bm[n >> 3] >> (n & 7)) & 1]
assert len([n for n in surv if n <= 200_000]) == 803, "803 mismatch"
assert len(surv) == 3944, "3944 mismatch"
assert surv[:3] == [123, 515, 719], "smallest survivors mismatch"
assert all(n % 2 == 1 for n in surv), "even survivor found"
stored = [int(l) for l in (R / "survivors.txt").read_text().split()]
assert stored == surv, "survivors.txt mismatch"
print("   OK: 803 in [0,200000], 3944 in [0,1e6], all odd, file matches")
EOF

echo "== [3/6] certify spot-checks (independent GMP trial-division path)"
rebuild() { clang -O3 -I/opt/homebrew/include -L/opt/homebrew/lib -o "$1" "$2" -lprimesieve -lgmp; }
rebuild src/certify_v src/certify.c
src/certify_v 2 50000000 results/xvals/x_719.txt results/xvals/x_1799.txt results/xvals/x_1815.txt \
  | grep -q "no divisor" || { echo "FAIL: unexpected small divisor"; FAIL=1; }
src/certify_v 439243801 439243801 results/xvals/x_123.txt | grep -q "DIVISOR" \
  || { echo "FAIL: known divisor of x_123 not found"; FAIL=1; }
src/certify_v 3219067 3219067 results/xvals/x_735.txt | grep -q "DIVISOR" \
  || { echo "FAIL: known divisor of x_735 not found"; FAIL=1; }
echo "   OK"

echo "== [4/6] algebraic factorization identity (exact product assert inside)"
python3 src/gen_algebraic_factors.py 1827 719 > /dev/null || { echo "FAIL identity"; FAIL=1; }
echo "   OK"

echo "== [5/6] pairwise coprimality sample (first 100 survivor terms)"
clang -O3 -I/opt/homebrew/include -L/opt/homebrew/lib -o src/pairgcd_v src/pairgcd.c -lgmp
XF=$(python3 -c "
from pathlib import Path
s=[int(l) for l in Path('results/survivors.txt').read_text().split() if int(l)<=200000][:100]
print(' '.join(f'results/xvals/x_{n}.txt' for n in s))")
src/pairgcd_v 0 1 $XF | grep -q "all coprime" || { echo "FAIL pair gcd"; FAIL=1; }
echo "   OK"

echo "== [6/6] prime-count integrity of the certification logs"
python3 - <<'EOF' || FAIL=1
import re
from pathlib import Path
RANGE = r"RANGE \[\d+,\d+\]: tested (\d+) primes"
tot9 = tot11 = 0
for f in ["certify_1e9_A.log", "certify_1e9_B.log", "certify_1e9_C.log"]:
    tot9 += sum(map(int, re.findall(RANGE, (Path("results") / f).read_text())))
for f in ["certify_1e11_A.log", "certify_1e11_B.log", "certify_1e11_C.log"]:
    tot11 += sum(map(int, re.findall(RANGE, (Path("results") / f).read_text())))
assert tot9 == 50_847_534, f"pi(1e9) mismatch: {tot9}"
assert tot9 + tot11 == 4_118_054_813, f"pi(1e11) mismatch: {tot9 + tot11}"
print(f"   OK: pi(1e9)={tot9}, pi(1e11)={tot9 + tot11}")
EOF

rm -f src/certify_v src/pairgcd_v
if [ "$FAIL" -eq 0 ]; then echo "VERIFY: ALL CHECKS PASS"; else echo "VERIFY: FAILURES"; exit 1; fi
