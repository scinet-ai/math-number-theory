#!/usr/bin/env python3
"""Growth analysis for F(k) (A006585) against the known bounds for Erdős #148.

Known (Bloom, erdosproblems.com/148, accessed 2026-07-21):
    2^(c^(k/log k))  <=  F(k)  <=  c0^((1/5+o(1)) * 2^k)
lower: Konyagin [Ko14]; upper: Elsholtz-Planitzer [ElPl21], c0 = 1.26408... (Vardi).

The doubly-exponential upper bound predicts log2 log2 F(k) ~ k + const.
We tabulate L(k) = log2 log2 F(k), its first differences, and the local
exponent-doubling ratio log2 F(k+1) / log2 F(k) (which -> 2 iff growth is
genuinely doubly exponential with base-exponent 2).
"""
import math
import sys

F = {1: 1, 2: 0, 3: 1, 4: 6, 5: 72, 6: 2320, 7: 245765, 8: 151182379}
FM = {1: 1, 2: 1, 3: 3, 4: 14, 5: 147, 6: 3462, 7: 294314, 8: 159330691}

# allow overriding/extending from the command line: growth.py k=8:151182379 ...
for arg in sys.argv[1:]:
    k, v = arg.split(":")
    F[int(k.lstrip("k="))] = int(v)

print(f"{'k':>2} {'F(k)':>14} {'log2 F':>9} {'L=log2 log2 F':>14} {'ΔL':>7} {'log2F(k)/log2F(k-1)':>20}")
prevL = prevlog = None
for k in sorted(F):
    if F[k] < 2:
        print(f"{k:>2} {F[k]:>14}")
        continue
    lg = math.log2(F[k])
    L = math.log2(lg)
    dL = f"{L - prevL:7.3f}" if prevL is not None else "      -"
    ratio = f"{lg / prevlog:20.3f}" if prevlog else " " * 20
    print(f"{k:>2} {F[k]:>14} {lg:9.3f} {L:14.3f} {dL} {ratio}")
    prevL, prevlog = L, lg

print("\nUpper-bound comparison: Elsholtz-Planitzer exponent (1/5)*2^k*log2(c0), c0=1.26408:")
c0 = 1.26408
for k in sorted(F):
    if F[k] < 2:
        continue
    ub_bits = 0.2 * (2 ** k) * math.log2(c0)
    print(f"  k={k}: log2 F(k) = {math.log2(F[k]):8.2f}   vs asymptotic-UB exponent {ub_bits:9.2f}"
          f"   ratio {math.log2(F[k])/ub_bits:6.3f}")
