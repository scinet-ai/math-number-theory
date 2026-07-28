#!/usr/bin/env python3
"""Independently re-verify the sweep's non-log-concave forest by-product census.

By Hoggar (1974) a product of log-concave positive polynomials is log-concave,
and round 1 proved every tree on <= 29 vertices except 28 specific trees
(2 of order 26, 19 of order 28, 7 of order 29) is log-concave; every q-set
polynomial is a product of trees of order <= 15, hence log-concave.  So a
non-log-concave product p_T * q in the <=30-vertex forest sweep can only have
T among those 28 trees.  This script:
  1. parses every NONLOGCONCAVE line banked by the sweep (logs/task_*.out),
     rebuilds the tree from its parent array with the independent Python DP,
     recomputes the product in big-int arithmetic, and asserts the sequence
     matches byte-for-byte, is genuinely non-log-concave, and is unimodal;
  2. recomputes the census from scratch: all products (28 non-LC trees of
     order <= 29) x (full order-k q-set) and asserts the per-order non-LC
     counts equal the sweep's FCHECK totals -- proving the banked lines are
     the complete census (no SAVE_LIMIT truncation);
  3. writes results/nonlc_products_recheck.txt.
Exit nonzero on any failure.
"""
import glob
import re
import sys
from collections import defaultdict

sys.path.insert(0, "/Users/alexroman/research/scinet_seeding/erdos-fleet/attacks/erdos-993-forests")
from poly993 import (conv, is_unimodal, is_log_concave, independence_sequence,
                     load_round1_nonlogconcave)

BASE = "/Users/alexroman/research/scinet_seeding/erdos-fleet/attacks/erdos-993-forests"
ROUND1 = "/Users/alexroman/research/scinet_seeding/erdos-fleet/attacks/erdos-993"


def load_qset(k):
    with open(f"{BASE}/qsets/qset_k{k}.txt") as fh:
        header = fh.readline().split()
        nq = int(header[1])
        polys = []
        for line in fh:
            parts = [int(x) for x in line.split()]
            assert parts[0] == len(parts) - 1
            polys.append(parts[1:])
        assert len(polys) == nq
    return polys


def main():
    out = open(f"{BASE}/results/nonlc_products_recheck.txt", "w")
    saved = []
    for path in sorted(glob.glob(f"{BASE}/logs/task_*.out")):
        for line in open(path):
            if line.startswith("NONUNIMODAL"):
                print(f"COUNTEREXAMPLE LINE PRESENT: {path}: {line}")
                sys.exit(2)
            if not line.startswith("NONLOGCONCAVE"):
                continue
            fields = dict(tok.split("=", 1) for tok in line.split()[1:])
            k = int(fields["k"])
            par = [int(x) for x in fields["par"].split(",")]
            q = [int(x) for x in fields["q"].split(",")]
            seq = [int(x) for x in fields["seq"].split(",")]
            tseq = independence_sequence(par)
            prod = conv(tseq, q)
            assert prod == seq, f"{path}: recomputed product differs"
            assert not is_log_concave(prod), f"{path}: product is LC?!"
            assert is_unimodal(prod), f"{path}: NON-UNIMODAL product?!"
            saved.append((k, tuple(tseq), tuple(q), tuple(seq)))
    per_k_saved = defaultdict(int)
    for k, *_ in saved:
        per_k_saved[k] += 1

    # census from scratch
    r1 = load_round1_nonlogconcave(f"{ROUND1}/results")
    nonlc_by_order = defaultdict(list)
    for t in r1:
        if t["n"] <= 29:
            nonlc_by_order[t["n"]].append(t["seq"])
    assert {k: len(v) for k, v in nonlc_by_order.items()} == {26: 2, 28: 19, 29: 7}
    per_k_pred = {}
    pred_set = set()
    for k, seqs in sorted(nonlc_by_order.items()):
        qs = load_qset(k)
        cnt = 0
        for ts in seqs:
            for q in qs:
                p = conv(ts, q)
                assert is_unimodal(p)
                if not is_log_concave(p):
                    cnt += 1
                    pred_set.add((k, tuple(p)))
        per_k_pred[k] = cnt

    # sweep FCHECK totals
    per_k_fcheck = defaultdict(int)
    for path in glob.glob(f"{BASE}/logs/task_*.done"):
        m = re.search(r"FCHECK k=(\d+) .* nonlogconcave=(\d+)", open(path).read())
        per_k_fcheck[int(m.group(1))] += int(m.group(2))
    for k in range(1, 30):
        assert per_k_fcheck[k] == per_k_pred.get(k, 0), \
            f"k={k}: sweep nonLC {per_k_fcheck[k]} != predicted {per_k_pred.get(k, 0)}"
        assert per_k_saved[k] == per_k_fcheck[k], \
            f"k={k}: saved lines {per_k_saved[k]} != counted {per_k_fcheck[k]} (truncation?)"
    assert {(k, s) for k, _, _, s in saved} == pred_set

    # forest multiplicities: how many distinct forests realise each non-LC
    # product (a q-polynomial can be shared by several q-forests)
    from build_qsets import build_capped, load_tree_polys
    tree_polys = load_tree_polys()
    forest_count = 0
    per_k_forests = {}
    for k in sorted(nonlc_by_order):
        budget = 30 - k
        sets = build_capped(min(k, budget), budget, tree_polys)
        mult = {}
        for m in range(1, budget + 1):
            for p, w in sets[m].items():
                mult[tuple(p)] = w
        cnt = 0
        for ts in nonlc_by_order[k]:
            for q in load_qset(k):
                if not is_log_concave(conv(ts, q)):
                    cnt += mult[tuple(q)]
        per_k_forests[k] = cnt
        forest_count += cnt

    out.write("Non-log-concave products in the <=30-vertex forest sweep "
              "(all unimodal; all\nindependently recomputed in Python big-int "
              "arithmetic; census completeness\nproved against a from-scratch "
              "recomputation over the 28 non-LC trees of order\n<= 29 x their "
              "full q-sets):\n\n")
    for k in sorted(per_k_pred):
        out.write(f"  order-{k} tree component: {per_k_pred[k]} non-log-concave "
                  f"products (of {len(nonlc_by_order[k])} x {len(load_qset(k))} "
                  f"candidate products)\n")
    out.write(f"\ntotal: {len(saved)} distinct non-log-concave product "
              f"polynomials, realised by\n"
              + "".join(f"  {per_k_forests[k]} disconnected forests with an "
                        f"order-{k} non-LC component\n" for k in sorted(per_k_forests))
              + f"= {forest_count} disconnected non-log-concave forests on "
              f"<= 30 vertices; every one\nis unimodal.  (By Hoggar's theorem "
              f"these, plus the 149 non-LC trees of round 1,\nare the ONLY "
              f"non-log-concave forests on <= 30 vertices: "
              f"{149 + forest_count} in all.)\n")
    out.close()
    print(open(f"{BASE}/results/nonlc_products_recheck.txt").read())
    print("RECHECK PASSED")


if __name__ == "__main__":
    main()
