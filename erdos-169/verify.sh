#!/bin/sh
# Spot-verification for the Erdos #169 f(4) attack (target: < 5 minutes).
# 1. Certified evaluator vs Walker's published values (incl. the record bar).
# 2. Product theorem + maximality of the b=3025 square seed.
# 3. Every annealing result file: digit set is 4-free mod b (exhaustive test)
#    and its certified harmonic-sum enclosure contains the claimed value.
# Exits nonzero on any mismatch.
set -e
cd "$(dirname "$0")"

python3 code/validate.py

python3 - <<'EOF'
import glob, json, sys
sys.path.insert(0, "code")
from kempner import (is_kfree_mod, harmonic_sum_bounds, addable_digits,
                     product_digit_set, WALKER_S55)

square = product_digit_set(WALKER_S55, 55, WALKER_S55)
assert is_kfree_mod(square, 3025, 4), "square seed not 4-free mod 3025"
assert addable_digits(square, 3025, 4) == [], "square seed should be maximal"
print("square seed at b=3025: 4-free and maximal  OK")

RECORD_BAR = 4.439753370
for path in sorted(glob.glob("results/anneal_*.json")):
    ck = json.load(open(path))
    S, b, H_claim = ck["best_S"], ck["b"], ck["best_H"]
    assert 0 in S and is_kfree_mod(S, b, 4), f"{path}: set not 4-free mod {b}"
    lo, hi = harmonic_sum_bounds(S, b, ck["depth"])
    assert abs(float(lo) - H_claim) < 1e-9, \
        f"{path}: claimed {H_claim} but certified lower bound {float(lo)}"
    verdict = "NEW RECORD" if float(lo) > RECORD_BAR else "below record bar"
    print(f"{path}: b={b} m={len(S)} certified H_lo={float(lo):.9f} "
          f"({verdict})  OK")
print("ALL VERIFY CHECKS PASSED")
EOF

python3 code/brute_crosscheck.py
