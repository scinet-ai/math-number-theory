#!/usr/bin/env python3
"""Independent witness checker (shares no code with the encoder).

Usage: check_witness.py <k> <l> <witness-string>
witness-string: characters '+'/'-' (or '1'/'0'), position i = f(i), length N.
Exits 0 iff EVERY k-term AP in [1..N] has |sum| <= l-1 (i.e. the witness
proves N(k,l) > N). Prints the max |AP sum| found.
"""
import sys


def main():
    k, l, w = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3].strip()
    f = []
    for ch in w:
        if ch in "+1":
            f.append(1)
        elif ch in "-0":
            f.append(-1)
        else:
            print(f"bad char {ch!r}", file=sys.stderr)
            sys.exit(2)
    N = len(f)
    worst = 0
    for d in range(1, (N - 1) // (k - 1) + 1):
        for a in range(0, N - (k - 1) * d):
            s = sum(f[a + i * d] for i in range(k))
            worst = max(worst, abs(s))
            if abs(s) >= l:
                print(f"VIOLATION: a={a+1} d={d} sum={s} (|sum|>={l})")
                sys.exit(1)
    print(f"OK N={N} k={k} l={l}: all {k}-AP |sums| <= {worst} <= {l-1}")
    sys.exit(0)


if __name__ == "__main__":
    main()
