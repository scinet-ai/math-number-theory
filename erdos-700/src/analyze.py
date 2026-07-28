#!/usr/bin/env python3
"""Analysis for Erdős #700 over the computed f-table (run after run_shards.py).
Produces the numbers cited in the finding: the f>sqrt(n) census + density decay,
the classical-bound assertion, the f(n)=n/P(n) equality-family characterization,
and the extremal-envelope A_hat fit. Usage: analyze.py <ftable> <N>"""
import math
import sys
from collections import Counter


def main(path, N):
    spf = list(range(N + 1))
    for i in range(2, int(N**0.5) + 1):
        if spf[i] == i:
            for j in range(i * i, N + 1, i):
                if spf[j] == j:
                    spf[j] = i

    def fact(n):
        d = {}
        while n > 1:
            p = spf[n]
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            d[p] = e
        return d

    f = {}
    for ln in open(path):
        _, n, v = ln.split()
        f[int(n)] = int(v)
    print(f"composites: {len(f):,} (N={N})")

    # classical bound f(n) <= n/P(n): must be violation-free
    viol = [(n, v) for n, v in f.items() if v * max(fact(n)) > n]
    print(f"violations of f<=n/P: {len(viol)}")
    assert not viol

    bigs = sorted((n, v) for n, v in f.items() if v * v > n)
    print(f"f>sqrt(n) census: {len(bigs):,} terms; first {bigs[:5]}")
    for e in range(2, int(math.log10(N))):
        lo, hi = 10**e, 10**(e + 1)
        c = sum(1 for n, _ in bigs if lo <= n < hi)
        print(f"  density [1e{e},1e{e+1}): {c/(hi-lo):.6f} ({c})")
    print(f"  all bigs have P(n)<=sqrt(n): "
          f"{all(max(fact(n))**2 <= n for n, _ in bigs)}")

    eq = [n for n, v in f.items() if v == n // max(fact(n))]
    print(f"equality f=n/P: {len(eq):,} ({len(eq)/len(f):.1%} of composites)")
    eqP = sum(1 for n in eq if max(fact(n)) ** 2 > n)
    allP = sum(1 for n in f if max(fact(n)) ** 2 > n)
    print(f"  equality cases with P>sqrt(n): {eqP:,}/{len(eq):,} = {eqP/len(eq):.1%}")
    print(f"  baseline composites with P>sqrt(n): {allP:,} "
          f"(equality rate there: {eqP/allP:.1%})")
    sq = lambda n: all(e == 1 for e in fact(n).values())
    noneq = [n for n, v in f.items() if v != n // max(fact(n))]
    print(f"  squarefree: equality {sum(map(sq, eq))/len(eq):.1%} "
          f"vs non-equality {sum(map(sq, noneq))/len(noneq):.1%}")

    print("record envelope (A_hat = log(n/f)/log log n):")
    rec = 0
    for n, v in bigs:
        if v > rec:
            rec = v
            A = math.log(n / v) / math.log(math.log(n))
            print(f"  f({n})={v}  n/f={n/v:.1f}  A_hat={A:.3f}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
