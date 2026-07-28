#!/usr/bin/env python3
"""CNF encoder for Erdos #160 exact values.

Decision problem (N, k): does there exist c: {1..N} -> {1..k} such that every
4-term AP (a, a+d, a+2d, a+3d), d >= 1, a+3d <= N, contains >= 3 distinct
colours?

Encoding:
  * one-hot colour variables x[i][c], exactly-one per element (pairwise AMO);
  * pairwise-equality indicators e[i][j] for every pair {i,j} that co-occurs
    in some 4-AP, with the upward direction only:
        (x[i][c] & x[j][c]) -> e[i][j]        for every colour c.
    (e may be true spuriously; that only tightens the constraint, so the
    formula is equisatisfiable with the colouring problem.)
  * per 4-AP: at-most-one of its 6 equality indicators (pairwise AMO).
    A 4-term multiset has >= 3 distinct values iff its colour partition is
    (1,1,1,1) or (2,1,1) iff at most 1 of the 6 pairwise equalities holds.
  * symmetry breaking (sound: colours can be renamed so that first
    occurrences appear in increasing colour order): precedence scheme with
    "seen" variables s[i][c] ("colour c occurs in {1..i}"):
        s[i][c] <-> (s[i-1][c] | x[i][c]),   x[i][c] -> s[i-1][c-1]  (c>=2).

Exit: writes DIMACS to stdout or --out. Deterministic.
"""
import argparse
import sys


def aps(N):
    for d in range(1, (N - 1) // 3 + 1):
        for a in range(1, N - 3 * d + 1):
            yield (a, a + d, a + 2 * d, a + 3 * d)


def build(N, k, symbreak=True):
    clauses = []
    # x vars: x(i,c) = (i-1)*k + c, i in 1..N, c in 1..k
    def x(i, c):
        return (i - 1) * k + c

    nvars = N * k

    # exactly-one colour per element
    for i in range(1, N + 1):
        clauses.append([x(i, c) for c in range(1, k + 1)])
        for c1 in range(1, k + 1):
            for c2 in range(c1 + 1, k + 1):
                clauses.append([-x(i, c1), -x(i, c2)])

    # collect pairs occurring in APs
    ap_list = list(aps(N))
    pairs = {}
    for ap in ap_list:
        for u in range(4):
            for v in range(u + 1, 4):
                key = (ap[u], ap[v])
                if key not in pairs:
                    nvars += 1
                    pairs[key] = nvars

    # equality upward implication
    for (i, j), evar in pairs.items():
        for c in range(1, k + 1):
            clauses.append([-x(i, c), -x(j, c), evar])

    # per AP: at most one equality among its 6 pairs
    for ap in ap_list:
        evars = [pairs[(ap[u], ap[v])] for u in range(4) for v in range(u + 1, 4)]
        for a in range(6):
            for b in range(a + 1, 6):
                clauses.append([-evars[a], -evars[b]])

    if symbreak:
        # seen vars s(i,c)
        s = {}
        for i in range(1, N + 1):
            for c in range(1, k + 1):
                nvars += 1
                s[(i, c)] = nvars
        for i in range(1, N + 1):
            for c in range(1, k + 1):
                clauses.append([-x(i, c), s[(i, c)]])
                if i >= 2:
                    clauses.append([-s[(i - 1, c)], s[(i, c)]])
                    clauses.append([-s[(i, c)], x(i, c), s[(i - 1, c)]])
                else:
                    clauses.append([-s[(1, c)], x(1, c)])
                if c >= 2:
                    if i >= 2:
                        clauses.append([-x(i, c), s[(i - 1, c - 1)]])
                    else:
                        clauses.append([-x(1, c)])

    return nvars, clauses


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("N", type=int)
    ap.add_argument("k", type=int)
    ap.add_argument("--no-symbreak", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    nvars, clauses = build(args.N, args.k, symbreak=not args.no_symbreak)
    out = open(args.out, "w") if args.out else sys.stdout
    out.write("c erdos160 N=%d k=%d symbreak=%d\n" % (args.N, args.k, 0 if args.no_symbreak else 1))
    out.write("p cnf %d %d\n" % (nvars, len(clauses)))
    for cl in clauses:
        out.write(" ".join(map(str, cl)) + " 0\n")
    if args.out:
        out.close()


if __name__ == "__main__":
    main()
