#!/usr/bin/env python3
"""Independent checker for witness colourings (no SAT machinery shared).

Given a colouring of {1,...,n} as a 0/1 string and a target size k, search
exhaustively for a k-element set A with A+A (doubles included) monochromatic,
where A+A must lie inside {1,...,n} (equivalently A is a subset of
{1,...,floor(n/2)}).

Reformulation used: A+A is monochromatic in colour c
  iff every a in A has colour(2a) = c            (vertex condition)
  and every pair a<b in A has colour(a+b) = c    (edge condition).
So such an A is exactly a k-clique in the graph G_c whose vertices are
{a <= n/2 : colour(2a) = c} and whose edges are {a,b} with colour(a+b) = c.
A straightforward branch-and-bound clique search decides this exactly.

Exit status 0: colouring is avoiding (no such A exists) -- a valid witness
               that n(k) > n.
Exit status 1: a monochromatic A+A was found (printed) -- not a witness.

Usage: check_coloring.py k coloring_file
  coloring_file holds one 0/1 string of length n (whitespace ignored).
"""
import sys


def iter_mono_sets(colours, k, limit=None):
    """Yield up to `limit` k-element sets A with A+A monochromatic.

    colours: list of 0/1, colours[i] is the colour of integer i+1.
    Yields (sorted A, colour) pairs.
    """
    n = len(colours)
    m = n // 2
    emitted = 0

    def col(i):
        return colours[i - 1]

    for c in (0, 1):
        vertices = [a for a in range(1, m + 1) if col(2 * a) == c]
        adj = {a: set() for a in vertices}
        for i, a in enumerate(vertices):
            for b in vertices[i + 1:]:
                if col(a + b) == c:
                    adj[a].add(b)
                    adj[b].add(a)

        stack = [([], vertices)]
        while stack:
            clique, cand = stack.pop()
            if len(clique) == k:
                yield sorted(clique), c
                emitted += 1
                if limit is not None and emitted >= limit:
                    return
                continue
            if len(clique) + len(cand) < k:
                continue
            for i, v in enumerate(cand):
                rest = [u for u in cand[i + 1:] if u in adj[v]]
                stack.append((clique + [v], rest))


def find_mono_set(colours, k):
    """Return one k-element A with A+A monochromatic (as (A, colour)), or None."""
    for hit in iter_mono_sets(colours, k, limit=1):
        return hit
    return None


if __name__ == "__main__":
    k = int(sys.argv[1])
    text = open(sys.argv[2]).read().split()
    bits = "".join(text)
    colours = [int(ch) for ch in bits]
    n = len(colours)
    hit = find_mono_set(colours, k)
    if hit is None:
        print(f"AVOIDING: no {k}-element A with A+A monochromatic in this "
              f"colouring of [1..{n}] (so n({k}) > {n})")
        sys.exit(0)
    A, c = hit
    sums = sorted({a + b for a in A for b in A})
    print(f"FOUND: A={A} colour={c} A+A={sums} -- colouring is NOT avoiding")
    sys.exit(1)
