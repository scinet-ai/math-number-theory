#!/usr/bin/env python3
r"""Verification certificates for the small-r theorem pack on Erdős problem #616.

Problem (erdosproblems.com/616, statement due to Erdős [Er99]):
  Let r >= 3. For an r-uniform hypergraph G let tau(G) be the transversal
  (covering) number. Determine the best possible t = t(r) such that if every
  subgraph G' of G on at most 3r-3 vertices has tau(G') <= 1, then tau(G) <= t(r).

We write L(r) for the local condition "every induced subgraph on at most 3r-3
vertices has transversal number <= 1".

This script verifies, by brute force / direct enumeration:

  [A] Arithmetic core of the upper-bound proof: for m in [2, r+1],
      M(r) := max_m m(r-m+2) satisfies M(r) = 3r-3 for r = 3,4,5 and
      M(r) > 3r-3 for r >= 6 (witnessed at m = 4 for r = 6: 16 > 15).

  [B] The 4-edge gadget H_r (r >= 6):
        vertices: a_1..a_4 and pairwise disjoint (r-3)-sets B_1..B_4,
        edges:    E_i = ({a_1..a_4} \ {a_i}) ∪ B_i.
      Checks for r = 6..40: r-uniformity, span 4r-8, tau(H_r) = 2 exactly
      (exhaustive over all 1-subsets and one explicit 2-cover), and L(r) via
      the subfamily criterion (every nonempty subfamily F of edges with
      |union F| <= 3r-3 has a common vertex).  The subfamily criterion is
      equivalent to L(r); see Lemma 1 in proof_small_r.md.

  [C] Direct-definition check of L(r) for the gadget at r = 6 and r = 7:
      enumerate ALL vertex subsets S (2^16 resp. 2^20) and verify that every
      S with |S| <= 3r-3 induces a hypergraph with a common vertex (tau <= 1).
      This uses no reduction at all -- it is the raw definition.

  [D] Failure-power control: the same gadget at r = 5 must VIOLATE L(5)
      (its span 4r-8 = 12 fits inside a 3r-3 = 12 window).  Both the
      subfamily criterion and the direct check must detect this.  If they
      don't, the harness is broken and the run fails.

  [E] Pendant extension (monotonicity lemma, Lemma 5): from the r=6 gadget
      build the 7-uniform P(H_6) by adding a distinct new pendant vertex to
      each edge.  Verify L(7) by DIRECT enumeration over all 2^20 subsets,
      and tau(P(H_6)) = 2.  Also verify the subfamily criterion for iterated
      pendant extensions up to r = 12.

Exit code 0 iff every check passes.  No external dependencies.
"""
import itertools
import sys

FAIL = []


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" -- {detail}" if detail else ""))
    if not ok:
        FAIL.append(name)


# ----------------------------------------------------------------------------
# generic helpers: hypergraph = list of frozensets of vertex ids
# ----------------------------------------------------------------------------

def tau_exact(edges, vertices):
    """Exact transversal number by exhaustive search over subset sizes."""
    edges = [set(e) for e in edges]
    if not edges:
        return 0
    verts = sorted(vertices)
    for k in range(1, len(edges) + 1):
        for T in itertools.combinations(verts, k):
            Ts = set(T)
            if all(e & Ts for e in edges):
                return k
    return len(edges)


def subfamily_criterion_violations(edges, window):
    """Return list of edge-subfamilies F (as index tuples) with
    |union F| <= window and empty common intersection.
    By Lemma 1 (proof_small_r.md) this list is empty iff L(r) holds."""
    bad = []
    m = len(edges)
    for k in range(1, m + 1):
        for idxs in itertools.combinations(range(m), k):
            fam = [edges[i] for i in idxs]
            uni = set().union(*fam)
            if len(uni) <= window:
                inter = set(fam[0])
                for e in fam[1:]:
                    inter &= e
                if not inter:
                    bad.append(idxs)
    return bad


def direct_window_violations(edges, vertices, window, max_report=3):
    """Raw definition of L(r): enumerate ALL subsets S of the vertex set with
    |S| <= window; the edges contained in S must have a common vertex.
    Bitmask implementation; feasible for |V| <= ~20. Returns violating S's."""
    verts = sorted(vertices)
    n = len(verts)
    pos = {v: i for i, v in enumerate(verts)}
    emasks = [sum(1 << pos[v] for v in e) for e in edges]
    full = (1 << n) - 1
    bad = []
    for S in range(1 << n):
        if S.bit_count() > window:
            continue
        inter = full
        found = False
        for em in emasks:
            if em & S == em:  # edge contained in S
                found = True
                inter &= em
        if found and inter == 0:
            bad.append(S)
            if len(bad) >= max_report:
                break
    return bad


# ----------------------------------------------------------------------------
# the gadget
# ----------------------------------------------------------------------------

def gadget(r):
    """4-edge gadget: vertices 0..3 are a_1..a_4; B_i = block i of size r-3.
    E_i = {a_j : j != i} ∪ B_i."""
    assert r >= 4
    a = list(range(4))
    edges = []
    nxt = 4
    for i in range(4):
        B = list(range(nxt, nxt + (r - 3)))
        nxt += r - 3
        edges.append(frozenset([a[j] for j in range(4) if j != i] + B))
    verts = set(range(nxt))
    return edges, verts


