#!/usr/bin/env python3
"""Build the per-order q-sets for the exhaustive forest sweep (Lane B).

For the order-k tree stream the q-set is the family of DISTINCT independence
polynomials of forests on m = 1..30-k vertices whose components all have at
most min(k, 30-k) vertices, together with the number of forests realising
each polynomial (the multiplicity, used only for coverage accounting).

Built by an exact multiset-knapsack DP over tree isomorphism types of order
<= 15 (dumped from gentreeg by the round-1-validated plugin and re-verified
here with an independent Python DP).  Every total count is cross-checked
against an INDEPENDENT Euler-transform computation from the A000055 tree
counts, and, where the cap is not binding, against OEIS A005195 (b-file).

Outputs:
  qsets/qset_k<k>.txt    header "NQ <n> K <k> BUDGET <b>" + one poly/line
  qsets/qset_meta.json   per-(k, m) distinct-poly and forest counts
  results/qset_build_log.txt
"""
import json
import sys
import time
from collections import defaultdict

sys.path.insert(0, "/Users/alexroman/research/scinet_seeding/erdos-fleet/attacks/erdos-993-forests")
from poly993 import conv, independence_sequence

BASE = "/Users/alexroman/research/scinet_seeding/erdos-fleet/attacks/erdos-993-forests"
SCRATCH_B5195 = "/private/tmp/claude-501/-Users-alexroman-projects-scinet/899ffdba-14dc-46c4-943f-1201e4628d28/scratchpad/b005195.txt"
TOTAL = 30  # verify all forests on <= TOTAL vertices
A000055 = [1, 1, 1, 1, 2, 3, 6, 11, 23, 47, 106, 235, 551, 1301, 3159, 7741]
# ^ index = order, orders 0..15 (order 0 unused)


def load_tree_polys():
    """Parse the gentreeg SEQ dump; re-verify every poly independently."""
    by_order = defaultdict(list)
    with open(f"{BASE}/qsets/trees_1_15_seqs.txt") as fh:
        for line in fh:
            assert line.startswith("SEQ ")
            fields = dict(tok.split("=", 1) for tok in line.split()[1:])
            n = int(fields["n"])
            par = [int(x) for x in fields["par"].split(",")]
            seq = tuple(int(x) for x in fields["seq"].split(","))
            assert list(seq) == independence_sequence(par), \
                f"order-{n} tree poly mismatch C vs Python"
            by_order[n].append(seq)
    for n in range(1, 16):
        assert len(by_order[n]) == A000055[n], \
            f"order {n}: {len(by_order[n])} trees, expected {A000055[n]}"
    return by_order


def forests_euler(cap, upto):
    """Forest counts with all components of order <= cap, via the Euler
    transform of the (truncated) tree counts -- an independent formula
    (divisor sums + the standard recurrence)."""
    t = [A000055[j] if 1 <= j <= cap else 0 for j in range(upto + 1)]
    c = [0] * (upto + 1)
    for n in range(1, upto + 1):
        c[n] = sum(d * t[d] for d in range(1, n + 1) if n % d == 0)
    F = [0] * (upto + 1)
    F[0] = 1
    for n in range(1, upto + 1):
        F[n] = (c[n] + sum(c[j] * F[n - j] for j in range(1, n))) // n
    return F


def build_capped(cap, budget, tree_polys):
    """DP: sets[m] = {poly_tuple: number of forests}, comps of order <= cap."""
    sets = [defaultdict(int) for _ in range(budget + 1)]
    sets[0][(1,)] = 1
    for order in range(1, min(cap, budget) + 1):
        for tp in tree_polys[order]:
            for m in range(order, budget + 1):
                src = sets[m - order]
                if not src:
                    continue
                dst = sets[m]
                for poly, cnt in list(src.items()):
                    dst[tuple(conv(list(poly), list(tp)))] += cnt
    return sets


def main():
    t0 = time.time()
    log = open(f"{BASE}/results/qset_build_log.txt", "w")

    def emit(msg):
        print(msg, flush=True)
        log.write(msg + "\n")
        log.flush()

    a5195 = {}
    with open(SCRATCH_B5195) as fh:
        for line in fh:
            parts = line.split()
            if len(parts) == 2:
                a5195[int(parts[0])] = int(parts[1])

    tree_polys = load_tree_polys()
    emit(f"[{time.time()-t0:6.1f}s] loaded + independently re-verified "
         f"{sum(len(v) for v in tree_polys.values())} tree polynomials (orders 1..15)")

    meta = {}
    # caps actually needed: cap(k) = min(k, 30-k); k>=15 all share cap=30-k with
    # budget=30-k -> nested inside the cap-15/budget-15 build.
    cache = {}
    for k in range(1, TOTAL):
        budget = TOTAL - k
        cap = min(k, budget)
        key = (cap, budget)
        if key not in cache:
            # a (cap, B) build also serves any smaller budget by truncation
            bigger = next((cache[(c2, b2)] for (c2, b2) in cache
                           if c2 == cap and b2 >= budget), None)
            if bigger is not None:
                cache[key] = bigger[:budget + 1]
            else:
                cache[key] = build_capped(cap, budget, tree_polys)
            # ---- independent cross-checks ----
            F = forests_euler(cap, budget)
            for m in range(1, budget + 1):
                tot = sum(cache[key][m].values())
                assert tot == F[m], \
                    f"cap={cap} m={m}: DP total {tot} != Euler {F[m]}"
                if cap >= m:
                    assert tot == a5195[m], \
                        f"m={m}: unrestricted total {tot} != A005195 {a5195[m]}"
            emit(f"[{time.time()-t0:6.1f}s] built cap={cap} budget={budget}: "
                 + " ".join(f"m{m}:{len(cache[key][m])}/{sum(cache[key][m].values())}"
                            for m in range(1, budget + 1)))
        sets = cache[key]
        # write the flattened q-set for this k
        polys = []
        per_m = {}
        for m in range(1, budget + 1):
            per_m[m] = {"distinct": len(sets[m]),
                        "forests": sum(sets[m].values())}
            polys.extend(sets[m].keys())
        # cross-m dedupe is NOT applied: identical polynomials arising at
        # different m are kept once each anyway via dict-per-m; a poly can
        # repeat across m (padding differences impossible: i_1 = m differs),
        # so entries are distinct across m too.  Assert it:
        assert len(set(polys)) == len(polys), f"k={k}: cross-m poly collision?!"
        with open(f"{BASE}/qsets/qset_k{k}.txt", "w") as fh:
            fh.write(f"NQ {len(polys)} K {k} BUDGET {budget}\n")
            for p in polys:
                assert p[0] == 1 and p[-1] > 0 and all(c < (1 << 28) for c in p)
                fh.write(f"{len(p)} " + " ".join(map(str, p)) + "\n")
        meta[k] = {"budget": budget, "cap": cap, "nq": len(polys),
                   "per_m": per_m}
        emit(f"[{time.time()-t0:6.1f}s] k={k}: q-set nq={len(polys)} "
             f"(forests represented: {sum(v['forests'] for v in per_m.values())})")
    with open(f"{BASE}/qsets/qset_meta.json", "w") as fh:
        json.dump(meta, fh, indent=1)
    emit(f"[{time.time()-t0:6.1f}s] DONE; meta written")
    log.close()


if __name__ == "__main__":
    main()
