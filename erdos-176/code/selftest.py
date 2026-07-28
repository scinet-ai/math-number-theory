#!/usr/bin/env python3
"""Encoder self-test.

1) Semantic test of the cardinality encoding: for k<=6 and every l, enumerate
   ALL +-1 vectors of length N (small N): CNF (with colouring bits forced by
   assumptions) must be SAT iff the vector has no k-AP with |sum|>=l.
2) Crossover test: SAT/UNSAT crossover of the encoder (via Glucose42) must
   match brute-force DFS N(k,l) on small cells.
Exit 0 iff all pass.
"""
import itertools
import subprocess
import sys

from pysat.solvers import Glucose42
from encode import encode, aps, bounds
from brute import longest


def direct_valid(vec, k, l):
    N = len(vec)
    for P in aps(N, k):
        s = sum(vec[p - 1] for p in P)
        if abs(s) >= l:
            return False
    return True


def semantic_test():
    fails = 0
    for (N, k) in [(8, 3), (9, 4), (10, 5), (9, 6)]:
        for l in range(1, k + 1):
            clauses, nvars = encode(N, k, l)
            with Glucose42(bootstrap_with=clauses) as s:
                for bits in itertools.product((1, -1), repeat=N):
                    assum = [i + 1 if bits[i] == 1 else -(i + 1) for i in range(N)]
                    got = s.solve(assumptions=assum)
                    want = direct_valid(bits, k, l)
                    if got != want:
                        print(f"SEMANTIC FAIL N={N} k={k} l={l} bits={bits} "
                              f"cnf={got} direct={want}")
                        fails += 1
    return fails


def crossover(k, l, Nmax=60):
    """Least N in [k..Nmax] with UNSAT, via encoder+Glucose; None if none."""
    for N in range(k, Nmax + 1):
        clauses, nvars = encode(N, k, l)
        with Glucose42(bootstrap_with=clauses) as s:
            if not s.solve():
                return N
    return None


def crossover_test():
    fails = 0
    # (k, l, known/brute Nmax)
    cells = [(3, 2, 20), (3, 3, 30), (4, 2, 20), (4, 3, 40), (5, 2, 30),
             (5, 3, 30), (4, 4, 40), (6, 2, 20)]
    for (k, l, Nmax) in cells:
        best, survived = longest(k, l, Nmax)
        want = None if survived else best + 1
        got = crossover(k, l, Nmax)
        tag = "ok" if got == want else "FAIL"
        if got != want:
            fails += 1
        print(f"crossover k={k} l={l}: brute={want} encoder={got} [{tag}]")
    return fails


if __name__ == "__main__":
    f1 = semantic_test()
    print(f"semantic test fails: {f1}")
    f2 = crossover_test()
    print(f"crossover test fails: {f2}")
    sys.exit(0 if f1 + f2 == 0 else 1)
