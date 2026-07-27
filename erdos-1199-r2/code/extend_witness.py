#!/usr/bin/env python3
"""Greedy witness extension: given an avoiding colouring of [1..n0], try all
2^(n-n0) colourings of the new elements n0+1..n (keeping [1..n0] fixed) and
report any that avoid a monochromatic A+A for k=4 at size n.  Cheap fallback
for finding lower-bound witnesses when SAT near the threshold gets slow.
Failure proves nothing (an avoiding colouring of [1..n] need not extend
ours); success is independently re-checkable with check_coloring.py.

Usage: extend_witness.py witness_file n
"""
import os
import sys
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_coloring import find_mono_set  # noqa: E402

K = 4


def main(path, n):
    bits = "".join(open(path).read().split())
    base = [int(ch) for ch in bits]
    n0 = len(base)
    assert n > n0, "target must exceed base length"
    for ext in product([0, 1], repeat=n - n0):
        colours = base + list(ext)
        if find_mono_set(colours, K) is None:
            out = os.path.join(os.path.dirname(os.path.abspath(path)),
                               f"witness_k{K}_n{n}.txt")
            with open(out, "w") as f:
                f.write("".join(map(str, colours)) + "\n")
            print(f"extended to n={n}: AVOIDING, saved {out}")
            return 0
    print(f"no extension of {path} to n={n} avoids; proves nothing")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], int(sys.argv[2])))
