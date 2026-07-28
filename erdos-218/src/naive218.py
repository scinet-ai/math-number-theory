#!/usr/bin/env python3
"""naive218.py -- independent tiny validator for erdos218.c (Erdős #218).

Simple (non-optimized, dependency-free) segmented sieve + the same triple
tallying logic, written independently: plain full-range bytearray sieve with
slice-assignment marking, no odd-only bitmap, no shared code with the C tool.
Prints the identical canonical CERT1/TOTAL1 (and optional EQ) lines so that
`diff` against the C tool's stdout must be empty.

Usage: naive218.py LO HI [CERT_WIDTH] [PRINT_EQ_K]
"""
import sys


def base_primes(limit):
    """Primes <= limit by plain sieve of Eratosthenes."""
    s = bytearray([1]) * (limit + 1)
    s[0:2] = b"\x00\x00"
    i = 2
    while i * i <= limit:
        if s[i]:
            s[i * i :: i] = b"\x00" * len(range(i * i, limit + 1, i))
        i += 1
    return [i for i in range(limit + 1) if s[i]]


def primes_in(lo, hi, bases):
    """Yield primes in [lo, hi) using a bytearray over the window."""
    lo = max(lo, 2)
    n = hi - lo
    s = bytearray([1]) * n
    for p in bases:
        if p * p >= hi:
            break
        start = max(p * p, ((lo + p - 1) // p) * p)
        if start < hi:
            s[start - lo :: p] = b"\x00" * len(range(start, hi, p))
    for i in range(n):
        if s[i]:
            yield lo + i


def main():
    LO = int(sys.argv[1])
    HI = int(sys.argv[2])
    W = int(sys.argv[3]) if len(sys.argv) > 3 else HI - LO
    K = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    if LO < 2:
        LO = 2
    if K and LO != 2:
        sys.exit("PRINT_EQ_K requires LO == 2")

    nW = (HI - LO + W - 1) // W
    # windows: [primes, first, last, gt, eq, lt]
    wins = [[0, 0, 0, 0, 0, 0] for _ in range(nW)]
    tot = [0, 0, 0, 0]  # primes, gt, eq, lt
    next_after = 0

    # The stream must run past HI until the two primes following the last
    # in-range prime are seen.  Sieve in chunks; extend until done.
    CHUNK = 1 << 21
    bases = base_primes(int((HI + (1 << 20)) ** 0.5) + 2)

    prev2 = prev1 = 0
    gen = 0
    done = False
    lo = LO
    out = sys.stdout.write
    while not done:
        hi = lo + CHUNK
        for cur in primes_in(lo, hi, bases):
            gen += 1
            if prev2:
                if LO <= prev2 < HI:
                    d1 = prev1 - prev2
                    d2 = cur - prev1
                    w = wins[(prev2 - LO) // W]
                    if d2 > d1:
                        w[3] += 1
                        tot[1] += 1
                    elif d2 == d1:
                        w[4] += 1
                        tot[2] += 1
                        if K:
                            out("EQ n=%d p=%d gap=%d\n" % (gen - 2, prev2, d1))
                            K -= 1
                    else:
                        w[5] += 1
                        tot[3] += 1
            if LO <= cur < HI:
                w = wins[(cur - LO) // W]
                w[0] += 1
                tot[0] += 1
                if not w[1]:
                    w[1] = cur
                w[2] = cur
            elif cur >= HI and not next_after:
                next_after = cur
            prev2, prev1 = prev1, cur
            if prev2 >= HI:
                done = True
                break
        lo = hi

    for k in range(nW):
        primes, first, last, gt, eq, lt = wins[k]
        assert primes == gt + eq + lt, "invariant violation window %d" % k
        wlo = LO + k * W
        whi = min(wlo + W, HI)
        nx = 0
        for j in range(k + 1, nW):
            if wins[j][1]:
                nx = wins[j][1]
                break
        if not nx:
            nx = next_after
        out(
            "CERT1 lo=%d hi=%d primes=%d first=%d last=%d next=%d "
            "gt=%d eq=%d lt=%d\n" % (wlo, whi, primes, first, last, nx, gt, eq, lt)
        )
    out(
        "TOTAL1 lo=%d hi=%d primes=%d gt=%d eq=%d lt=%d\n"
        % (LO, HI, tot[0], tot[1], tot[2], tot[3])
    )


if __name__ == "__main__":
    main()
