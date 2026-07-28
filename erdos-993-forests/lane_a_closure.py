#!/usr/bin/env python3
"""Lane A: structural closure over the 149 non-log-concave trees on <= 30 vertices.

Theory (classical results, cited in README):
  [Hoggar 1974]      The product of log-concave positive-coefficient polynomials
                     is log-concave.
  [Keilson-Gerber 71] A nonnegative sequence with interval support is strongly
                     unimodal (its convolution with EVERY unimodal sequence is
                     unimodal) iff it is log-concave.  In particular
                     LC * unimodal = unimodal.

Consequence: let F be a forest all of whose components have <= 30 vertices.
Round 1 (finding b1eaa502) proved every tree on <= 30 vertices is unimodal and
that exactly 149 of them are non-log-concave.  Write F = L + M where L collects
the log-concave components and M the non-log-concave ones (all from the 149,
up to isomorphism).  poly(L) is LC (Hoggar).  If poly(M) is unimodal then
poly(F) = poly(L) * poly(M) is unimodal (Keilson-Gerber).  So

    F non-unimodal  ==>  the pure product of its non-LC components is
                         non-unimodal.

Moreover if M is non-unimodal then for EVERY split M = A + B into nonempty
sub-multisets, poly(A) and poly(B) are both non-LC provided both are unimodal
(else K-G/Hoggar make poly(M) unimodal).  Inductively (verifying levels
r = 2, 3, ... in order) every proper nonempty sub-multiset of a minimal
non-unimodal M must have a non-log-concave product.  This is a hereditary
condition, so the candidate multisets at level r are exactly the extensions
by one tree of the level-(r-1) hereditary risk set

    H_{r-1} = { multisets Q of size r-1 from the 149 :
                poly(Q) non-LC and every proper sub-multiset non-LC },

and if some H_r = empty set (with all candidates up to level r verified
unimodal), NO forest with all components <= 30 vertices can be non-unimodal,
at any size: any minimal counterexample M would have all its r-sub-multisets
in H_r.  This script runs that closure.

Everything is exact big-integer arithmetic.  Any non-unimodal product found is
a COUNTEREXAMPLE to Erdős #993 and is dumped in full machine-checkable detail.
"""
import itertools
import sys
import time

sys.path.insert(0, "/Users/alexroman/research/scinet_seeding/erdos-fleet/attacks/erdos-993-forests")
from poly993 import (conv, is_unimodal, first_valley, is_log_concave,
                     independence_sequence, load_round1_nonlogconcave)

ROUND1 = "/Users/alexroman/research/scinet_seeding/erdos-fleet/attacks/erdos-993"
OUT = "/Users/alexroman/research/scinet_seeding/erdos-fleet/attacks/erdos-993-forests/results"
MAX_LEVEL = 8
H_CAP = 3_000_000  # runaway guard


