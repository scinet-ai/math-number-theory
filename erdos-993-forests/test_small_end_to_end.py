#!/usr/bin/env python3
"""End-to-end validation of the forest pipeline at TOTAL=12 (exit nonzero on fail).

1. PRODUCT IDENTITY + BRUTE FORCE: enumerate ALL forests on 1..12 vertices as
   explicit graphs (multisets of gentreeg trees, disjoint union), compute the
   independence sequence two ways -- brute-force 2^n subset enumeration on the
   forest graph, and the product of the components' polynomials -- and assert
   they agree.  Counts per n must equal OEIS A005195.
2. C PIPELINE: build the TOTAL=12 q-sets, run gentreeg_forest for k=1..11,
   and reproduce every FCHECK line (trees, checks, counts, aggregate FNV hash)
   with an independent Python computation of the same (tree, q) products.
3. COVERAGE IDENTITY: sum over streamed (tree, q) pairs of q-multiplicities
   equals sum over disconnected forests F on <= 12 vertices of (# maximum
   components of F), computed from the explicit enumeration of step 1.
"""
import os
import subprocess
import sys
from collections import defaultdict
from itertools import combinations_with_replacement

sys.path.insert(0, "/Users/alexroman/research/scinet_seeding/erdos-fleet/attacks/erdos-993-forests")
from poly993 import (conv, independence_sequence, brute_force_sequence,
                     parents_to_edges, is_unimodal)
from build_qsets import build_capped, load_tree_polys, forests_euler

BASE = "/Users/alexroman/research/scinet_seeding/erdos-fleet/attacks/erdos-993-forests"
T = 12
A005195 = {1: 1, 2: 2, 3: 3, 4: 6, 5: 10, 6: 20, 7: 37, 8: 76, 9: 153,
           10: 329, 11: 710, 12: 1601}
A000055 = [1, 1, 1, 1, 2, 3, 6, 11, 23, 47, 106, 235, 551]

MASK = (1 << 64) - 1


def fnv(seq):
    h = 1469598103934665603
    for c in seq:
        h ^= c
        h = (h * 1099511628211) & MASK
    return h


class Tee:
    def __init__(self, path):
        self.fh = open(path, "w")
        self.stdout = sys.stdout

    def write(self, s):
        self.fh.write(s)
        self.stdout.write(s)

    def flush(self):
        self.fh.flush()
        self.stdout.flush()


