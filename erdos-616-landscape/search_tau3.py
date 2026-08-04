#!/usr/bin/env python3
"""Randomized falsification search for the theorem t(8) = 2.

Builds random greedy-maximal (within a sampled candidate pool) 8-uniform
families satisfying the local property L(8) ("every subgraph on <= 21 vertices
has tau <= 1") and checks tau <= 2.  A single family with L(8) and tau >= 3
would DISPROVE the theorem -- this is the search's failure power.

Seeding: trials are run unplanted and planted with each of the three rigid
survivor configurations at r=8 (m = 4, 5, 6: E_i = (X \\ {x_i}) u B_i with
pairwise disjoint private (9-m)-sets B_i), i.e. the searches start inside the
structural regime where a tau >= 3 example would have to live (families
containing MEIFs of minimum size 4, 5 and 6 respectively).

L(8) checking is exact: a family violates L(8) iff some subfamily has union
<= 21 and empty intersection; any such subfamily contains a minimal one with
at most r+1 = 9 edges, and every prefix of a minimal violating subfamily (in
any order) has nonempty intersection, so DFS over subfamilies that extends
only while the running intersection is nonempty, with union-size pruning at
21 and depth cap 9, finds a violation iff one exists.  (Same checker design
as ../code/random_maximal_search.py, which was cross-validated against a
literal-definition oracle on 400 unfiltered random families in the t6/t7
round, by two implementations.)

Vertices are bitmask ints for speed.
"""
import random
import sys

R = 8
WINDOW = 3 * R - 3   # 21
MAXDEPTH = R + 1     # 9

def edge_mask(vs):
    m = 0
    for v in vs:
        m |= 1 << v
    return m

def violates_local_with(new, family, window=WINDOW, maxdepth=MAXDEPTH):
    """Is there a subfamily of family+[new] containing `new` with union <=
    window and empty intersection?  Exact via DFS (see module docstring)."""
    edges = family
    n = len(edges)

    def dfs(start, union, inter, depth):
        if depth > maxdepth:
            return False
        for idx in range(start, n):
            E = edges[idx]
            u = union | E
            if u.bit_count() > window:
                continue
            i = inter & E
            if i == 0:
                return True
            if dfs(idx + 1, u, i, depth + 1):
                return True
        return False

    return dfs(0, new, new, 1)

def full_local_check(family, window=WINDOW, maxdepth=MAXDEPTH):
    """From-scratch exact L(8) check of a whole family (final audit)."""
    n = len(family)
    def dfs(start, union, inter, depth):
        if depth > maxdepth:
            return False
        for idx in range(start, n):
            E = family[idx]
            u = union | E
            if u.bit_count() > window:
                continue
            i = inter & E
            if i == 0:
                return True
            if dfs(idx + 1, u, i, depth + 1):
                return True
        return False
    for s in range(n):
        if dfs(s + 1, family[s], family[s], 1):
            return False
    return True

def tau_of(family, nverts):
    """Exact tau capped at 3: returns 0, 1, 2, or 3 (meaning >= 3)."""
    if not family:
        return 0
    inter = (1 << nverts) - 1
    for E in family:
        inter &= E
    if inter:
        return 1
    for a in range(nverts):
        pa = 1 << a
        rest = [E for E in family if not (E & pa)]
        # is one extra vertex enough for the rest?
        ri = (1 << nverts) - 1
        for E in rest:
            ri &= E
        if ri:
            return 2
    return 3

def rigid_masks(m):
    """Rigid survivor configuration at r=8: X (m vertices) + m disjoint
    private (9-m)-sets."""
    X = list(range(m))
    edges = []
    v = m
    for i in range(m):
        B = list(range(v, v + (R - m + 1)))
        v += R - m + 1
        edges.append(edge_mask([x for x in X if x != i] + B))
    return edges, v

def trial(n, pool_size, plant_m, rng):
    family = []
    if plant_m:
        family, span = rigid_masks(plant_m)
        assert span <= n
    pool = set()
    verts = list(range(n))
    while len(pool) < pool_size:
        pool.add(tuple(sorted(rng.sample(verts, R))))
    for cand in pool:
        cm = edge_mask(cand)
        if cm in family:
            continue
        if not violates_local_with(cm, family):
            family.append(cm)
    return family, tau_of(family, n)

def main():
    quick = "--quick" in sys.argv
    rng = random.Random(616808)
    CONFIGS = [
        # (n, pool_size, plant_m, trials)
        (24, 4000, 4, 4),
        (26, 5000, 4, 3),
        (30, 6000, 4, 3),
        (25, 4000, 5, 4),
        (28, 5000, 5, 3),
        (24, 4000, 6, 4),
        (28, 5000, 6, 3),
        (24, 4000, None, 4),
        (28, 6000, None, 3),
    ]
    if quick:
        CONFIGS = [(24, 1500, 4, 1), (25, 1500, 5, 1), (24, 1500, 6, 1),
                   (24, 1500, None, 1)]
    total = 0
    worst = 0
    for (n, ps, plant, ntr) in CONFIGS:
        for t_i in range(ntr):
            fam, tau = trial(n, ps, plant, rng)
            total += 1
            worst = max(worst, tau)
            tag = f"planted-m{plant}" if plant else "unplanted"
            print(f"n={n} {tag:11s} |family|={len(fam):4d} tau={tau}", flush=True)
            if tau >= 3:
                print("*** COUNTEREXAMPLE CANDIDATE -- auditing from scratch ***")
                ok = full_local_check(fam)
                print(f"    from-scratch L(8) check: "
                      f"{'PASSES (genuine counterexample!)' if ok else 'fails (search bug)'}")
                print("    family:", [bin(E) for E in fam])
                sys.exit(2)
            if t_i == 0:
                assert full_local_check(fam), "incremental and full L-check disagree"
    print(f"\n{total} trials; max tau observed = {worst} (theorem predicts <= 2).")
    print("NO COUNTEREXAMPLE FOUND -- consistent with t(8) = 2")

if __name__ == "__main__":
    main()
