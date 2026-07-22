#!/usr/bin/env python3
"""Independent naive validator for Erdős #699: big-integer binomials, gcd, trial factoring.

Prints the SAME line format as erdos699.c ("W n i j" weak failures, "S n i j" strong
failures, "A n i" Sylvester–Schur anomalies, final CERT line) so outputs diff directly.
Shares nothing with the C implementation: no Kummer, no bitsets, no sieve tricks.
"""
import sys
from math import comb, gcd, isqrt


def prime_factors_binomial(x, n):
    """Prime factors of a binomial coefficient C(n,·): all are <= n (classical),
    so divide by primes <= n and insist the cofactor collapses to 1."""
    fs = set()
    for p in range(2, n + 1):
        if not is_prime(p):
            continue
        if x % p == 0:
            fs.add(p)
            while x % p == 0:
                x //= p
    assert x == 1, f"binomial had a prime factor > n?! leftover {x}"
    return fs


def is_prime(x):
    return x >= 2 and all(x % d for d in range(2, isqrt(x) + 1))


def main(nlo, nhi):
    pairs = weak = strong = anom = 0
    for n in range(nlo, nhi + 1):
        m = n // 2
        row = [comb(n, t) for t in range(m + 1)]
        pf = [prime_factors_binomial(v, n) if v > 1 else set() for v in row]
        for i in range(1, m + 1):
            if not any(p > i for p in pf[i]):
                print(f"A {n} {i}")
                anom += 1
            for j in range(i + 1, m + 1):
                pairs += 1
                shared = pf[i] & pf[j]
                if not any(p >= i for p in shared):
                    print(f"W {n} {i} {j}")
                    weak += 1
                # strong form differs only when i is prime (p = i possible)
                if is_prime(i) and i in shared and not any(p > i for p in shared):
                    print(f"S {n} {i} {j}")
                    strong += 1
    print(f"CERT {nlo} {nhi} pairs={pairs} weak={weak} strong={strong} anomalies={anom}")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