def main():
    sys.stdout = Tee(f"{BASE}/results/end_to_end_12.txt")
    # --- load trees with par arrays (orders 1..12) ---
    trees = defaultdict(list)  # order -> list of (par, seq)
    with open(f"{BASE}/qsets/trees_1_15_seqs.txt") as fh:
        for line in fh:
            fields = dict(tok.split("=", 1) for tok in line.split()[1:])
            n = int(fields["n"])
            if n > T:
                continue
            par = [int(x) for x in fields["par"].split(",")]
            seq = [int(x) for x in fields["seq"].split(",")]
            trees[n].append((par, seq))
    for n in range(1, T + 1):
        assert len(trees[n]) == A000055[n]

    # --- step 1: all forests on <= 12 vertices, explicitly ---
    print("step 1: enumerating all forests on 1..12 vertices explicitly ...")
    tree_list = [(n, par, seq) for n in range(1, T + 1)
                 for (par, seq) in trees[n]]  # index = iso type
    per_n_count = defaultdict(int)
    m_max_sum = defaultdict(int)   # n -> sum of #max-components over disconnected forests
    checked = 0

    def rec(start_idx, remaining, comps):
        nonlocal checked
        # comps: list of type indices chosen so far (nondecreasing)
        if comps:
            n = T - remaining
            per_n_count[n] += 1
            # build explicit forest graph
            edges, seqs, offset = [], [], 0
            for ti in comps:
                tn, par, seq = tree_list[ti]
                edges += [(u + offset, v + offset) for u, v in parents_to_edges(par)]
                seqs.append(seq)
                offset += tn
            prod = [1]
            for s in seqs:
                prod = conv(prod, s)
            bf = brute_force_sequence(offset, edges)
            assert prod == bf, f"product != brute force for comps {comps}"
            assert is_unimodal(prod), f"NON-UNIMODAL small forest {comps}: {prod}"
            checked += 1
            if len(comps) > 1:
                cmax = max(tree_list[ti][0] for ti in comps)
                # a forest is generated once per DISTINCT max-size component
                # type (removing equal copies leaves the same (T, q) pair)
                m_max_sum[n] += len({ti for ti in comps
                                     if tree_list[ti][0] == cmax})
        for ti in range(start_idx, len(tree_list)):
            tn = tree_list[ti][0]
            if tn <= remaining:
                rec(ti, remaining - tn, comps + [ti])

    rec(0, T, [])
    for n in range(1, T + 1):
        assert per_n_count[n] == A005195[n], \
            f"n={n}: enumerated {per_n_count[n]} forests != A005195 {A005195[n]}"
    print(f"  ok: {checked} forests, counts match A005195(1..12), "
          f"product==brute force everywhere, all unimodal")

    # --- step 2: mini q-sets + C binary comparison ---
    print("step 2: TOTAL=12 mini-sweep, C binary vs independent Python ...")
    tree_polys = load_tree_polys()
    os.makedirs(f"{BASE}/qsets/mini", exist_ok=True)
    total_checks_pred = 0
    for k in range(1, T):
        budget = T - k
        cap = min(k, budget)
        sets = build_capped(cap, budget, tree_polys)
        F = forests_euler(cap, budget)
        for m in range(1, budget + 1):
            assert sum(sets[m].values()) == F[m]
        polys, mults = [], []
        for m in range(1, budget + 1):
            for p, w in sets[m].items():
                polys.append(p)
                mults.append(w)
        path = f"{BASE}/qsets/mini/qset_k{k}.txt"
        with open(path, "w") as fh:
            fh.write(f"NQ {len(polys)} K {k} BUDGET {budget}\n")
            for p in polys:
                fh.write(f"{len(p)} " + " ".join(map(str, p)) + "\n")
        # independent Python prediction of the FCHECK line
        pred_hash = 0
        pred_checks = 0
        for (par, seq) in trees[k]:
            for p in polys:
                prod = conv(seq, list(p))
                assert is_unimodal(prod)
                pred_hash = (pred_hash + fnv(prod)) & MASK
                pred_checks += 1
        total_checks_pred += sum(mults) * len(trees[k])  # coverage accounting below
        env = dict(os.environ, QSET_FILE=path)
        r = subprocess.run([f"{BASE}/gentreeg_forest", "-q", str(k)],
                           capture_output=True, text=True, env=env)
        line = [l for l in r.stderr.splitlines() if l.startswith("FCHECK")][0]
        f = dict(tok.split("=", 1) for tok in line.replace("FCHECK ", "").split())
        assert int(f["trees"]) == A000055[k], line
        assert int(f["checks"]) == pred_checks == A000055[k] * len(polys), line
        assert int(f["nonunimodal"]) == 0, line
        assert int(f["hash"], 16) == pred_hash, \
            f"k={k}: C hash {f['hash']} != python {pred_hash:016x}"
        print(f"  k={k}: C FCHECK reproduced exactly (trees={f['trees']} "
              f"checks={f['checks']} hash={f['hash']})")

    # --- step 3: coverage identity ---
    print("step 3: coverage identity ...")
    # sum over (k, m) of A000055(k) * (#forests on m with comps <= k)  ==
    # sum over disconnected forests on <= 12 of (# distinct max-component
    # types), via the bijection (T, q) <-> (F = T + q, max type T)
    lhs = 0
    for k in range(1, T):
        budget = T - k
        cap = min(k, budget)
        F = forests_euler(cap, budget)
        lhs += A000055[k] * sum(F[1:budget + 1])
    rhs = sum(m_max_sum.values())
    assert lhs == rhs, f"coverage identity fails: {lhs} != {rhs}"
    print(f"  ok: sum_k trees(k) x forests(m<=12-k, comps<=k) = {lhs} = "
          f"sum over disconnected forests of #max-components (explicit)")
    print("ALL END-TO-END TESTS PASSED")


if __name__ == "__main__":
    main()
