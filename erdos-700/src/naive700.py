#!/usr/bin/env python3
"""Tier-1 truth for Erdős #700: literal big-integer binomials and gcd.
Same output shape as erdos700.c with report_all=1 ("F n f" + "BIG n f" + CERT).
Shares nothing with the C implementation (no Kummer, no sieve, no digit tricks)."""
import sys
from math import comb, gcd, isqrt


def main(nlo, nhi):
    composites = bigs = 0
    for n in range(max(nlo, 4), nhi + 1):
        if all(n % d for d in range(2, isqrt(n) + 1)):
            continue  # prime
        composites += 1
        f = min(gcd(n, comb(n, k)) for k in range(2, n // 2 + 1))
        print(f"F {n} {f}")
        if f * f > n:
            print(f"BIG {n} {f}")
            bigs += 1
    print(f"CERT {nlo} {nhi} composites={composites} bigs={bigs}")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
