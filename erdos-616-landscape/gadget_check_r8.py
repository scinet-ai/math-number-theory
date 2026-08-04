#!/usr/bin/env python3
r"""Certify the lower-bound witnesses for t(8) >= 2 directly from definitions.

Three 8-uniform witnesses, all of the "rigid MEIF" shape
    E_i = (X \ {x_i}) u B_i,  i = 1..m,
with X = {x_1..x_m} distinguished vertices and B_i pairwise disjoint private
(r - m + 1)-sets:
    m = 4:  |B_i| = 5, span 4 + 20 = 24   (the gadget H_8 of proof_small_r.md)
    m = 5:  |B_i| = 4, span 5 + 20 = 25
    m = 6:  |B_i| = 3, span 6 + 18 = 24
Each has span > 3r-3 = 21, so the single empty-intersection subfamily (all m
edges) violates no window constraint.

Checks (no lemmas assumed):
 (1) L(8) via ALL subfamilies: every nonempty subfamily with |union| <= 21
     has a common vertex.  [Equivalent to the literal induced-subgraph
     definition by proof_small_r.md Lemma 1, itself elementary.]
 (2) L(8) LITERALLY for each witness: over every subset S of the witness's
     vertex set (bitmask sweep, 2^24 or 2^25 subsets), if |S| <= 21 then the
     edges contained in S have a common vertex.  Vertices outside the span
     can never matter (edges inside S depend only on S n span).
 (3) tau = 2 exactly: no single vertex covers all edges; an explicit pair does.

A planted-bug negative control (failure power): re-run check (2) on the m=4
witness with E_4 tampered -- 3 of its private vertices replaced by 3 private
vertices of E_1 -- which shrinks the 4-edge union to 24 - 3 = 21 <= window
while keeping the total intersection empty, i.e. creates a genuine 21-vertex
bad window.  The literal checker must FLAG this family, and does.
"""
from itertools import combinations

R = 8
WINDOW = 3 * R - 3  # 21

def rigid_witness(m, r=R):
    r"""E_i = (X \ {x_i}) u B_i with |B_i| = r - m + 1."""
    X = list(range(m))
    edges = []
    v = m
    for i in range(m):
        B = list(range(v, v + (r - m + 1)))
        v += r - m + 1
        edges.append(frozenset([x for x in X if x != i] + B))
    return edges, v  # v = span

def common(subfam):
    s = set(subfam[0])
    for E in subfam[1:]:
        s &= E
    return s

def check_subfamilies(edges, r=R, window=WINDOW):
    """Every nonempty subfamily with union <= window has a common vertex.
    Returns list of subfamily sizes that had empty intersection (must all
    have union > window)."""
    m = len(edges)
    for k in range(1, m + 1):
        for sub in combinations(edges, k):
            u = set().union(*sub)
            if len(u) <= window:
                assert common(list(sub)), \
                    f"subfamily of size {k} with union {len(u)} has no common vertex"
    return True

def check_literal_bitmask(edges, span, window=WINDOW, expect_ok=True):
    """Literal L(8) over all 2^span vertex subsets of the span."""
    masks = []
    for E in edges:
        me = 0
        for x in E:
            me |= 1 << x
        masks.append(me)
    n_checked = 0
    for S in range(1 << span):
        if S.bit_count() > window:
            continue
        inter = ~0
        found = False
        for me in masks:
            if me & ~S == 0:      # edge inside S
                inter &= me
                found = True
        if found:
            n_checked += 1
            if inter == 0:
                assert not expect_ok, \
                    f"literal L(8) FAILS on window of size {S.bit_count()}"
                return n_checked, False
    assert expect_ok, "planted-bug control: checker failed to flag bad family"
    return n_checked, True

def check_tau_exactly_2(edges):
    V = sorted(set().union(*edges))
    assert not any(all(v in E for E in edges) for v in V), "tau <= 1?!"
    pair = next(((a, b) for a, b in combinations(V, 2)
                 if all(a in E or b in E for E in edges)), None)
    assert pair is not None, "no covering pair: tau > 2?!"
    return pair

def planted_bug_family():
    """Tamper the m=4 witness so that a <= 21-vertex window becomes bad:
    replace 3 private vertices of E_4 by 3 private vertices of E_1.  The
    4-edge union then has 24 - 3 = 21 vertices and still empty intersection."""
    edges, span = rigid_witness(4)
    e = [set(E) for E in edges]
    b4 = sorted(e[3] - set(range(4)))[:3]      # 3 private vertices of E_4
    b1 = sorted(e[0] - set(range(4)))[:3]      # 3 private vertices of E_1
    e[3] = (e[3] - set(b4)) | set(b1)
    assert len(e[3]) == R
    fam = [frozenset(x) for x in e]
    assert not common(fam), "tampered family should still have empty intersection"
    assert len(set().union(*fam)) == 21
    return fam, span

def main():
    for m in (4, 5, 6):
        edges, span = rigid_witness(m)
        assert all(len(E) == R for E in edges)
        print(f"m={m}: rigid witness, span={span} (> {WINDOW}: {span > WINDOW})")
        check_subfamilies(edges)
        print(f"  L(8) via all {2**m - 1} subfamilies: OK")
        n, ok = check_literal_bitmask(edges, span)
        print(f"  L(8) literal (bitmask sweep of all 2^{span} subsets; "
              f"{n} subsets contained an edge): OK")
        pair = check_tau_exactly_2(edges)
        print(f"  tau = 2 exactly (no single vertex covers; pair {pair} covers): OK")
    fam, span = planted_bug_family()
    n, ok = check_literal_bitmask(fam, span, expect_ok=False)
    print(f"negative control: tampered m=4 family (21-vertex bad window) "
          f"correctly FLAGGED by the literal checker after {n} windows. OK")
    print("\nALL r=8 WITNESS CHECKS PASSED: t(8) >= 2 certified")

if __name__ == "__main__":
    main()
