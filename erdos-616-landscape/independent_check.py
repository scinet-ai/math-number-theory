#!/usr/bin/env python3
r"""INDEPENDENT verification of the Fatness Lemma via its covering reduction,
plus an independent re-derivation of the r = 8 survivor landscape.

This file shares NO code with classify_fatness.py (different formulation,
different algorithms); agreement between the two is the double-check required
for the nonexistence claim "no 3-fat survivor MEIF at r = 8, 9, 10".

------------------------------------------------------------------------------
PART 1 -- covering exhaustion.

Setting (see proof_t8_t11.md, Lemma F): let F = {E_1..E_m} be a MEIF of r-sets
with span >= 3r-2, written by Venn-region counts c_T.  Put
    e_i  = c_{[m]\{i}} - 1  >= 0   (extra copies of the required types),
    f_ij = c_{[m]\{i,j}}    >= 0.
Then for each pair {i,j}:
    |inter_{k != i,j} E_k| = 2 + e_i + e_j + f_ij,
and the span constraint forces the BUDGET INEQUALITY
    (m-2) * sum_i e_i + (m-3) * sum_{i<j} f_ij  <=  B(m,r) := (m-3)(r-1-m) - 1.
(Proof: D = sum_T (|T|-1) c_T = m*r - span <= m*r - (3r-2), and D is at least
the contribution of the required and pair-complement types alone, which is
(m-2)(m + sum e_i) + (m-3) sum f_ij; subtract m(m-2).)

"3-fat" (every (m-2)-wise intersection >= 3) is then EXACTLY the condition
    e_i + e_j + f_ij >= 1 for every pair {i,j} of [m],
i.e. {i : e_i >= 1} together with {pairs with f_ij >= 1} covers the edge set
of the complete graph K_m.  Since only 0/1 values matter for covering and
capping at 1 never increases the cost, 3-fatness within budget is possible
iff some BINARY (e, f) covers K_m at cost <= B(m, r).

This part exhaustively enumerates all binary (e, f) with cost <= B(m, r) --
directly, by choosing the star set A = {i : e_i = 1} and the f-support -- and
checks the covering condition.  Claim verified: NO cover exists for any
m in {4,...,r-2} when r in {6,...,10}; covers DO exist at r = 11 (m = 4)
[failure-power control], matching the analytic minimum cover cost
    mincost(m) = min_a [ a(m-2) + C(m-a,2)(m-3) ]
which is also printed and compared with B(m, r).

------------------------------------------------------------------------------
PART 2 -- independent enumeration of the r = 8 survivors.

A from-scratch enumeration of all labeled survivor type-vectors at r = 8
(span >= 22), written as a worklist algorithm over explicit per-type
multiplicity vectors (not the DFS-with-shared-state of classify_fatness.py),
recomputing uniformity, minimality, span and the (m-2)-wise intersections
directly from each completed vector.  Must reproduce the landscape recorded
in ../proofs/proof_t6_t7.md -- 32 / 401 / 156 survivors at m = 4 / 5 / 6 --
and find zero 3-fat vectors.
"""
import sys
from itertools import combinations

# ----------------------------------------------------------------------------
# PART 1: covering exhaustion
# ----------------------------------------------------------------------------

