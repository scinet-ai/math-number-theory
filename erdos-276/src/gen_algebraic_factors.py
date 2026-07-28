#!/usr/bin/env python3
"""For odd survivor indices 2n+1, write the exact algebraic factors
A_n = p F_n + q F_{n+1} and B_n = p L_n + q L_{n+1} (p=1), so that
x_{2n+1} = A_n * B_n (identity certified in Stage A7). Also asserts the
product equals the independently computed x_{2n+1}.
Usage: gen_algebraic_factors.py <odd_index> [...]"""
import sys
from pathlib import Path

sys.set_int_max_str_digits(100_000)
ROOT = Path(__file__).resolve().parent.parent
q = int((ROOT / "data" / "q_decimal.txt").read_text().strip())

def fib_pair(n):
    if n == 0:
        return (0, 1)
    a, b = fib_pair(n >> 1)
    c = a * (2 * b - a)
    d = a * a + b * b
    return (d, c + d) if n & 1 else (c, d)

outdir = ROOT / "results" / "factors"
outdir.mkdir(parents=True, exist_ok=True)
for arg in sys.argv[1:]:
    idx = int(arg)
    assert idx % 2 == 1, "odd indices only"
    n = (idx - 1) // 2
    Fn, Fn1 = fib_pair(n)
    # L_k = F_{k-1} + F_{k+1}:  L_n = 2F_{n+1} - F_n,  L_{n+1} = 2F_n + F_{n+1}
    Ln = 2 * Fn1 - Fn
    Ln1 = 2 * Fn + Fn1
    A = Fn + q * Fn1
    B = Ln + q * Ln1
    xfile = ROOT / "results" / "xvals" / f"x_{idx}.txt"
    x = int(xfile.read_text().strip())
    assert A * B == x, f"identity FAILED at index {idx}"
    (outdir / f"A_{idx}.txt").write_text(str(A) + "\n")
    (outdir / f"B_{idx}.txt").write_text(str(B) + "\n")
    print(f"x_{idx} = A*B verified exactly; A has {len(str(A))} digits, "
          f"B has {len(str(B))} digits")
