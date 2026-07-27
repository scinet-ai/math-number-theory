#!/usr/bin/env python3
"""Independently re-verify every saved non-log-concave tree.

Rebuilds each tree from its parent array and recounts independent sets per
size with a DP written here in Python big-int arithmetic (sharing no code
with the C checker), then confirms that (a) the sequence matches the C
checker's output byte for byte, (b) the sequence is genuinely
non-log-concave, and (c) it is nevertheless unimodal.  Exits nonzero on any
failure.
"""
import sys

FILES = [
    "results/order28_nonlogconcave_trees.txt",
    "results/order29_nonlogconcave_trees.txt",
    "results/order30_nonlogconcave_trees.txt",
    "results/order26_exceptions.txt",
]


def conv(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def independence_sequence(parents):
    n = len(parents)
    children = [[] for _ in range(n + 1)]
    for child in range(2, n + 1):
        children[parents[child - 1]].append(child)

    def dfs(v):
        exc, inc = [1], [0, 1]
        for c in children[v]:
            ce, ci = dfs(c)
            cs = [(ce[i] if i < len(ce) else 0) + (ci[i] if i < len(ci) else 0)
                  for i in range(max(len(ce), len(ci)))]
            exc = conv(exc, cs)
            inc = conv(inc, ce)
        return exc, inc

    sys.setrecursionlimit(100)
    e, i = dfs(1)
    seq = [(e[k] if k < len(e) else 0) + (i[k] if k < len(i) else 0)
           for k in range(max(len(e), len(i)))]
    while seq[-1] == 0:
        seq.pop()
    return seq


def main():
    total = 0
    for path in FILES:
        for line in open(path):
            fields = dict(kv.split("=", 1) for kv in line.split()[1:])
            parents = [int(x) for x in fields["par"].split(",")]
            claimed = [int(x) for x in fields["seq"].split(",")]
            seq = independence_sequence(parents)
            assert seq == claimed, f"sequence mismatch in {path}: {parents}"
            assert any(seq[k] ** 2 < seq[k - 1] * seq[k + 1]
                       for k in range(1, len(seq) - 1)), \
                f"not actually non-log-concave: {parents}"
            rising, unimodal = True, True
            for k in range(len(seq) - 1):
                if seq[k + 1] < seq[k]:
                    rising = False
                elif seq[k + 1] > seq[k] and not rising:
                    unimodal = False
            assert unimodal, f"NON-UNIMODAL TREE FOUND: {parents}"
            total += 1
    print(f"re-verified {total} saved non-log-concave trees (exact big-int arithmetic):")
    print("all sequences match the C checker, all genuinely non-log-concave, all unimodal")


if __name__ == "__main__":
    main()
