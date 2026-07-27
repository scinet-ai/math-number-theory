#!/usr/bin/env python3
"""Count and (for small n) list ALL avoiding colourings at n = n(k)-1,
i.e. 2-colourings of {1,...,n} with no k-element A having A+A monochromatic.

For k=2, n=13 this is a 8192-case brute force -- exact and independent of
any SAT machinery.  For k=3, n=45 brute force over the constrained core
[2..44] (2^43) is too big, so this script only handles the brute-forceable
case and prints all extremal colourings up to colour swap.

Usage: count_extremal.py k n
"""
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from check_coloring import find_mono_set  # noqa: E402


def main(k, n):
    if n > 24:
        raise SystemExit("brute force limited to n <= 24")
    total = 0
    reps = []
    for mask in range(2 ** n):
        colours = [(mask >> i) & 1 for i in range(n)]
        if find_mono_set(colours, k) is None:
            total += 1
            if colours[0] == 0:  # canonical representative under colour swap
                reps.append("".join(map(str, colours)))
    print(f"k={k} n={n}: {total} avoiding colourings "
          f"({len(reps)} up to colour swap):")
    for r in sorted(reps):
        print(" ", r)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
