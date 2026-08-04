#!/usr/bin/env python3
r"""Exhaustive classification of minimal empty-intersection families of m r-sets
whose span exceeds the local window 3r-3.

Background (see proofs/proof_t6_t7.md, Lemma 2):
A family E_1,...,E_m of r-sets is a *minimal empty-intersection family* (MEIF) if
  - the intersection of all m sets is empty, and
  - every proper subfamily has nonempty intersection.
Up to isomorphism such a family is determined by its Venn-region cardinalities:
for each nonempty T subseteq [m], c_T = #{vertices lying in exactly the edges E_i, i in T}.
The family axioms translate to:
  - uniformity:   sum_{T ni i} c_T = r for every i
  - empty inter:  c_[m] = 0
  - minimality:   c_{[m] minus {i}} >= 1 for every i   (a vertex in all edges but E_i)
    [minimality of the whole family is equivalent to this: the intersection of any
     (m-1)-subfamily omitting E_i must contain a vertex outside E_i, which is exactly
     a vertex of type [m]\{i}, since c_[m]=0]
  - span = sum_T c_T.

This script enumerates ALL solutions (c_T) with span >= 3r-2 ("survivors" of the
local property L(r)), materializes each as an explicit set family, re-verifies the
axioms directly on the sets, and prints the intersection structure that the proof
of t(6)=2 / t(7)=2 relies on. The only analytic ingredient is the trivial
double-counting identity span = m*r - sum_T (|T|-1) c_T, used as an EXACT pruning
bound in the enumeration (see enumerate_survivors); no claimed span bound or
structural lemma is assumed.
"""
import sys
from itertools import combinations, chain

def nonempty_proper_types(m, required_first=True):
    """All T with 2 <= |T| <= m-1, as frozensets; the m required types [m]\\{i}
    first (search order). Singletons handled implicitly (deficit 0)."""
    req = [frozenset(set(range(m)) - {i}) for i in range(m)]
    rest = []
    for k in range(m-1, 1, -1):
        for T in combinations(range(m), k):
            fT = frozenset(T)
            if fT not in req:
                rest.append(fT)
    return req + rest

