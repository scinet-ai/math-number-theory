#!/usr/bin/env python3
"""Exact N(k,l) by DFS over colourings with pruning — ground truth for small cells.

Usage: brute.py <k> <l> <Nmax>
Prints N(k,l) if it is <= Nmax, else reports N(k,l) > Nmax.
A prefix f[0..n-1] is feasible iff every COMPLETE k-AP inside it has |sum|<=l-1.
DFS extends position by position; on placing position n (1-indexed), only APs
whose last element is n need checking.
"""
import sys
sys.setrecursionlimit(100000)


def longest(k, l, Nmax):
    k_, l_ = k, l
    f = [0] * (Nmax + 1)  # 1-indexed
    best = [0]

    def ok(n):
        # check all k-APs ending at n
        d = 1
        while n - (k_ - 1) * d >= 1:
            s = 0
            for i in range(k_):
                s += f[n - i * d]
            if abs(s) >= l_:
                return False
            d += 1
        return True

    def dfs(n):
        best[0] = max(best[0], n - 1)
        if n > Nmax:
            return True  # survived to Nmax
        for v in (1, -1):
            f[n] = v
            if ok(n) and dfs(n + 1):
                f[n] = 0
                return True
            f[n] = 0
        return False

    survived = dfs(1)
    return best[0], survived


def main():
    k, l, Nmax = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    best, survived = longest(k, l, Nmax)
    if survived:
        print(f"N({k},{l}) > {Nmax} (colouring of [{Nmax}] exists)")
    else:
        print(f"N({k},{l}) = {best + 1} (longest valid colouring length {best})")


if __name__ == "__main__":
    main()
