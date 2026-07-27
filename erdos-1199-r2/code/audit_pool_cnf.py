#!/usr/bin/env python3
"""Audit a lazily-generated CNF: confirm every clause is a genuine constraint.

The lazy driver's UNSAT conclusion is sound only if each clause pair in its
CNF really is "S = A+A for some k-subset A of {1,...,floor(n/2)}, S must not
be monochromatic".  This script re-derives that property for every clause,
independently of the pool file: for each positive clause S it searches for a
k-subset A with A+A = S among the candidates {a : 2a in S, 2a <= n}, and
checks the matching negative clause is its exact mirror.

Usage: audit_pool_cnf.py k n cnf_file      (exit 0 iff every clause checks)
"""
import sys
from itertools import combinations, combinations_with_replacement


def sumset(A):
    return sorted({a + b for a, b in combinations_with_replacement(A, 2)})


def realizable(S, k, n):
    """Is S = A+A for some k-subset A of [1..n/2]?"""
    cand = sorted({s // 2 for s in S if s % 2 == 0 and s <= n})
    cand = [a for a in cand if 2 * a in set(S)]
    for A in combinations(cand, k):
        if sumset(A) == S:
            return True
    return False


def main(k, n, path):
    clauses = []
    for line in open(path):
        if line.startswith(("c", "p")):
            continue
        lits = [int(t) for t in line.split()[:-1]]
        if lits:
            clauses.append(lits)
    assert len(clauses) % 2 == 0, "clauses must come in pos/neg pairs"
    checked = 0
    for pos, neg in zip(clauses[0::2], clauses[1::2]):
        S = sorted(pos)
        assert sorted(-x for x in neg) == S, f"mirror mismatch at {S}"
        assert all(1 <= s <= n for s in S), f"literal out of range in {S}"
        assert realizable(S, k, n), f"clause {S} is not any A+A"
        checked += 1
    print(f"audited {checked} constraint pairs in {path}: all are genuine "
          f"A+A constraints for k={k}, n={n}")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
