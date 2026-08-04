#!/usr/bin/env python3
"""Certify the lower-bound gadgets for t(6) >= 2 and t(7) >= 2, and run the
exhaustive one-edge-extension check for the key step of the t(6)=2 proof.

Gadget(r): vertices X = {x_1..x_4} plus four pairwise-disjoint private sets
B_1..B_4 of size r-3; edges E_i = (X \\ {x_i}) u B_i. Span = 4(r-2).

Checks (all direct from the definition of the local property; no lemmas used):
 (1) L(r): for EVERY subfamily of the 4 edges with |union| <= 3r-3, the
     subfamily has a common vertex. [Equivalent to: every induced subgraph on
     <= 3r-3 vertices has tau <= 1, since the edges inside a vertex set S form
     a subfamily with union <= |S|, and conversely S := union works.]
     We also run the literal definition over all vertex subsets S of the gadget's
     vertex set with |S| <= 3r-3 (feasible because span is 16 resp. 20).
 (2) tau(gadget) = 2 exactly: no single vertex covers all 4 edges; an explicit
     pair does.
 (3) [r=6 only] Exhaustive extension check of the final proof step: on a ground
     set of 16 gadget vertices + 6 fresh vertices, for EVERY 6-subset F, if
     {E_1..E_4, F} still satisfies L(6) (checked by complete enumeration of all
     2^5 subfamilies -- no minimality lemma needed), then F meets E_1 n E_2
     (= {x_3,x_4}).  This is exactly the deduction "the pair E_1 n E_2 is a
     transversal of any L(6)-hypergraph containing the gadget", tested against
     all possible single additional edges.
"""
from itertools import combinations, chain

def gadget(r):
    X = list(range(4))
    B = []
    v = 4
    for i in range(4):
        B.append(set(range(v, v + r - 3)))
        v += r - 3
    edges = [set(X) - {i} | B[i] for i in range(4)]
    return edges, v  # v = span

def common(subfam):
    return set.intersection(*subfam) if subfam else None

def check_local_subfamilies(edges, r):
    """L(r) via subfamilies: every subfamily with union <= 3r-3 has common vertex."""
    w = 3*r - 3
    for k in range(2, len(edges)+1):
        for sub in combinations(edges, k):
            u = set().union(*sub)
            if len(u) <= w:
                assert common(list(sub)), f"L({r}) fails on subfamily with union {len(u)}"
    return True

def check_local_literal(edges, r):
    """L(r) literally: every vertex subset S with |S| <= 3r-3 induces tau <= 1."""
    w = 3*r - 3
    V = sorted(set().union(*edges))
    n = len(V)
    # only need |S| in [r, w]; smaller S contain no edges
    count = 0
    for size in range(r, w+1):
        for S in combinations(V, size):
            Sset = set(S)
            inside = [E for E in edges if E <= Sset]
            if len(inside) >= 1:
                # tau <= 1 iff common vertex
                assert common(inside), f"induced subgraph on {size} vertices has tau >= 2"
            count += 1
    return count

def check_tau_exactly_2(edges):
    V = set().union(*edges)
    assert not any(all(v in E for E in edges) for v in V), "tau <= 1?!"
    pairs = [p for p in combinations(sorted(V), 2)
             if all(p[0] in E or p[1] in E for E in edges)]
    assert pairs, "no covering pair found: tau > 2?!"
    return pairs[:3]

def extension_check_r6(extra=6):
    r = 6
    edges, span = gadget(r)
    assert span == 16
    ground = list(range(span + extra))
    E12 = edges[0] & edges[1]
    assert len(E12) == 2
    tested = passed_local = 0
    for F in combinations(ground, 6):
        Fs = set(F)
        fam = edges + [Fs]
        # complete direct L(6) check on the 5-edge family: all subfamilies
        ok = True
        for k in range(2, 6):
            for sub in combinations(fam, k):
                u = set().union(*sub)
                if len(u) <= 15 and not common(list(sub)):
                    ok = False
                    break
            if not ok:
                break
        tested += 1
        if ok:
            passed_local += 1
            assert Fs & E12, \
                f"COUNTEREXAMPLE to key step: F={sorted(Fs)} is L(6)-compatible but avoids E1 n E2"
    return tested, passed_local

def main():
    for r in (6, 7):
        edges, span = gadget(r)
        print(f"r={r}: gadget span={span} (> {3*r-3}: {span > 3*r-3})")
        check_local_subfamilies(edges, r)
        print(f"  L({r}) via all subfamilies: OK")
        cnt = check_local_literal(edges, r)
        print(f"  L({r}) literal (all {cnt} vertex subsets of size {r}..{3*r-3}): OK")
        pairs = check_tau_exactly_2(edges)
        print(f"  tau = 2 exactly (no single vertex covers; covering pairs e.g. {pairs}): OK")
    tested, passed = extension_check_r6()
    print(f"r=6 extension check: {tested} candidate edges F on 22 vertices; "
          f"{passed} were L(6)-compatible with the gadget; ALL of them meet E1 n E2. OK")
    print("\nALL GADGET CHECKS PASSED")

if __name__ == "__main__":
    main()
