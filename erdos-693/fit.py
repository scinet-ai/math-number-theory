#!/usr/bin/env python3
"""fit.py — growth analysis of G(n,k) against (log n)^c.

Model: G(n,k) ~ C * (log n)^c, i.e. log G = c * log log n + log C.
Least-squares fit of log G on log log n over several n-ranges; also reports
where the witness gaps live inside [n, n^k] and a per-decade summary table.
Writes data/fit_summary.txt.
"""
import csv, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "data", "results.csv")
OUT = os.path.join(HERE, "data", "fit_summary.txt")

rows = []
for r in csv.reader(open(RESULTS)):
    rows.append((int(r[0]), int(r[1]), int(r[2]), int(r[3]), int(r[4]),
                 int(r[5])))
rows.sort()

lines = []


def say(s=""):
    lines.append(s)
    print(s)


def fit(data, lo):
    pts = [(n, G) for (n, G) in data if n >= lo]
    if len(pts) < 4:
        return None
    x = np.log(np.log(np.array([p[0] for p in pts], dtype=float)))
    y = np.log(np.array([p[1] for p in pts], dtype=float))
    c, b = np.polyfit(x, y, 1)
    yhat = c * x + b
    ss = 1 - np.sum((y - yhat) ** 2) / np.sum((y - np.mean(y)) ** 2)
    return c, math.exp(b), ss, len(pts)


for k in (2, 3):
    data = [(n, G) for (n, kk, G, gs, ge, cnt) in rows if kk == k]
    if not data:
        continue
    nmax = max(n for n, _ in data)
    say(f"=== k={k}:  {len(data)} values of n, range [{min(d[0] for d in data)}, {nmax}] ===")
    say(f"model  G(n,{k}) ~ C*(log n)^c   [fit of log G on log log n]")
    for lo in (10, 100, 1000, 10000, 100000):
        if lo > nmax:
            break
        f = fit(data, lo)
        if f:
            say(f"  n >= {lo:>6}:  c = {f[0]:.3f}   C = {f[1]:.3f}   "
                f"R^2 = {f[2]:.4f}   ({f[3]} pts)")
    say()
    say(f"  per-decade maxima (n, G, G/(log n)^2, G/(log n)^1.5, log n):")
    for lo_e in range(0, 7):
        dec = [(n, G) for (n, G) in data if 10 ** lo_e <= n < 10 ** (lo_e + 1)]
        if not dec:
            continue
        n, G = max(dec, key=lambda p: p[1])
        L = math.log(n)
        say(f"    n={n:>8}  G={G:>4}   G/log^2={G / L ** 2:6.3f}   "
            f"G/log^1.5={G / L ** 1.5:6.3f}   log n={L:6.2f}")
    say()
    say(f"  witness location (relative position of gap_start in [n, n^{k}]):")
    for (n, kk, G, gs, ge, cnt) in rows:
        if kk != k or n < 1000:
            continue
        if k == 2 and n not in (1000, 3160, 10000, 31620, 100000, 316200,
                                1000000):
            continue
        if k == 3 and n not in (1000, 2239, 5012, 10000):
            continue
        rel = (gs - n) / (n ** k - n)
        extra = f"  gs/n^2={gs / n ** 2:.4f}" if k == 3 else ""
        say(f"    n={n:>8}  G={G:>4}  gap at {gs}  rel-pos={rel:.4f}  "
            f"|A|={cnt}{extra}")
    say()

say("=== Poisson-Ford heuristic (context, not a proof) ===")
delta = 1 - (1 + math.log(math.log(2))) / math.log(2)
say(f"Ford density exponent delta = 1-(1+log log 2)/log 2 = {delta:.5f}")
say("Heuristic G(n,k) ~ (log n)^(1+delta) * (log log n)^(3/2)  ==> local")
say("log-log slope (d log G / d log log n) = 1 + delta + 1.5/log log n:")
for nn in (10 ** 4, 10 ** 5, 10 ** 6):
    say(f"    n={nn:>8}: predicted local slope = "
        f"{1 + delta + 1.5 / math.log(math.log(nn)):.3f}")

with open(OUT, "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"[fit] wrote {OUT}")
