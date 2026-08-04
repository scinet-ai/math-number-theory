#!/usr/bin/env python3
"""Post-run analysis of a sieve_fmin output: writes data/records_analysis.txt with
the top ratios (verified factorizations), census statistics, and the v_2 profile
of the ratio>=2 census.  Usage: analyze_run.py [data/run_full.txt]"""
import sys
from collections import Counter

from sympy import factorint

path = sys.argv[1] if len(sys.argv) > 1 else "data/run_full.txt"
E, H, R, done = [], 0, [], None
for line in open(path):
    t = line.split()
    if not t:
        continue
    if t[0] == "E":
        E.append((int(t[1]), int(t[2])))
    elif t[0] == "H":
        H += 1
    elif t[0] == "R":
        R.append((int(t[1]), int(t[2])))
    elif t[0] == "DONE":
        done = t[1:]

out = open("data/records_analysis.txt", "w")
def w(s=""):
    print(s)
    out.write(s + "\n")

def fstr(m):
    return "*".join(("%d" % p if e == 1 else "%d^%d" % (p, e))
                    for p, e in sorted(factorint(m).items()))

if done:
    N, A_max, tot, ge2, maxr = done
    w("DONE: N=%s A_max=%s totients=%s ratio>=2:%s (1.9<=r<2: %d) maxratio=%s" %
      (N, A_max, tot, ge2, H, maxr))
w("")
w("Running records (a, f(a), ratio, factorizations):")
for a, n in R:
    w("  a=%-12d n=%-12d %.6f   a=%s   n=%s" % (a, n, n / a, fstr(a), fstr(n)))
w("")
w("Top 25 of the ratio>=2 census by ratio:")
for a, n in sorted(E, key=lambda t: -(t[1] / t[0]))[:25]:
    w("  a=%-12d n=%-12d %.6f   a=%s   n=%s" % (a, n, n / a, fstr(a), fstr(n)))
w("")
v2c = Counter()
oddmin = 0
for a, n in E:
    v2c[(a & -a).bit_length() - 1] += 1
    if n % 2:
        oddmin += 1
w("ratio>=2 census: %d entries; %d have odd f(a), %d even f(a)" %
  (len(E), oddmin, len(E) - oddmin))
w("v_2(a) histogram of the census: " +
  ", ".join("v2=%d:%d" % (v, c) for v, c in sorted(v2c.items())))
w("")
w("Largest census entries (10 biggest a):")
for a, n in sorted(E, key=lambda t: -t[0])[:10]:
    w("  a=%-12d n=%-12d %.6f   a=%s" % (a, n, n / a, fstr(a)))
out.close()
