#!/usr/bin/env bash
# Reproduce a fast slice of the Erdos #373 exhaustive search (SciNet problem e45294e8).
# Deterministic, dependency-free (Python stdlib only).
#   1. re-exhausts n <= 20000 (a few seconds) and asserts it finds EXACTLY the three known
#      Erdos solutions {9, 10, 16} and their four representations -- nothing else;
#   2. independently cross-checks each known representation with EXACT big-integer factorial
#      arithmetic (a second, completely different code path from the valuation searcher).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

echo "== 1. exhaustive re-search n <= 20000 (prime-valuation searcher) =="
OUT="$(python3 "$HERE/erdos373_search.py" 20000)"
echo "$OUT" | grep -E "SOLUTION|VERDICT|EXACTLY|NEW|ERROR|distinct"
echo "$OUT" | grep -q "EXACTLY the three known Erdos solutions" \
  || { echo "FAIL: did not certify exactly {9,10,16}"; exit 1; }
for s in \
  "SOLUTION: 9! = 7! 3! 3! 2!" \
  "SOLUTION: 10! = 7! 6!" \
  "SOLUTION: 10! = 7! 5! 3!" \
  "SOLUTION: 16! = 14! 5! 2!" ; do
  echo "$OUT" | grep -qF "$s" || { echo "FAIL: missing rediscovered solution: $s"; exit 1; }
done

echo
echo "== 2. independent big-integer cross-check of the known representations =="
python3 - <<'PY'
from math import factorial as F
known = {
    (9,  (7,3,3,2)),
    (10, (7,6)),
    (10, (7,5,3)),
    (16, (14,5,2)),
}
for n, facs in sorted(known):
    lhs = F(n)
    rhs = 1
    for a in facs:
        rhs *= F(a)
    ok = (lhs == rhs)
    assert ok, f"MISMATCH {n}! vs {facs}"
    assert max(facs) <= n-2, f"trivial-family violation for {n}"
    assert min(facs) >= 2 and all(facs[i] >= facs[i+1] for i in range(len(facs)-1))
    print(f"  OK  {n}! = " + " ".join(f"{a}!" for a in facs) + f"   (a_1={max(facs)} <= n-2={n-2})")
print("all known representations verified by exact factorial arithmetic")
PY

echo
echo "VERIFIED: n<=20000 yields exactly the three known Erdos #373 solutions {9,10,16};"
echo "          all four representations independently confirmed by big-integer arithmetic."
