#!/usr/bin/env python3
"""Complete overflow-truncated sweep tails for Erdos #411 (RELAY Job-0 script).

Reads a sweep hits file; for every line "T x r v" (orbit value v = g_{r-1}(x)
exceeded the u64 guard before step r), continues the orbit from v with Python
big integers through steps r..R and prints any further raw hits "H x r' c"
(g_{r'}(x) = c*x, integer c >= 2) to stdout, plus a "# tails" summary to stderr.

Append the output to the hits file, then re-run postprocess.py (which re-derives
every H line independently, so this script is not trusted by the merge).

Usage: complete_tails.py hits.txt R  [>> hits.txt]
Place in code/ next to probe.py (reuses its factorizer).
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # find probe.py next to this script
from probe import phi_big  # own trial division + Miller-Rabin + Brent rho

def main():
    hits_file, R = sys.argv[1], int(sys.argv[2])
    cache = {}
    n_tails = n_hits = 0
    for line in open(hits_file):
        parts = line.split()
        if not parts or parts[0] != "T":
            continue
        x, r, v = int(parts[1]), int(parts[2]), int(parts[3])
        n_tails += 1
        for rr in range(r, R + 1):
            v = v + phi_big(v, cache)
            if v % x == 0 and v // x >= 2:
                print(f"H {x} {rr} {v // x}")
                n_hits += 1
        if n_tails % 5000 == 0:
            print(f"# ... {n_tails} tails done", file=sys.stderr)
    print(f"# tails completed: {n_tails}, new hits: {n_hits}", file=sys.stderr)

if __name__ == "__main__":
    main()
