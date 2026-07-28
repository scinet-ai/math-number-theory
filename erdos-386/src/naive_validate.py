#!/usr/bin/env python3
"""
naive_validate.py — INDEPENDENT naive validator for Erdős #386 (ref 918f9da2).

Deliberately shares NO logic with erdos386_scan.c:
  * computes the actual integer C(n,k) with math.comb (exact bignum),
  * factors that integer by direct trial division d = 2, 3, 4, 5, ...
    (no sieve, no Legendre/Kummer valuations, no carry counting),
  * checks squarefreeness on the factorization itself,
  * checks the consecutive-prime property with sympy.nextprime chains.

Modes:
  scan N_LO N_HI [KMIN]   exhaustive naive scan over n in [N_LO,N_HI],
                          k in [max(KMIN,2), n//2]; prints SOLUTION lines in
                          the same format as erdos386_scan for exact diffing.
  check FILE              independently re-verify every SOLUTION line in FILE:
                          recompute C(n,k), confirm it equals the product of
                          the listed primes, that each listed factor is prime,
                          and that they are consecutive primes. Exit 0 iff all
                          lines verify.

Usage:
  python3 naive_validate.py scan 4 600 > out_naive.txt
  python3 naive_validate.py check out_production.txt
"""

import math
import re
import sys

from sympy import isprime, nextprime


def consecutive_prime_block(v, dmax):
    """If v is a product of consecutive primes (each to the 1st power), return
    the list of those primes; else None. Factors by naive trial division over
    ALL integers d = 2..dmax; requires the cofactor to reach 1 (any factor
    > dmax means the caller's bound was wrong -> treated as failure loudly)."""
    assert v >= 2
    factors = []
    d = 2
    while v > 1 and d <= dmax:
        if v % d == 0:
            v //= d
            if v % d == 0:
                return None          # square factor -> not squarefree
            factors.append(d)        # smallest remaining divisor is prime
        d += 1
    if v != 1:
        raise RuntimeError(f"cofactor {v} has a prime factor > {dmax}")
    # consecutive-prime chain (factors are ascending by construction)
    for a, b in zip(factors, factors[1:]):
        if nextprime(a) != b:
            return None
    return factors


def scan(n_lo, n_hi, kmin=2):
    n_lo = max(4, n_lo)
    kmin = max(2, kmin)
    nsol = 0
    for n in range(n_lo, n_hi + 1):
        for k in range(kmin, n // 2 + 1):
            c = math.comb(n, k)
            block = consecutive_prime_block(c, n)
            if block is not None:
                nsol += 1
                print(f"SOLUTION n={n} k={k} len={len(block)} "
                      f"primes={'*'.join(map(str, block))}")
    print(f"# NAIVE-STATS range=[{n_lo},{n_hi}] kmin={kmin} solutions={nsol}")


LINE_RE = re.compile(
    r"^SOLUTION n=(\d+) k=(\d+) len=(\d+) primes=([\d*]+)\s*$")


def check(path):
    n_checked = bad = 0
    with open(path) as fh:
        for line in fh:
            if not line.startswith("SOLUTION"):
                continue
            m = LINE_RE.match(line)
            if not m:
                print(f"MALFORMED: {line.rstrip()}")
                bad += 1
                continue
            n, k, ln = int(m[1]), int(m[2]), int(m[3])
            ps = [int(x) for x in m[4].split("*")]
            errs = []
            if not (2 <= k <= n - 2):
                errs.append("k out of range")
            if len(ps) != ln:
                errs.append("len mismatch")
            if len(set(ps)) != len(ps) or ps != sorted(ps):
                errs.append("primes not distinct/ascending")
            if not all(isprime(p) for p in ps):
                errs.append("non-prime listed")
            if any(nextprime(a) != b for a, b in zip(ps, ps[1:])):
                errs.append("primes not consecutive")
            if math.comb(n, k) != math.prod(ps):
                errs.append("C(n,k) != product of listed primes")
            n_checked += 1
            if errs:
                bad += 1
                print(f"FAIL n={n} k={k}: {'; '.join(errs)}")
            else:
                print(f"OK   n={n} k={k} C(n,k)={math.comb(n, k)} "
                      f"= {'*'.join(map(str, ps))}")
    print(f"# CHECK {path}: {n_checked} solution lines, {bad} failures")
    return 1 if bad or n_checked == 0 else 0


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "scan":
        kmin = int(sys.argv[4]) if len(sys.argv) > 4 else 2
        scan(int(sys.argv[2]), int(sys.argv[3]), kmin)
    elif len(sys.argv) == 3 and sys.argv[1] == "check":
        sys.exit(check(sys.argv[2]))
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    main()
