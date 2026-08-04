#!/usr/bin/env python3
"""Targeted falsification for Theorem 2 (t(7)=2), Case B flavor: plant the rigid
m=5 minimal empty-intersection family for r=7 (5 distinguished vertices x_1..x_5,
each edge E_i = (X \\ {x_i}) u B_i with disjoint 3-sets B_i, span 20) and grow a
random greedy-maximal L(7)-family around it; verify tau <= 2 on every result.
A single tau >= 3 family would disprove Theorem 2. Shares the exact DFS local-
property checker logic of random_maximal_search.py (see docstring there for the
correctness argument)."""
import random, sys

def popcount(x): return bin(x).count("1")

def edge_mask(vs):
    m = 0
    for v in vs: m |= 1 << v
    return m

def violates_local_with(new, family, window, maxdepth):
    edges = family; n = len(edges)
    def dfs(start, union, inter, depth):
        if depth > maxdepth: return False
        for idx in range(start, n):
            E = edges[idx]
            u = union | E
            if popcount(u) > window: continue
            i = inter & E
            if i == 0: return True
            if dfs(idx + 1, u, i, depth + 1): return True
        return False
    return dfs(0, new, new, 1)

def full_local_check(family, window, maxdepth):
    n = len(family)
    def dfs(start, union, inter, depth):
        if depth > maxdepth: return False
        for idx in range(start, n):
            E = family[idx]
            u = union | E
            if popcount(u) > window: continue
            i = inter & E
            if i == 0: return True
            if dfs(idx + 1, u, i, depth + 1): return True
        return False
    return not any(dfs(s + 1, family[s], family[s], 1) for s in range(n))

def tau_le_2(family, nverts):
    if not family: return 0
    inter = (1 << nverts) - 1
    for E in family: inter &= E
    if inter: return 1
    for a in range(nverts):
        for b in range(a + 1, nverts):
            p = (1 << a) | (1 << b)
            if all(E & p for E in family): return 2
    return 3

def m5_meif_r7():
    """X = {0..4}; E_i = X\\{i} u B_i, B_i = 3-set; span 20."""
    edges = []
    v = 5
    for i in range(5):
        vs = [x for x in range(5) if x != i] + list(range(v, v + 3))
        v += 3
        edges.append(edge_mask(vs))
    return edges, v

def main():
    r, window, maxdepth = 7, 18, 8
    rng = random.Random(7616)
    base, span = m5_meif_r7()
    assert span == 20
    # sanity: base is L(7) (its own union is 20 > 18; proper subfamilies intersect)
    assert full_local_check(base, window, maxdepth), "planted m=5 MEIF violates L(7)?!"
    assert tau_le_2(base, span) == 2
    print("planted m=5 MEIF for r=7: L(7) OK, tau = 2")
    worst = 0
    for n, pool_size, trials in ((22, 6000, 5), (26, 8000, 4)):
        for _ in range(trials):
            family = list(base)
            pool = set()
            while len(pool) < pool_size:
                pool.add(tuple(sorted(rng.sample(range(n), r))))
            for cand in pool:
                cm = edge_mask(cand)
                if cm not in family and not violates_local_with(cm, family, window, maxdepth):
                    family.append(cm)
            t = tau_le_2(family, n)
            worst = max(worst, t)
            print(f"n={n} |family|={len(family):4d} tau={t}")
            if t >= 3:
                ok = full_local_check(family, window, maxdepth)
                print(f"*** tau>=3 candidate; from-scratch L(7): {ok}")
                sys.exit(2)
    print(f"max tau observed = {worst}; NO COUNTEREXAMPLE FOUND (m=5-planted r=7 search)")

if __name__ == "__main__":
    main()