def pendant(edges, vertices):
    """Add one fresh pendant vertex to each edge (Lemma 5 construction)."""
    nxt = max(vertices) + 1
    new_edges = []
    new_verts = set(vertices)
    for e in edges:
        new_edges.append(frozenset(e | {nxt}))
        new_verts.add(nxt)
        nxt += 1
    return new_edges, new_verts


# ----------------------------------------------------------------------------
# [A] arithmetic core
# ----------------------------------------------------------------------------

def main():
    print("== [A] max span of a minimal empty-intersection family: max_m m(r-m+2)")
    for r in range(3, 13):
        M, argm = max((m * (r - m + 2), m) for m in range(2, r + 2))
        if r <= 5:
            check(f"A: r={r}: M(r)={M} == 3r-3={3*r-3}", M == 3 * r - 3,
                  f"attained at m={argm}")
        else:
            check(f"A: r={r}: M(r)={M} > 3r-3={3*r-3}", M > 3 * r - 3,
                  f"attained at m={argm}")
    check("A: r=6 window escape exactly at m=4: 4*(6-4+2)=16 > 15",
          4 * (6 - 4 + 2) == 16 and 16 > 15)

    # ----------------------------------------------------------------------------
    # [B] gadget, subfamily criterion, tau -- r = 6..40
    # ----------------------------------------------------------------------------

    print("== [B] gadget H_r for r = 6..40")
    for r in range(6, 41):
        edges, verts = gadget(r)
        ok_unif = all(len(e) == r for e in edges)
        ok_span = len(set().union(*edges)) == 4 * r - 8
        bad = subfamily_criterion_violations(edges, 3 * r - 3)
        # tau = 2: no single vertex covers, explicit pair does, intersection of all empty
        no1 = all(any(v not in e for e in edges) for v in verts)
        pair = {0, 1}  # a_1 covers E_2,E_3,E_4 ; a_2 covers E_1
        ok2 = all(e & pair for e in edges)
        ok = ok_unif and ok_span and not bad and no1 and ok2
        if r <= 8 or r == 40:
            check(f"B: r={r}: uniform/span/L(r)-subfam/tau=2", ok,
                  f"span={len(set().union(*edges))}, violations={bad}")
        elif not ok:
            check(f"B: r={r}", False, f"violations={bad}")
    print(f"      (r=9..39 all checked; failures would have printed)")

    # exact tau by exhaustive search for small r
    for r in (6, 7):
        edges, verts = gadget(r)
        t = tau_exact(edges, verts)
        check(f"B: r={r}: tau_exact(H_r) == 2 (exhaustive)", t == 2, f"tau={t}")

    # ----------------------------------------------------------------------------
    # [C] direct-definition check of L(r), r = 6, 7
    # ----------------------------------------------------------------------------

    print("== [C] direct window enumeration (raw definition of L(r))")
    for r in (6, 7):
        edges, verts = gadget(r)
        bad = direct_window_violations(edges, verts, 3 * r - 3)
        check(f"C: r={r}: all 2^{len(verts)} subsets, no bad window of size <= {3*r-3}",
              not bad, f"bad={bad}")

    # ----------------------------------------------------------------------------
    # [D] failure-power control: gadget at r=5 must FAIL L(5)
    # ----------------------------------------------------------------------------

    print("== [D] negative control (checker must be able to fail)")
    edges5, verts5 = gadget(5)
    bad_sub = subfamily_criterion_violations(edges5, 3 * 5 - 3)
    bad_dir = direct_window_violations(edges5, verts5, 3 * 5 - 3)
    check("D: r=5 gadget violates L(5) per subfamily criterion",
          bool(bad_sub), f"violating subfamilies: {bad_sub}")
    check("D: r=5 gadget violates L(5) per direct enumeration",
          bool(bad_dir), f"{len(bad_dir)}+ bad windows found")
    check("D: the r=5 violation is the full 4-edge family spanning 12 <= 12",
          (0, 1, 2, 3) in bad_sub)

    # ----------------------------------------------------------------------------
    # [E] pendant extension (monotonicity)
    # ----------------------------------------------------------------------------

    print("== [E] pendant extension of the r=6 gadget")
    e6, v6 = gadget(6)
    e7, v7 = pendant(e6, v6)
    check("E: pendant(H_6) is 7-uniform on 20 vertices",
          all(len(e) == 7 for e in e7) and len(v7) == 20)
    bad = direct_window_violations(e7, v7, 3 * 7 - 3)
    check("E: pendant(H_6) satisfies L(7), direct enumeration over 2^20 subsets",
          not bad, f"bad={bad}")
    t = tau_exact(e7, v7)
    check("E: tau(pendant(H_6)) == 2 (exhaustive)", t == 2, f"tau={t}")

    # iterate pendant extension up to r = 12, subfamily criterion
    edges, verts = gadget(6)
    for r in range(7, 13):
        edges, verts = pendant(edges, verts)
        ok_unif = all(len(e) == r for e in edges)
        bad = subfamily_criterion_violations(edges, 3 * r - 3)
        no1 = all(any(v not in e for e in edges) for v in verts)
        pair = {0, 1}
        ok2 = all(e & pair for e in edges)
        check(f"E: pendant^{r-6}(H_6): {r}-uniform, L({r}) subfam, tau=2",
              ok_unif and not bad and no1 and ok2)

    # ----------------------------------------------------------------------------

    print()
    if FAIL:
        print(f"OVERALL: FAIL ({len(FAIL)} failed checks): {FAIL}")
        sys.exit(1)
    print("OVERALL: ALL CHECKS PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
