#!/usr/bin/env python3
"""Growth diagnostics for the exact h(N) table vs the known asymptotic bounds.

Caveat printed with the output: N in the exact range is tiny; these numbers
are descriptive diagnostics, not evidence about asymptotics (the truth is not
even known to be a power of N vs subpolynomial).
"""
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
res = json.load(open(os.path.join(ROOT, "results.json")))
table = {int(n): v["h"] for n, v in res["table"].items()}
Ns = sorted(table)
jumps = sorted((j["first_N"], int(k)) for k, j in res["jumps"].items() if int(k) >= 3)

print("jump points (first N with h(N)=k):")
prev = None
for N, k in jumps:
    r = "" if prev is None else "  N_k/N_{k-1}=%.3f" % (N / prev)
    print("  k=%2d  N=%4d  log k/log N=%.3f%s" % (k, N, math.log(k) / math.log(N), r))
    prev = N

Nmax = Ns[-1]
hmax = table[Nmax]
print("\nat table end N=%d: h=%d" % (Nmax, hmax))
print("  empirical exponent log h/log N            = %.3f" % (math.log(hmax) / math.log(Nmax)))
print("  Shi-Dong 2026 upper-bound shape  N^{1/4}  = %.1f" % (Nmax ** 0.25))
print("  Hunter upper-bound shape  N^{log3/log22}  = %.1f" % (Nmax ** (math.log(3) / math.log(22))))
print("  lower-bound shape  exp((log N)^{1/9})     = %.1f" % (math.exp((math.log(Nmax)) ** (1 / 9))))
print("\n(Descriptive only: at these N the o(1)/constant terms dominate; the data")
print("cannot discriminate polynomial vs subpolynomial growth.)")