def main():
    t0 = time.time()
    log = open(f"{OUT}/lane_a_closure.txt", "w")

    def emit(msg):
        print(msg)
        log.write(msg + "\n")
        log.flush()

    trees = load_round1_nonlogconcave(f"{ROUND1}/results")
    assert len(trees) == 149, f"expected 149 non-LC trees, got {len(trees)}"

    # Step 1: independently recompute every banked sequence from its parent
    # array with this workspace's own DP; assert byte-identical, non-LC,
    # unimodal, positive, i1 = n.
    by_order = {}
    for idx, t in enumerate(trees):
        seq = independence_sequence(t["par"])
        assert seq == t["seq"], f"tree {idx}: recomputed sequence differs"
        assert all(x > 0 for x in seq), f"tree {idx}: internal zero"
        assert seq[0] == 1 and seq[1] == t["n"], f"tree {idx}: bad head"
        assert not is_log_concave(seq), f"tree {idx}: unexpectedly log-concave"
        assert is_unimodal(seq), f"tree {idx}: NON-UNIMODAL SINGLE TREE?!"
        by_order[t["n"]] = by_order.get(t["n"], 0) + 1
    emit(f"[{time.time()-t0:7.1f}s] loaded+reverified all 149 non-LC trees "
         f"(orders {by_order}); all non-LC, all unimodal, seqs match round 1")

    polys = [t["seq"] for t in trees]
    orders = [t["n"] for t in trees]

    # Step 2: closure levels.
    # H entries: sorted index tuple -> product poly
    H_prev = {(i,): polys[i] for i in range(149)}  # level 1: all 149 (non-LC by construction)
    level = 1
    total_products_checked = 0
    counterexample = False
    while H_prev and level < MAX_LEVEL:
        level += 1
        # candidates: extend each Q in H_{r-1} by one tree index
        cand = {}
        for Q, pQ in H_prev.items():
            for t in range(149):
                M = tuple(sorted(Q + (t,)))
                if M not in cand:
                    cand[M] = (Q, t)
        emit(f"[{time.time()-t0:7.1f}s] level {level}: {len(cand)} candidate "
             f"multisets (extensions of |H_{level-1}|={len(H_prev)})")
        if len(cand) > H_CAP:
            emit(f"level {level}: candidate count exceeds cap {H_CAP}; "
                 f"stopping closure here (partial result through level {level-1})")
            level -= 1
            break
        H_cur = {}
        n_nonlc = n_lc = n_nonhered = 0
        for M, (Q, t) in cand.items():
            p = conv(H_prev[Q], polys[t])  # Q always in H_prev by construction
            total_products_checked += 1
            if not is_unimodal(p):
                counterexample = True
                report_counterexample(M, p, trees, emit)
            # hereditary: every (r-1)-sub-multiset in H_{r-1}
            hered = all(tuple(sorted(M[:k] + M[k+1:])) in H_prev
                        for k in range(len(M))
                        if k == 0 or M[k] != M[k-1])
            if not hered:
                n_nonhered += 1  # provably unimodal via K-G; checked anyway above
                continue
            if is_log_concave(p):
                n_lc += 1
            else:
                n_nonlc += 1
                H_cur[M] = p
        vmin = min((sum(orders[i] for i in M) for M in H_cur), default=None)
        vmax = max((sum(orders[i] for i in M) for M in H_cur), default=None)
        emit(f"[{time.time()-t0:7.1f}s] level {level}: all {len(cand)} products "
             f"UNIMODAL; hereditary candidates: {n_lc} log-concave, "
             f"{n_nonlc} non-log-concave -> |H_{level}| = {len(H_cur)}"
             + (f" (total vertices {vmin}..{vmax})" if H_cur else "")
             + f"; non-hereditary (K-G-guaranteed, still checked): {n_nonhered}")
        if level == 2 and H_cur:
            with open(f"{OUT}/lane_a_H2_members.txt", "w") as fh:
                for M, p in sorted(H_cur.items()):
                    fh.write(f"H2 idx={M[0]},{M[1]} orders={orders[M[0]]},{orders[M[1]]} "
                             f"seq={','.join(map(str, p))}\n")
            emit(f"          H_2 members written to lane_a_H2_members.txt")
        H_prev = H_cur

    emit(f"[{time.time()-t0:7.1f}s] closure ended at level {level}; "
         f"H_{level} size = {len(H_prev)}; "
         f"products checked (levels 2..{level}): {total_products_checked}; "
         f"counterexample found: {counterexample}")
    if not H_prev and not counterexample:
        emit("CLOSURE TERMINATED EMPTY => THEOREM (conditional only on "
             "Hoggar 1974 + Keilson-Gerber 1971 + the round-1 exhaustive "
             "tree results): EVERY forest all of whose components have at "
             "most 30 vertices has a unimodal independent-set sequence. "
             "Any counterexample to Erdős #993 must contain a tree "
             "component on >= 31 vertices.")
        status = "CLOSED"
    elif counterexample:
        status = "COUNTEREXAMPLE"
    else:
        status = f"PARTIAL_THROUGH_LEVEL_{level}"
    emit(f"LANE_A_STATUS {status}")
    log.close()
    return 0 if status != "COUNTEREXAMPLE" else 2


def prod_poly(M, polys):
    p = polys[M[0]]
    for i in M[1:]:
        p = conv(p, polys[i])
    return p


def prod_poly_direct(M, polys):
    return prod_poly(M, polys)


def report_counterexample(M, p, trees, emit):
    emit("=" * 70)
    emit("NON-UNIMODAL FOREST PRODUCT FOUND — COUNTEREXAMPLE TO ERDŐS #993")
    a, b, c = first_valley(p)
    emit(f"components (indices into the 149): {M}")
    for i in M:
        t = trees[i]
        emit(f"  component n={t['n']} par={','.join(map(str, t['par']))}")
    emit(f"product sequence: {','.join(map(str, p))}")
    emit(f"valley: i_{a}={p[a]} > i_{b}={p[b]} < i_{c}={p[c]}")
    emit("=" * 70)


if __name__ == "__main__":
    sys.exit(main())
