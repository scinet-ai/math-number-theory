"""Independent cross-check of the certified evaluator by brute force.

Digit-tests every integer below 11^7 for membership in K({0,1,2,4,5,7}, 11)
(no shared code with the evaluator's digit-string enumeration) and compares
the resulting head sum of 1/(n+1) against the evaluator's exact head.
"""
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from kempner import _exact_recip_sums, _digit_strings, SCALE

S = np.array([0, 1, 2, 4, 5, 7])
b, D = 11, 7
n = np.arange(b ** D, dtype=np.int64)
ok = np.ones(n.size, dtype=bool)
t = n.copy()
for _ in range(D):
    ok &= np.isin(t % b, S)
    t //= b
members = n[ok]
assert members.size == 6 ** D, "member count mismatch"
brute_head = float(np.sum(1.0 / (members.astype(np.float64) + 1.0))) - 1.0

head_lo = 0
for L in range(1, D + 1):
    lo, _ = _exact_recip_sums(_digit_strings([0, 1, 2, 4, 5, 7], b, L, True), 1)
    head_lo += lo
eval_head = head_lo / SCALE

print(f"members below 11^7: {members.size} (= 6^7)")
print(f"brute-force head sum (n>=1): {brute_head:.13f}")
print(f"evaluator   head sum (n>=1): {eval_head:.13f}")
assert abs(brute_head - eval_head) < 1e-12, "evaluator disagrees with brute force"
print("BRUTE-FORCE CROSS-CHECK PASSED")
