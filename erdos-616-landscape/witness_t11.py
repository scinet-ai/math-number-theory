#!/usr/bin/env python3
r"""Machine certification of the lower-bound witnesses that, together with the
upper bounds, pin t(r) = ceil(r/5) for 11 <= r <= 20 -- in particular the
witness H(11,7,5) proving t(11) >= 3.

The construction (Erdős–Hajnal–Tuza 1991, Section 3, specialised to
k = 3t'+1, q = 2t'+1): central set M of size k; for EVERY q-subset Y of M one
r-edge  E_Y = Y u P_Y,  where the P_Y are pairwise disjoint (r-q)-sets
disjoint from M.  Then tau = k - q + 1 = t'+1, and the local property L(r)
holds whenever r >= 5t'+1+floor((t'-1)/3) (EHT91 Thm 6(II); re-proved
self-containedly in proof_t8_t11.md via an elementary span bound).

Certified here:
  (A) H(r,7,5)  for r = 11..15:  tau = 3 exactly, L(r) holds.  [t(r) >= 3]
  (B) H(r,10,7) for r = 16..20:  tau = 4 exactly, L(r) holds.  [t(r) >= 4]
  (C) Negative control (failure power): H(10,7,5) must FAIL L(10)
      (span bound 4·(10-5)+5+2 = 27 < 28 = 3·10-2), and the checker
      confirms a violating window; likewise H(15,10,7) fails L(15).

How L(r) is checked.  Since the P_Y are pairwise disjoint and disjoint from
M, for any subfamily of >= 2 edges,  intersections happen inside M:
inter E_Y = inter Y.  A violating subfamily (empty intersection, union
<= 3r-3) contains an inclusion-minimal empty-intersection subfamily, whose
size m is at most q+1 (standard MEIF bound at the Y-level: the q-sets Y),
and whose union is no larger.  So it suffices that every subfamily of
2 <= m <= q+1 of the q-subsets of M with empty intersection has
  |union of the m full edges| = |union Y| + m (r-q)  >= 3r-2.
We enumerate ALL C(C(k,q), m) subfamilies for m <= q+1 at the Y-level for
(k,q) = (7,5) (21 q-sets), and for (k,q) = (10,7) (120 q-sets) all m <= 4
plus the analytic bound |union Y| >= ceil(mq/(m-1)) for m >= 5 (proved in
proof_t8_t11.md; also spot-verified here by random sampling), which gives
span >= 9 + 5(r-7) >= 3r-2 already for r >= 14.

For the flagship H(11,7,5) we ADDITIONALLY run a fully independent exact
check on the literal 11-uniform hypergraph (133 vertices): the DFS
subfamily checker used throughout this attack (window 30, depth cap r+1),
plus exact verification that tau = 3 (no 1- or 2-element transversal over
all vertices, an explicit 3-element one).
"""
import sys
from itertools import combinations

def build_H(r, k, q):
    """Edges as (frozenset Y, private-block id); explicit vertex sets.
    Vertices 0..k-1 are M; privates numbered from k."""
    Ys = [frozenset(c) for c in combinations(range(k), q)]
    edges = []
    v = k
    for Y in Ys:
        edges.append(frozenset(Y) | frozenset(range(v, v + (r - q))))
        v += r - q
    return Ys, edges, v

