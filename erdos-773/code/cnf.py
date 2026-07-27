"""DIMACS CNF encoder for the level-N decision problem of Erdos #773:

    exists A subseteq {1..N} (roots), |A| >= t, N in A, A square-Sidon?

Encoding:
- vars 1..N: x_i  <=> root i selected (element i^2 in the set)
- collision clauses: for each pair-of-pairs with equal sum of squares,
  OR of negated selected roots
- unit clause x_N
- cardinality |A| >= t as at-most-(N-t) over the negations, Sinz sequential
  counter (aux vars N+1 ...). Deterministic output (fixed clause order).

Also usable as a module: write_cnf(path, N, t) returns (nvars, nclauses).
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sidon_common import collision_clauses


def at_most_k(literals, k, next_var):
    """Sinz sequential-counter clauses for at-most-k over literals.
    Returns (clauses, next_var)."""
    n = len(literals)
    clauses = []
    if k >= n:
        return clauses, next_var
    if k == 0:
        for l in literals:
            clauses.append([-l])
        return clauses, next_var
    # s[i][j] for i in 0..n-1, j in 1..k
    s = [[0] * (k + 1) for _ in range(n)]
    for i in range(n):
        for j in range(1, k + 1):
            s[i][j] = next_var
            next_var += 1
    l = literals
    clauses.append([-l[0], s[0][1]])
    for j in range(2, k + 1):
        clauses.append([-s[0][j]])
    for i in range(1, n):
        clauses.append([-l[i], s[i][1]])
        clauses.append([-s[i - 1][1], s[i][1]])
        for j in range(2, k + 1):
            clauses.append([-l[i], -s[i - 1][j - 1], s[i][j]])
            clauses.append([-s[i - 1][j], s[i][j]])
        clauses.append([-l[i], -s[i - 1][k]])
    return clauses, next_var


def build_cnf(N, t, force_last=True):
    """Return (nvars, clauses) for the level-N decision with target t.
    force_last: add unit clause x_N (used by the chain; lower-bound climbs
    at large N omit it)."""
    clauses = [[-i for i in cl] for cl in collision_clauses(N)]
    if force_last:
        clauses.append([N])  # root N must be selected
    # at-least-t over x_1..x_N  ==  at-most-(N-t) over (-x_1..-x_N)
    card, nv = at_most_k([-i for i in range(1, N + 1)], N - t, N + 1)
    clauses.extend(card)
    return nv - 1, clauses


def build_cnf_profile(N, t, S):
    """Level-N decision with target t, STRENGTHENED by the certified prefix
    profile S = [S(1), ..., S(N-1)] (list, S[m-1] = S(m)).

    Encoding: one bidirectional sequential counter over x_1..x_N counting
    TRUE variables: c[i][j] <=> 'at least j of x_1..x_i are selected',
    for 1 <= j <= t. Then:
      - assert c[N][t]                      (|A| >= t)
      - unit -c[m][S(m)+1] for each m < N with S(m)+1 <= t
        (valid for EVERY square-Sidon subset of the first N squares, since
        its restriction to {1..m} is square-Sidon in the first m squares;
        certified by the chain below level N)
      - unit x_N, collision clauses as in build_cnf.
    Bidirectional counter clauses (full equivalence both directions) so the
    prefix upper bounds propagate. Returns (nvars, clauses).
    """
    assert len(S) >= N - 1
    clauses = [[-i for i in cl] for cl in collision_clauses(N)]
    clauses.append([N])
    nv = N
    c = [[0] * (t + 1) for _ in range(N + 1)]  # c[i][j], i in 1..N, j in 1..t
    for i in range(1, N + 1):
        for j in range(1, min(i, t) + 1):
            nv += 1
            c[i][j] = nv
    for i in range(1, N + 1):
        for j in range(1, min(i, t) + 1):
            here = c[i][j]
            prev_same = c[i - 1][j] if j <= i - 1 else 0
            prev_less = c[i - 1][j - 1] if j - 1 >= 1 else -1  # -1 == true
            # here -> prev_same OR (x_i AND prev_less)
            if prev_same:
                clauses.append([-here, prev_same, i])
                if prev_less > 0:
                    clauses.append([-here, prev_same, prev_less])
            else:
                # j == i: all of x_1..x_i must be true
                clauses.append([-here, i])
                if prev_less > 0:
                    clauses.append([-here, prev_less])
            # monotone up: prev_same -> here ; (x_i AND prev_less) -> here
            if prev_same:
                clauses.append([-prev_same, here])
            if prev_less > 0:
                clauses.append([-i, -prev_less, here])
            elif prev_less == -1:  # j == 1: x_i -> c[i][1]
                clauses.append([-i, here])
    clauses.append([c[N][t]])
    for m in range(1, N):
        j = S[m - 1] + 1
        if j <= min(m, t):
            clauses.append([-c[m][j]])
    return nv, clauses


def write_cnf(path, N, t, profile=None):
    if profile is not None:
        nvars, clauses = build_cnf_profile(N, t, profile)
        with open(path, "w") as f:
            f.write(f"c erdos773 level decision N={N} t={t} "
                    f"profile-strengthened\n")
            f.write(f"p cnf {nvars} {len(clauses)}\n")
            for cl in clauses:
                f.write(" ".join(map(str, cl)) + " 0\n")
        return nvars, len(clauses)
    nvars, clauses = build_cnf(N, t)
    with open(path, "w") as f:
        f.write(f"c erdos773 level decision N={N} t={t}\n")
        f.write(f"p cnf {nvars} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")
    return nvars, len(clauses)


if __name__ == "__main__":
    N, t, path = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    nv, nc = write_cnf(path, N, t)
    print(f"wrote {path}: N={N} t={t} vars={nv} clauses={nc}")
