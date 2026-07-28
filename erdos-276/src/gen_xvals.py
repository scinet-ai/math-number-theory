#!/usr/bin/env python3
"""Compute exact decimal values of x_n for given indices (or for all survivors
<= 200000 with --survivors). Iterative exact bignum addition — independent of
the mod-p sieve path. Writes results/xvals/x_<n>.txt"""
import sys
from pathlib import Path

sys.set_int_max_str_digits(100_000)

ROOT = Path(__file__).resolve().parent.parent
q = int((ROOT / "data" / "q_decimal.txt").read_text().strip())
x0, x1 = 1 + q * q, 2 * q + q * q

if sys.argv[1] == "--survivors":
    ns = [int(l) for l in (ROOT / "results" / "survivors.txt").read_text().split()
          if int(l) <= 200_000]
else:
    ns = sorted(int(a) for a in sys.argv[1:])

outdir = ROOT / "results" / "xvals"
outdir.mkdir(parents=True, exist_ok=True)
want = set(ns)
a, b = x0, x1
if 0 in want:
    (outdir / "x_0.txt").write_text(str(a) + "\n")
if 1 in want:
    (outdir / "x_1.txt").write_text(str(b) + "\n")
for n in range(2, max(ns) + 1):
    a, b = b, a + b
    if n in want:
        (outdir / f"x_{n}.txt").write_text(str(b) + "\n")
print(f"wrote {len(ns)} exact terms to {outdir} (max index {max(ns)}, "
      f"largest has {len(str(b))} digits)")