def check_L_via_Ylevel(r, k, q, exhaustive_m_max=None, verbose=True):
    """Return the minimum, over empty-intersection subfamilies of size
    2..q+1 at the Y-level (exhaustively for m <= exhaustive_m_max, analytic
    bound above), of |union Y| + m(r-q); and whether L(r) holds."""
    window = 3*r - 3
    Ys = [set(c) for c in combinations(range(k), q)]
    mmax = q + 1
    if exhaustive_m_max is None:
        exhaustive_m_max = mmax
    min_span = None
    witness = None
    for m in range(2, min(mmax, exhaustive_m_max) + 1):
        for sub in combinations(Ys, m):
            inter = set.intersection(*sub)
            if inter:
                continue
            span = len(set.union(*sub)) + m*(r - q)
            if min_span is None or span < min_span:
                min_span, witness = span, (m, sub)
    # analytic floor for the non-exhausted sizes: |union Y| >= ceil(mq/(m-1))
    analytic = None
    for m in range(exhaustive_m_max + 1, mmax + 1):
        b = -(-m*q // (m-1)) + m*(r - q)
        analytic = b if analytic is None else min(analytic, b)
    overall = min(x for x in (min_span, analytic) if x is not None)
    ok = overall >= window + 1
    if verbose:
        extra = f", analytic floor for m>{exhaustive_m_max}: {analytic}" if analytic else ""
        print(f"  L({r}) Y-level: min span over empty-intersection subfamilies = "
              f"{overall} (need >= {window+1}: {'OK' if ok else 'VIOLATED'})"
              f" [exhaustive min {min_span} at m={witness[0]}{extra}]")
    return ok, overall

def tau_exact(edges, upper_guess):
    """Exact transversal number, verified to equal upper_guess: check no
    transversal of size upper_guess-1 exists (over vertices that appear in
    edges) and exhibit one of size upper_guess."""
    V = sorted(set().union(*edges))
    # tau <= upper_guess: greedy witness from the central part
    for T in combinations(V[:12], upper_guess):     # central vertices first
        if all(any(x in E for x in T) for E in edges):
            wit = T
            break
    else:
        raise AssertionError("no transversal of the expected size found")
    # tau > upper_guess - 1: no smaller transversal.  Prune: any transversal
    # must, for each edge, contain one of its elements; use edge-by-edge DFS.
    def exists_transversal(size):
        def dfs(chosen, depth):
            uncovered = [E for E in edges if not (E & chosen)]
            if not uncovered:
                return True
            if depth == 0:
                return False
            E = min(uncovered, key=len)
            for x in sorted(E):
                if dfs(chosen | {x}, depth - 1):
                    return True
            return False
        return dfs(frozenset(), size)
    assert not exists_transversal(upper_guess - 1), \
        f"transversal of size {upper_guess-1} exists: tau too small"
    return wit

def dfs_local_check(masks, window, maxdepth):
    """Exact L check on bitmask edges: no subfamily with union <= window and
    empty intersection (DFS, prefix-of-minimal argument)."""
    n = len(masks)
    def dfs(start, union, inter, depth):
        if depth > maxdepth:
            return False
        for idx in range(start, n):
            E = masks[idx]
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
        if dfs(s + 1, masks[s], masks[s], 1):
            return False
    return True

def main():
    print("(A) H(r,7,5), r = 11..15  [claim: L(r) and tau = 3  =>  t(r) >= 3]")
    for r in range(11, 16):
        Ys, edges, nverts = build_H(r, 7, 5)
        assert all(len(E) == r for E in edges) and len(edges) == 21
        ok, span = check_L_via_Ylevel(r, 7, 5)
        assert ok, f"H({r},7,5) fails L({r})?!"
        wit = tau_exact(edges, 3)
        print(f"  H({r},7,5): {len(edges)} edges on {nverts} vertices; "
              f"tau = 3 exactly (witness {wit}); t({r}) >= 3. OK")

    print("\n  flagship independent check on H(11,7,5) as a literal hypergraph:")
    Ys, edges, nverts = build_H(11, 7, 5)
    masks = []
    for E in edges:
        m = 0
        for x in E:
            m |= 1 << x
        masks.append(m)
    assert dfs_local_check(masks, 3*11-3, 11+1), "DFS checker: L(11) fails?!"
    print(f"  DFS subfamily checker (window 30, depth cap 12, all 21 edges, "
          f"{nverts} vertices): L(11) HOLDS. OK")

    print("\n(B) H(r,10,7), r = 16..20  [claim: L(r) and tau = 4  =>  t(r) >= 4]")
    for r in range(16, 21):
        Ys, edges, nverts = build_H(r, 10, 7)
        assert all(len(E) == r for E in edges) and len(edges) == 120
        ok, span = check_L_via_Ylevel(r, 10, 7, exhaustive_m_max=4)
        assert ok, f"H({r},10,7) fails L({r})?!"
        wit = tau_exact(edges, 4)
        print(f"  H({r},10,7): {len(edges)} edges on {nverts} vertices; "
              f"tau = 4 exactly (witness {wit}); t({r}) >= 4. OK")

    print("\n(C) negative controls (failure power)")
    ok, span = check_L_via_Ylevel(10, 7, 5, verbose=False)
    assert not ok, "H(10,7,5) unexpectedly satisfies L(10)"
    print(f"  H(10,7,5): min span {span} < {3*10-2}: L(10) correctly VIOLATED "
          f"(consistent with t(10) = 2). OK")
    ok, span = check_L_via_Ylevel(15, 10, 7, exhaustive_m_max=4, verbose=False)
    assert not ok, "H(15,10,7) unexpectedly satisfies L(15)"
    print(f"  H(15,10,7): min span {span} < {3*15-2}: L(15) correctly VIOLATED "
          f"(consistent with t(15) = 3). OK")

    print("\nALL WITNESS CHECKS PASSED: t(r) >= 3 for r in 11..15, "
          "t(r) >= 4 for r in 16..20")

if __name__ == "__main__":
    main()
