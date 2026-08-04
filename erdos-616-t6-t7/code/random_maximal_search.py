#!/usr/bin/env python3
"""Randomized falsification search for the theorems t(6)=2 and t(7)=2.

Builds random (greedy-maximal within a sampled candidate pool) r-uniform
families satisfying the local property L(r) ("every subgraph on <= 3r-3
vertices has tau <= 1") and checks tau <= 2. A single family with L(r) and
tau >= 3 would DISPROVE the corresponding theorem.

L(r) checking: a family violates L(r) iff it has a subfamily with union
<= 3r-3 and empty intersection. Any such subfamily contains a minimal one
(w.r.t. inclusion), and a minimal empty-intersection family has at most r+1
edges (standard: the distinguished vertices x_j, one per omitted edge, are
distinct and all lie in E_1). So DFS over subfamilies with union-size pruning
at 3r-3 and depth cap r+1 is exact. The DFS extends only subfamilies with
nonempty intersection, reporting a violation the moment the intersection dies
while the union is still within the window; a minimal violating subfamily is
always reachable this way (order its edges arbitrarily: every prefix has
nonempty intersection by minimality... prefixes of a minimal family in any
order have nonempty intersection since they are proper subfamilies, and the
union of the full minimal family is within the window, hence so is every
prefix union).

Vertices are bitmask ints for speed.
"""
import random
import sys
from itertools import combinations

def edge_mask(vs):
    m = 0
    for v in vs:
        m |= 1 << v
    return m

def popcount(x):
    return bin(x).count("1")

def violates_local_with(new, family, window, maxdepth):
    """Is there a subfamily of family+[new] containing `new` with union <= window
    and empty intersection? Exact via DFS (see module docstring)."""
    # candidates must intersect `new`'s window-neighborhood eventually; just DFS.
    edges = family
    n = len(edges)

    def dfs(start, union, inter, depth):
        if depth > maxdepth:
            return False
        for idx in range(start, n):
            E = edges[idx]
            u = union | E
            if popcount(u) > window:
                continue
            i = inter & E
            if i == 0:
                return True
            if dfs(idx + 1, u, i, depth + 1):
                return True
        return False

    return dfs(0, new, new, 1)

def full_local_check(family, window, maxdepth):
    """From-scratch exact L(r) check of a whole family (used for final audit)."""
    n = len(family)
    def dfs(start, union, inter, depth):
        if depth > maxdepth:
            return False
        for idx in range(start, n):
            E = family[idx]
            u = union | E
            if popcount(u) > window:
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

def tau_le_2(family, nverts):
    if not family:
        return 0
    allmask = (1 << nverts) - 1
    # tau <= 1?
    inter = allmask
    for E in family:
        inter &= E
    if inter:
        return 1
    for a in range(nverts):
        for b in range(a + 1, nverts):
            p = (1 << a) | (1 << b)
            if all(E & p for E in family):
                return 2
    return 3  # tau >= 3: counterexample!

def gadget_masks(r):
    X = list(range(4))
    edges = []
    v = 4
    Bs = []
    for i in range(4):
        Bs.append(list(range(v, v + r - 3)))
        v += r - 3
    for i in range(4):
        vs = [x for x in X if x != i] + Bs[i]
        edges.append(edge_mask(vs))
    return edges

def trial(r, n, pool_size, plant, rng):
    window = 3 * r - 3
    maxdepth = r + 1
    family = []
    if plant:
        family = gadget_masks(r)  # occupies vertices 0..4(r-2)-1 < n
    # candidate pool: random r-subsets
    pool = set()
    verts = list(range(n))
    while len(pool) < pool_size:
        pool.add(tuple(sorted(rng.sample(verts, r))))
    added = 0
    for cand in pool:
        cm = edge_mask(cand)
        if cm in family:
            continue
        if not violates_local_with(cm, family, window, maxdepth):
            family.append(cm)
            added += 1
    t = tau_le_2(family, n)
    return family, added, t

def main():
    rng = random.Random(616)
    results = {}
    CONFIGS = [
        # (r, n, pool_size, plant, trials)
        (6, 16, 4000, True, 8),
        (6, 18, 6000, True, 8),
        (6, 20, 8000, True, 6),
        (6, 24, 8000, True, 4),
        (6, 18, 6000, False, 6),
        (6, 22, 8000, False, 4),
        (7, 20, 6000, True, 5),
        (7, 24, 8000, True, 4),
        (7, 22, 6000, False, 3),
    ]
    worst = 0
    total = 0
    for (r, n, ps, plant, ntr) in CONFIGS:
        for t_i in range(ntr):
            fam, added, tau = trial(r, n, ps, plant, rng)
            total += 1
            worst = max(worst, tau)
            tag = "planted-gadget" if plant else "unplanted"
            print(f"r={r} n={n} {tag:15s} |family|={len(fam):4d} tau={tau}")
            if tau >= 3:
                print("*** COUNTEREXAMPLE CANDIDATE — auditing from scratch ***")
                ok = full_local_check(fam, 3*r-3, r+1)
                print(f"    from-scratch L({r}) check: {'PASSES (genuine counterexample!)' if ok else 'fails (search bug)'}")
                sys.exit(2)
            # audit a sample of families from scratch (defense against incremental-check bugs)
            if t_i == 0:
                assert full_local_check(fam, 3*r-3, r+1), "incremental and full L-check disagree"
    print(f"\n{total} trials; max tau observed = {worst} (theorems predict <= 2).")
    print("NO COUNTEREXAMPLE FOUND — consistent with t(6)=t(7)=2")

if __name__ == "__main__":
    main()
