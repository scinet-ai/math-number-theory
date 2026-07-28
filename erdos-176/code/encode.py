#!/usr/bin/env python3
"""CNF encoder for Erdos #176 discrepancy of k-term APs.

N(k,l) = least N such that every f:{1..N}->{-1,+1} admits a k-term AP P with
|sum_{n in P} f(n)| >= l.

We encode "a colouring of [N] with NO k-AP of |sum| >= l exists":
variable b_i (DIMACS var i, 1<=i<=N) means f(i) = +1.
For each k-AP P, with T = #(+1 positions in P), sum = 2T - k, we require
|2T - k| <= l-1, i.e.  L <= T <= U with
    L = ceil((k-l+1)/2),  U = floor((k+l-1)/2).
Cardinality constraints via pysat CardEnc (sequential counter, Sinz 2005).

SAT at N  => a valid colouring of [N] exists => N(k,l) > N.
UNSAT at N => N(k,l) <= N.
"""
import sys
from math import ceil, floor
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool


def aps(N, k):
    """All k-term APs (as position tuples) inside [1..N], positive difference."""
    out = []
    d = 1
    while 1 + (k - 1) * d <= N:
        for a in range(1, N - (k - 1) * d + 1):
            out.append(tuple(a + i * d for i in range(k)))
        d += 1
    return out


def bounds(k, l):
    """T-window [L, U] equivalent to |2T-k| <= l-1."""
    L = ceil((k - l + 1) / 2)
    U = floor((k + l - 1) / 2)
    return max(L, 0), min(U, k)


def encode(N, k, l):
    """Return (clauses, nvars). Vars 1..N are the colouring bits."""
    L, U = bounds(k, l)
    pool = IDPool(start_from=N + 1)
    clauses = []
    for P in aps(N, k):
        lits = [p for p in P]  # var index == position
        if U < k:  # at most U of the k positive
            cnf = CardEnc.atmost(lits=lits, bound=U, vpool=pool,
                                 encoding=EncType.seqcounter)
            clauses.extend(cnf.clauses)
        if L > 0:  # at least L positive == at most k-L negatives
            cnf = CardEnc.atmost(lits=[-p for p in P], bound=k - L, vpool=pool,
                                 encoding=EncType.seqcounter)
            clauses.extend(cnf.clauses)
    return clauses, pool.top


def write_dimacs(path, clauses, nvars):
    with open(path, "w") as f:
        f.write(f"p cnf {nvars} {len(clauses)}\n")
        f.write("".join(" ".join(map(str, c)) + " 0\n" for c in clauses))


if __name__ == "__main__":
    N, k, l = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    path = sys.argv[4]
    clauses, nvars = encode(N, k, l)
    write_dimacs(path, clauses, nvars)
    print(f"N={N} k={k} l={l} vars={nvars} clauses={len(clauses)}")
