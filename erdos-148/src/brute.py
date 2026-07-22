#!/usr/bin/env python3
"""Independent brute-force counter for cross-validation (small k only).

Enumerates ALL levels of the search tree with exact Fraction arithmetic — no
divisor closure, no incremental factorization, no shared code with erdos148.c.
Deliberately the dumbest correct implementation we could write.
"""
import sys
from fractions import Fraction


def count(k: int, distinct: bool) -> int:
    def rec(r: Fraction, j: int, last: int) -> int:
        if j == 1:
            if r.numerator != 1:
                return 0
            n = r.denominator
            return 1 if (n > last if distinct else n >= last) else 0
        # j >= 2 terms left; next denominator n must leave a positive remainder
        lo = max(last + (1 if distinct else 0), int(1 / r) + 1, 2)
        hi = int(j / r)
        c = 0
        for n in range(lo, hi + 1):
            c += rec(r - Fraction(1, n), j - 1, n)
        return c

    if k == 1:
        return 1  # 1 = 1/1 in both variants
    return rec(Fraction(1), k, 0)


if __name__ == "__main__":
    kmax = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    for variant, distinct in (("distinct", True), ("multi", False)):
        vals = [count(k, distinct) for k in range(1, kmax + 1)]
        print(f"{variant}: {vals}")
