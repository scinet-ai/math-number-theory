#!/usr/bin/env python3
"""Generate a DIMACS CNF encoding of the finite Owings threshold question.

Instance (n, k): variables x_1..x_n, where x_i true means integer i has
colour 1 and false means colour 0.  For every k-element subset A of
{1,...,floor(n/2)} (these are exactly the k-element A subsets of natural
numbers with A+A contained in {1,...,n}), let S = A+A including doubled
elements 2a.  Two clauses forbid S from being monochromatic:
    (x_s1 OR ... OR x_sm)      -- S is not entirely colour 0
    (-x_s1 OR ... OR -x_sm)    -- S is not entirely colour 1

Therefore:
  UNSAT  =>  every 2-colouring of {1,...,n} contains a k-element A with
             A+A monochromatic  =>  n(k) <= n.
  SAT    =>  the model is a 2-colouring of {1,...,n} with no such A
             =>  n(k) > n.

No symmetry breaking is added: an UNSAT certificate for this CNF proves the
statement for ALL colourings directly, with no side argument needed.

Usage: generate_cnf.py n k out.cnf
"""
import sys
from itertools import combinations, combinations_with_replacement


def sumset_clauses(n, k):
    """Yield the sorted sumset S = A+A for every valid k-subset A."""
    m = n // 2
    for A in combinations(range(1, m + 1), k):
        S = sorted({a + b for a, b in combinations_with_replacement(A, 2)})
        yield S


def write_cnf(n, k, path):
    clause_lines = []
    for S in sumset_clauses(n, k):
        pos = " ".join(str(s) for s in S)
        neg = " ".join(str(-s) for s in S)
        clause_lines.append(pos + " 0\n")
        clause_lines.append(neg + " 0\n")
    with open(path, "w") as f:
        f.write(f"c finite Owings instance n={n} k={k}\n")
        f.write(f"p cnf {n} {len(clause_lines)}\n")
        f.writelines(clause_lines)
    return len(clause_lines)


if __name__ == "__main__":
    n, k, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    num = write_cnf(n, k, out)
    print(f"wrote {out}: n={n} k={k} clauses={num}")
