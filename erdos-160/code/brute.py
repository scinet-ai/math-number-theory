#!/usr/bin/env python3
"""Independent exhaustive computation of h(N) for small N (cross-check for SAT
pipeline). Backtracking over colourings with first-occurrence canonical order;
h(N) = min k admitting a valid colouring. Exact, no SAT solver involved."""
import sys


def aps_through(N):
    """For each i, the list of 4-APs (as tuples) whose max element is i."""
    by_max = {i: [] for i in range(1, N + 1)}
    for d in range(1, (N - 1) // 3 + 1):
        for a in range(1, N - 3 * d + 1):
            t = (a, a + d, a + 2 * d, a + 3 * d)
            by_max[t[3]].append(t)
    return by_max


def feasible(N, k):
    by_max = aps_through(N)
    col = [0] * (N + 1)

    def ok(i):
        for t in by_max[i]:
            cs = {col[t[0]], col[t[1]], col[t[2]], col[t[3]]}
            if len(cs) < 3:
                return False
        return True

    def rec(i, used):
        if i > N:
            return True
        for c in range(1, min(used + 1, k) + 1):
            col[i] = c
            if ok(i) and rec(i + 1, max(used, c)):
                return True
        col[i] = 0
        return False

    return rec(1, 0)


def h_of(N):
    k = 1
    while not feasible(N, k):
        k += 1
    return k


if __name__ == "__main__":
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    for N in range(lo, hi + 1):
        print(N, h_of(N), flush=True)
