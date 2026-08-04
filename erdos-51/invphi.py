#!/usr/bin/env python3
"""Exact inverse totient: enumerate ALL n with phi(n) = m.

Method (classical, Contini--Croot--Shparlinski style): any n with phi(n) = m is a
product of prime powers p^e (distinct p) with phi(p^e) = p^(e-1)(p-1) | m and the
phi-values multiplying to m.  Candidate primes are exactly {d+1 prime : d | m}.
DFS over candidates in decreasing order, dividing m by each chosen phi(p^e).

Independent of the C sieve: uses sympy primality/factorization, no shared code.

Self-test: `python3 invphi.py --selftest` brute-forces phi over n <= 10^6 and
compares the complete fibers for every m <= 300 (all preimages of m <= 300 are
< 4.4*300 < 10^6 since n/phi(n) < 4.4 for n < 10^6, cf. Lemma 2 of the
obstruction pack: R(5) = 4.8125 needs n >= 11# = 2310, R(8)=5.85 needs n >= 19#
= 9699690 > 10^6, and preimages beyond 10^6 of such small m are impossible:
n > 10^6 with phi(n) <= 300 would need n/phi(n) > 3333 -- absurd).
"""
import sys
from sympy import isprime, factorint


def _divisors(fac):
    divs = [1]
    for p, e in fac.items():
        divs = [d * p**i for d in divs for i in range(e + 1)]
    return divs


def invphi(m):
    """Sorted list of all n >= 1 with phi(n) = m."""
    if m == 1:
        return [1, 2]
    if m % 2:
        return []
    divs = sorted(_divisors(factorint(m)))
    cand = [d + 1 for d in divs if isprime(d + 1)]
    cand.sort(reverse=True)          # big primes first; 2 is last
    res = []

    def rec(left, idx, cur):
        if left == 1:
            res.append(cur)
            if cur % 2:          # phi(2m) = phi(m) for odd m; 2 (=last
                res.append(2 * cur)  # candidate, d=1) is still available
            return
        for j in range(idx, len(cand)):
            p = cand[j]
            d = p - 1
            if d > left or left % d:
                continue
            mm = left // d
            n2 = cur * p
            rec(mm, j + 1, n2)       # exponent 1
            while mm % p == 0:       # higher powers p^e, phi = p^(e-1)(p-1)
                mm //= p
                n2 *= p
                rec(mm, j + 1, n2)

    rec(m, 0, 1)
    return sorted(res)


def fmin(m):
    pre = invphi(m)
    return pre[0] if pre else None


def _selftest():
    N = 10**6
    phi = list(range(N))
    for p in range(2, N):
        if phi[p] == p:              # p prime
            for q in range(p, N, p):
                phi[q] -= phi[q] // p
    fibers = {}
    for n in range(1, N):
        fibers.setdefault(phi[n], []).append(n)
    bad = 0
    for m in range(1, 301):
        want = fibers.get(m, [])
        got = invphi(m)
        if want != got:
            print("MISMATCH at m=%d: sieve=%s invphi=%s" % (m, want, got))
            bad += 1
    print("selftest: %d mismatches over m<=300 (complete fibers)" % bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        _selftest()
    for arg in sys.argv[1:]:
        m = int(arg)
        pre = invphi(m)
        print("m=%d  #preimages=%d  min=%s  max=%s" %
              (m, len(pre), pre[0] if pre else None, pre[-1] if pre else None))