def mincost(m):
    """min over a of [ a(m-2) + C(m-a,2)(m-3) ]  (analytic minimum cover cost)."""
    best = None
    for a in range(m+1):
        rest = m - a
        cost = a*(m-2) + (rest*(rest-1)//2)*(m-3)
        best = cost if best is None else min(best, cost)
    return best

def covering_possible(m, B):
    """Exhaustively test whether some binary (e, f) with
    (m-2)|A| + (m-3)|F| <= B covers K_m.  Returns a witness or None."""
    verts = range(m)
    all_pairs = list(combinations(verts, 2))
    max_a = B // (m-2)
    for a in range(max_a + 1):
        for A in combinations(verts, a):
            Aset = set(A)
            uncovered = [p for p in all_pairs if p[0] not in Aset and p[1] not in Aset]
            rem = B - a*(m-2)
            max_f = rem // (m-3)
            # a cover must include every uncovered pair in the f-support:
            if len(uncovered) <= max_f:
                return (sorted(Aset), uncovered)
            # (any f-support smaller than `uncovered` misses a pair; supersets
            #  only cost more -- so this A admits no cover within budget)
    return None

def part1():
    print("PART 1: covering exhaustion (no 3-fat MEIF budget-feasible, r<=10)")
    print(f" {'r':>2} {'m':>2} {'B(m,r)':>7} {'mincost':>8}  verdict")
    ok = True
    for r in range(6, 11):
        for m in range(4, r-1):
            B = (m-3)*(r-1-m) - 1
            mc = mincost(m)
            wit = covering_possible(m, B)
            verdict = "COVER EXISTS (3-fat feasible)" if wit else "no cover"
            print(f" {r:>2} {m:>2} {B:>7} {mc:>8}  {verdict}")
            assert (wit is None) == (mc > B), "exhaustion disagrees with mincost"
            if wit is not None:
                ok = False
    assert ok, "a 3-fat allocation is budget-feasible at some r <= 10!"
    # failure-power control: r = 11, m = 4
    r, m = 11, 4
    B = (m-3)*(r-1-m) - 1
    wit = covering_possible(m, B)
    assert wit is not None and mincost(m) == B == 5
    print(f" control r=11 m=4: B = {B} = mincost = {mincost(m)}; cover exists: "
          f"stars at {wit[0]}, f-pairs {wit[1]}  -> detector CAN fire")
    print(" PART 1 PASSED: no covering within budget for any m, 6 <= r <= 10\n")

# ----------------------------------------------------------------------------
# PART 2: independent survivor enumeration at r = 8
# ----------------------------------------------------------------------------

def all_nonsingleton_types(m):
    """All subsets of [m] with 2 <= |T| <= m-1, as sorted tuples, in a fixed
    deterministic order: by size DESCENDING, then lexicographic.  The size
    descending order puts the m required types [m]\\{i} (= ALL types of size
    m-1) first, so the minimality constraint c >= 1 -- part of the MEIF
    definition -- consumes its deficit before the cheap small types are
    considered.  (Ordering affects speed only, not the enumerated set.)"""
    out = []
    for k in range(m-1, 1, -1):
        out.extend(combinations(range(m), k))
    return out

def enumerate_r8_survivors(m, r=8):
    """Worklist enumeration of all labeled c-vectors for MEIFs of m r-sets
    with span >= 3r-2.  States are explicit immutable tuples
    (position, multiplicity-vector-so-far, deficit-so-far, degree-vector);
    no shared mutable state.  The only constraints applied during the search
    are parts of the MEIF/survivor *definition*:
      - minimality: c_{[m]\\{i}} >= 1 (lower bound 1 on the size-(m-1) types),
      - deficit D = sum (|T|-1) c_T must satisfy D <= m*r - (3r-2)
        [span identity span = m*r - D, by double counting; span is also
         recomputed from scratch on every completed vector],
      - degree sum_{T ni i} c_T <= r for every i (uniformity feasibility).
    Returns the list of completed vectors as dicts {type-tuple: count}
    WITH singleton counts filled in by uniformity."""
    span_min = 3*r - 2
    Dmax = m*r - span_min
    types = all_nonsingleton_types(m)
    n_req = m  # the first m types (all of size m-1) are exactly the required ones
    work = [(0, (), 0, (0,)*m)]     # (pos, mults, D, degrees)
    complete = []
    while work:
        pos, mults, D, degs = work.pop()
        if pos == len(types):
            vec = {}
            for T, c in zip(types, mults):
                if c > 0:
                    vec[T] = c
            singles = [r - d for d in degs]
            assert min(singles) >= 0
            for i in range(m):
                if singles[i] > 0:
                    vec[(i,)] = singles[i]
            span = sum(vec.values())   # recomputed from scratch
            if span >= span_min:
                complete.append(vec)
            continue
        T = types[pos]
        w = len(T) - 1
        capD = (Dmax - D) // w
        capdeg = min(r - degs[i] for i in T)
        lo = 1 if pos < n_req else 0
        for c in range(lo, min(capD, capdeg) + 1):
            nd = list(degs)
            for i in T:
                nd[i] += c
            work.append((pos + 1, mults + (c,), D + w*c, tuple(nd)))
    return complete

def check_vector_r8(vec, m, r=8):
    """Recompute everything about a completed vector from first principles."""
    # uniformity
    for i in range(m):
        assert sum(c for T, c in vec.items() if i in T) == r, "uniformity fails"
    # empty intersection: no type = [m] present (by construction types < [m])
    assert tuple(range(m)) not in vec
    # minimality: each [m]\{i} present
    for i in range(m):
        T = tuple(sorted(set(range(m)) - {i}))
        assert vec.get(T, 0) >= 1, "minimality fails"
    span = sum(vec.values())
    assert span >= 3*r - 2, "span below survivor threshold"
    # (m-2)-wise intersections
    sizes = []
    for i, j in combinations(range(m), 2):
        A = set(range(m)) - {i, j}
        s = sum(c for T, c in vec.items() if A <= set(T))
        sizes.append(s)
    return span, min(sizes), max(sizes)

def part2():
    print("PART 2: independent r=8 survivor enumeration (worklist algorithm)")
    expected = {4: 32, 5: 401, 6: 156}
    total = 0
    for m in range(4, 7):
        vecs = enumerate_r8_survivors(m)
        n_fat = 0
        span_lo = span_hi = None
        for vec in vecs:
            span, mn, mx = check_vector_r8(vec, m)
            span_lo = span if span_lo is None else min(span_lo, span)
            span_hi = span if span_hi is None else max(span_hi, span)
            assert mn >= 2
            if mn >= 3:
                n_fat += 1
        print(f" m={m}: {len(vecs)} survivors (spans {span_lo}..{span_hi}), "
              f"3-fat: {n_fat}")
        assert len(vecs) == expected[m], \
            f"m={m}: got {len(vecs)}, recorded landscape says {expected[m]}"
        assert n_fat == 0
        total += len(vecs)
    # no survivors for m outside 4..6 (independent confirmation of Lemma 3(4))
    for m in (2, 3, 7, 8, 9):
        vecs = enumerate_r8_survivors(m)
        assert not vecs, f"unexpected survivors at m={m}"
    print(f" m in {{2,3,7,8,9}}: 0 survivors (matches Lemma 3(4))")
    print(f" total: {total} survivors at r=8 (recorded landscape: 589); "
          f"0 are 3-fat")
    assert total == 589
    print(" PART 2 PASSED: independent enumeration reproduces 32/401/156, "
          "no 3-fat survivor\n")

def main():
    part1()
    part2()
    print("INDEPENDENT CHECKS PASSED")

if __name__ == "__main__":
    main()