def enumerate_survivors(r, m, span_min):
    """Enumerate all c-vectors (on non-singleton types; singleton counts are then
    forced by uniformity) satisfying the MEIF axioms with span >= span_min.

    Exact pruning via the double-counting identity (no lemma assumed):
        sum_i deg_i = sum_T |T| c_T = m*r   and   span = sum_T c_T,
    hence span = m*r - D with D = sum_T (|T|-1) c_T (singletons contribute 0).
    So span >= span_min  <=>  D <= budget := m*r - span_min.
    Each of the m required minimality types [m]\\{i} contributes deficit m-2 per
    vertex, so unplaced required types add >= m-2 each to D.
    Returns list of dicts {T: c_T} including singleton counts."""
    budget = m*r - span_min
    if budget < 0:
        return []
    types = nonempty_proper_types(m)
    n_req = m  # first m entries of `types` are the required types
    solutions = []
    deg = [0]*m  # degree from non-singleton types so far

    def rec(idx, counts, D):
        # remaining required types not yet placed:
        req_left = max(0, n_req - idx)
        if D + req_left * (m-2) > budget:
            return
        if idx == len(types):
            sol = dict(counts)
            for i in range(m):
                s = r - deg[i]
                if s < 0:
                    return
                if s > 0:
                    sol[frozenset({i})] = s
            span = sum(sol.values())
            assert span == m*r - D  # identity self-check
            if span >= span_min:
                solutions.append(sol)
            return
        T = types[idx]
        w = len(T) - 1
        cap = min((r - deg[i]) for i in T)
        cap = min(cap, (budget - D) // w)
        lo = 1 if idx < n_req else 0
        for c in range(cap, lo - 1, -1):
            for i in T:
                deg[i] += c
            if c > 0:
                counts[T] = c
            rec(idx + 1, counts, D + w * c)
            if c > 0:
                del counts[T]
            for i in T:
                deg[i] -= c
    rec(0, {}, 0)
    return solutions

def materialize(sol, m):
    r"""Build explicit edges as sets of vertex ids; return (edges, xs) where
    xs[i] is the distinguished vertex of type [m]\{i} (first one)."""
    edges = [set() for _ in range(m)]
    xs = {}
    v = 0
    for T, c in sorted(sol.items(), key=lambda kv: (-len(kv[0]), sorted(kv[0]))):
        for _ in range(c):
            for i in T:
                edges[i].add(v)
            if len(T) == m-1:
                i_missing = (set(range(m)) - T).pop()
                if i_missing not in xs:
                    xs[i_missing] = v
            v += 1
    return edges, xs, v

def verify_family(edges, r, m):
    """Direct verification of MEIF axioms on explicit sets."""
    assert all(len(E) == r for E in edges), "not r-uniform"
    inter_all = set.intersection(*edges)
    assert not inter_all, "intersection of all edges nonempty"
    for i in range(m):
        sub = [edges[j] for j in range(m) if j != i]
        if len(sub) >= 1:
            assert set.intersection(*sub), f"(m-1)-subfamily omitting {i} has empty intersection"
    return True

def main():
    overall_ok = True
    for r in (6, 7):
        window = 3*r - 3
        print(f"\n=== r = {r}, local window = {window} ===")
        for m in range(2, r+3):
            sols = enumerate_survivors(r, m, span_min=window+1)
            print(f" m={m}: {len(sols)} surviving MEIF type-vectors (span > {window})")
            for sol in sols:
                edges, xs, n = materialize(sol, m)
                verify_family(edges, r, m)
                span = len(set(chain.from_iterable(edges)))
                assert span == sum(sol.values())
                pretty = sorted(((tuple(sorted(T)), c) for T, c in sol.items()),
                                key=lambda kv: (-len(kv[0]), kv[0]))
                print(f"   span={span}  c = {pretty}")
                # intersection structure used by the theorems:
                pair_ints = {(k, l): edges[k] & edges[l] for k, l in combinations(range(m), 2)}
                min_pair = min(len(s) for s in pair_ints.values())
                print(f"   pairwise |E_k∩E_l| sizes: {sorted(len(s) for s in pair_ints.values())}")
                if r == 6:
                    # Theorem 1 needs: every pairwise intersection has size exactly 2
                    # and equals a pair of distinguished vertices.
                    for (k, l), s in pair_ints.items():
                        assert len(s) == 2, f"r=6 rigid gadget: |E_{k}∩E_{l}|={len(s)}!=2"
                        assert s == {xs[i] for i in range(m) if i not in (k, l)}, \
                            "pair intersection is not the complementary x-pair"
                    print("   [r=6 CHECK] every E_k∩E_l = complementary x-pair (size 2): OK")
                if r == 7 and m == 4:
                    # Theorem 2 Case A needs: SOME pair with intersection of size exactly 2
                    # consisting of x-vertices.
                    good = [(k, l) for (k, l), s in pair_ints.items()
                            if len(s) == 2 and s <= set(xs.values())]
                    assert good, "r=7 m=4 survivor with no size-2 x-pair intersection"
                    print(f"   [r=7 m=4 CHECK] pairs with E_k∩E_l = x-pair of size 2: {good}")
                if r == 7 and m == 5:
                    # Theorem 2 Case B needs: every triple intersection = the complementary
                    # x-pair (size exactly 2).
                    for a, b, c in combinations(range(5), 3):
                        s = edges[a] & edges[b] & edges[c]
                        expect = {xs[i] for i in range(5) if i not in (a, b, c)}
                        assert s == expect, \
                            f"r=7 m=5: E_{a}∩E_{b}∩E_{c} = {s} != complementary x-pair {expect}"
                    print("   [r=7 m=5 CHECK] every triple intersection = complementary x-pair: OK")
        # summary assertions the theorems rely on
        if r == 6:
            for m in range(2, r+3):
                sols = enumerate_survivors(r, m, span_min=window+1)
                if m != 4:
                    assert not sols, f"unexpected survivor at r=6 m={m}"
                else:
                    assert len(sols) == 1, "r=6 m=4 should have exactly one survivor (the rigid gadget)"
            print(" [SUMMARY r=6] unique survivor: m=4 rigid 16-vertex gadget. OK")
        if r == 7:
            for m in range(2, r+3):
                sols = enumerate_survivors(r, m, span_min=window+1)
                if m not in (4, 5):
                    assert not sols, f"unexpected survivor at r=7 m={m}"
            print(" [SUMMARY r=7] survivors only at m=4 and m=5. OK")
    print("\nALL CLASSIFICATION CHECKS PASSED")

if __name__ == "__main__":
    main()
