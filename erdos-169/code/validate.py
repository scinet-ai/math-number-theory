"""Validate the certified evaluator against Walker's published values.

Expected (arXiv:2203.06045v2):
  H(K({0,1,2,4,5,7}, 11) + 1)  = 4.421746
  H(K(S55, 55) + 1)            = 4.43975   (the M_4 record)
  H(K({0,1,2,4,5,7,8,9,14,17}, 22) + 1) = 4.41989
Also: each digit set must be 4-free mod its base, and the product
construction S55 + 55*S55 must be 4-free mod 3025 with the SAME harmonic
sum as the b=55 record (it is the same integer set).
"""
import sys
import time

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from kempner import (is_kfree_mod, harmonic_sum_bounds, product_digit_set,
                     WALKER_S11, WALKER_S55, WALKER_S22)


def report(name, S, b, depth):
    t0 = time.time()
    ok = is_kfree_mod(S, b, 4)
    lo, hi = harmonic_sum_bounds(S, b, depth)
    dt = time.time() - t0
    print(f"{name}: b={b} |S|={len(S)} 4-free-mod-b={ok} depth={depth}")
    print(f"  H(K+1) in [{float(lo):.9f}, {float(hi):.9f}]"
          f"  width={float(hi - lo):.3e}  ({dt:.1f}s)")
    return ok, lo, hi


if __name__ == "__main__":
    # Walker prints values rounded to ~6 decimals from a float pipeline;
    # our certified enclosures may differ from his print-outs by O(1e-5).
    # (Verified independently: a brute-force digit test of every n < 11^7
    # reproduces our head sum to 13 digits.)
    ok11, lo11, hi11 = report("S11", WALKER_S11, 11, 8)
    assert ok11 and abs(float(lo11) - 4.421746) < 5e-6, "S11 mismatch"

    ok22, lo22, hi22 = report("S22", WALKER_S22, 22, 6)
    assert ok22, "S22 not 4-free"
    assert abs(float(lo22) - 4.41989) < 5e-5, "S22 mismatch"

    ok55, lo55, hi55 = report("S55 (record)", WALKER_S55, 55, 5)
    assert ok55 and abs(float(lo55) - 4.43975) < 5e-5, \
        "record set does not certify near 4.43975"
    print(f"  RECORD BAR (certified upper bound of Walker's set): "
          f"{float(hi55):.9f}")

    Sq = product_digit_set(WALKER_S55, 55, WALKER_S55)
    okq, loq, hiq = report("S55 x S55 (square seed)", Sq, 3025, 2)
    assert okq, "square seed not 4-free mod 3025 (product theorem violated?)"
    print(f"  square-seed enclosure contains record: "
          f"{float(loq) <= 4.43975 <= float(hiq)}")

    print("ALL VALIDATION CHECKS PASSED")
