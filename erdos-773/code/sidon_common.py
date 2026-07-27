"""Common utilities for Erdos #773: largest Sidon subset of {1^2,...,N^2}.

Conventions:
- We work with ROOTS i in {1..N}; the actual set elements are i^2.
- A subset A (of roots) is "square-Sidon" iff all pairwise sums i^2+j^2 (i<=j,
  both in A) are distinct, i.e. no two distinct unordered pairs {i,j} != {k,l}
  (repeats allowed) with i^2+j^2 == k^2+l^2 are fully contained in A.
- Collision clause: for each pair of pairs ({i,j},{k,l}) with equal sums, the
  union of the (distinct) roots involved cannot all be selected.

All arithmetic is exact Python int arithmetic.
"""

from collections import defaultdict


def collision_clauses(N):
    """All minimal 'not all of these roots' clauses for level N.

    Returns a sorted list of tuples of distinct roots (each tuple = set of
    roots that may not be simultaneously selected). Deduplicated; a clause
    that is a superset of another is NOT removed (rare; harmless), but exact
    duplicates are.
    """
    by_sum = defaultdict(list)
    for j in range(1, N + 1):
        jj = j * j
        for i in range(1, j + 1):
            by_sum[i * i + jj].append((i, j))
    clauses = set()
    for pairs in by_sum.values():
        if len(pairs) < 2:
            continue
        for a in range(len(pairs)):
            ia, ja = pairs[a]
            for b in range(a + 1, len(pairs)):
                ib, jb = pairs[b]
                roots = tuple(sorted(set((ia, ja, ib, jb))))
                clauses.add(roots)
    return sorted(clauses)


def is_square_sidon(roots):
    """Exact check: all pairwise sums of squares (i<=j) distinct."""
    rs = sorted(set(roots))
    if len(rs) != len(roots):
        return False
    sums = set()
    sq = [r * r for r in rs]
    for a in range(len(sq)):
        for b in range(a, len(sq)):
            s = sq[a] + sq[b]
            if s in sums:
                return False
            sums.add(s)
    return True


def brute_force_S(N):
    """Exact S(N) by DFS over roots 1..N (for small N only). Independent of
    the clause machinery above: uses direct sum-set collision tests."""
    best = 0

    def dfs(next_root, chosen, sums):
        nonlocal best
        remaining = N - next_root + 1
        if len(chosen) + remaining <= best:
            return
        if next_root > N:
            if len(chosen) > best:
                best = len(chosen)
            return
        r2 = next_root * next_root
        new = [r2 + c * c for c in chosen] + [2 * r2]
        if len(set(new)) == len(new) and not any(s in sums for s in new):
            for s in new:
                sums.add(s)
            chosen.append(next_root)
            dfs(next_root + 1, chosen, sums)
            chosen.pop()
            for s in new:
                sums.discard(s)
        dfs(next_root + 1, chosen, sums)
        if len(chosen) > best:
            best = len(chosen)

    dfs(1, [], set())
    return best


OEIS_A390813 = [1, 2, 3, 4, 5, 6, 6, 7, 8, 9, 9, 9, 10, 10, 11, 12, 12, 13,
                13, 13, 14, 14, 14, 15, 16, 17, 17, 17, 17, 18, 19, 19, 19,
                20, 20, 20, 21, 21, 22, 22, 22, 22, 23, 24, 24, 24, 24, 25,
                25, 26, 26, 27, 27, 27, 27, 28, 28, 29, 29, 29, 30, 30, 30,
                31, 31, 31, 32, 32]  # a(1)..a(68), fetched 2026-07-27
