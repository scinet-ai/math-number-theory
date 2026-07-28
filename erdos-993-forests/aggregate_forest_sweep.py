#!/usr/bin/env python3
"""Aggregate + certify the banked forest-sweep chunk logs (Lane B).

Certification, per order k = 1..29:
  - every task (k, res, mod) from tasks.txt is banked exactly once;
  - summed tree count == OEIS A000055(k) exactly (full coverage of the
    order-k stream, since gentreeg's res/mod classes partition it);
  - summed product checks == A000055(k) * nq(k) (every streamed tree was
    convolved against the complete order-k q-set);
  - nonunimodal total (a nonzero value would be a counterexample to #993).
Then the global coverage statement: with the q-set construction certified in
build_qsets.py (totals == Euler transform of A000055, == A005195 where the
cap is not binding), every disconnected forest on <= 30 vertices F = T + q
(T a maximum component) has had its independence sequence checked.

Exit nonzero unless every certificate passes and nonunimodal == 0.
"""
import json
import re
import sys
from collections import defaultdict

BASE = "/Users/alexroman/research/scinet_seeding/erdos-fleet/attacks/erdos-993-forests"
A000055 = {1: 1, 2: 1, 3: 1, 4: 2, 5: 3, 6: 6, 7: 11, 8: 23, 9: 47, 10: 106,
           11: 235, 12: 551, 13: 1301, 14: 3159, 15: 7741, 16: 19320,
           17: 48629, 18: 123867, 19: 317955, 20: 823065, 21: 2144505,
           22: 5623756, 23: 14828074, 24: 39299897, 25: 104636890,
           26: 279793450, 27: 751065460, 28: 2023443032, 29: 5469566585}
MASK = (1 << 64) - 1

meta = json.load(open(f"{BASE}/qsets/qset_meta.json"))
tasks = [tuple(map(int, l.split())) for l in open(f"{BASE}/tasks.txt")]

per_k = defaultdict(lambda: {"trees": 0, "checks": 0, "nonuni": 0,
                             "nonlc": 0, "hash": 0, "tasks": 0, "cpu": 0.0})
for (k, res, mod) in tasks:
    path = f"{BASE}/logs/task_{k}_{res}_{mod}.done"
    try:
        txt = open(path).read()
    except FileNotFoundError:
        print(f"MISSING banked task {k} {res}/{mod}")
        sys.exit(1)
    m = re.search(r"FCHECK k=(\d+) trees=(\d+) qpolys=(\d+) checks=(\d+) "
                  r"nonunimodal=(\d+) nonlogconcave=(\d+) hash=([0-9a-f]+) "
                  r"gentreeg_nout=(\d+) cpu=([\d.]+)", txt)
    assert m, f"bad FCHECK in {path}"
    kk, trees, qp, checks, nu, nlc, h, nout, cpu = m.groups()
    assert int(kk) == k and int(nout) == int(trees)
    assert int(qp) == meta[str(k)]["nq"], f"{path}: q-set size mismatch"
    d = per_k[k]
    d["trees"] += int(trees); d["checks"] += int(checks)
    d["nonuni"] += int(nu); d["nonlc"] += int(nlc)
    d["hash"] = (d["hash"] + int(h, 16)) & MASK
    d["tasks"] += 1; d["cpu"] += float(cpu)

total = {"trees": 0, "checks": 0, "nonuni": 0, "nonlc": 0, "cpu": 0.0}
out = open(f"{BASE}/results/forest_sweep_summary.txt", "w")
out.write("Exhaustive unimodality check of all forests on <= 30 vertices "
          "(disconnected ones;\nsingle trees were exhausted by round 1). "
          "Scheme: for every tree T of order k\n(gentreeg stream) and every "
          "distinct forest polynomial q on m <= 30-k vertices\nwith "
          "components of order <= k, test p_T * q. Chunk hashes are "
          "order-independent\nFNV-1a sums.\n\n"
          "  k      trees(=A000055)      q-polys       product_checks  "
          "nonuni  nonLC  hash\n")
ok = True
for k in range(1, 30):
    d = per_k[k]
    nq = meta[str(k)]["nq"]
    expect_tasks = sum(1 for (kk, _, _) in tasks if kk == k)
    line_ok = (d["trees"] == A000055[k] and d["checks"] == A000055[k] * nq
               and d["tasks"] == expect_tasks)
    ok &= line_ok
    out.write(f" {k:3d} {d['trees']:18,} {nq:12,} {d['checks']:20,} "
              f"{d['nonuni']:6d} {d['nonlc']:6d}  {d['hash']:016x}"
              f"{'' if line_ok else '  *** MISMATCH ***'}\n")
    for key in ("trees", "checks", "nonuni", "nonlc", "cpu"):
        total[key] += d[key]
out.write(f"\ntotals: {len(tasks)} banked chunk tasks; trees streamed "
          f"{total['trees']:,}; distinct q-polynomials "
          f"{sum(meta[str(k)]['nq'] for k in range(1, 30)):,}; product checks "
          f"{total['checks']:,};\nnon-unimodal {total['nonuni']}; "
          f"non-log-concave products {total['nonlc']}; "
          f"check cpu {total['cpu']:.0f}s\n")
# coverage bookkeeping from OEIS b-files (fetched 2026-07-27)
A005195 = [0, 1, 2, 3, 6, 10, 20, 37, 76, 153, 329, 710, 1601, 3658, 8599,
           20514, 49905, 122963, 307199, 775529, 1977878, 5086638, 13184156,
           34402932, 90328674, 238474986, 632775648, 1686705630, 4514955632,
           12132227370, 32717113805]
tot_forests = sum(A005195[1:31])
tot_trees30 = sum(A000055[k] for k in range(1, 30)) + 14830871802
out.write(f"coverage: forests on 1..30 vertices (OEIS A005195 partial sum) = "
          f"{tot_forests:,},\nof which {tot_trees30:,} are single trees "
          f"(verified by round 1, orders 1..30)\nand {tot_forests - tot_trees30:,} "
          f"are disconnected -- each factoring as T + q with T a\nmaximum "
          f"component of order k <= 29 and poly(q) in the order-k q-set, so "
          f"each is\ncovered by the {total['checks']:,} distinct (T, q) "
          f"product checks above.\n")
out.write(f"certificates: per-order tree counts == A000055, checks == "
          f"trees x nq: {'ALL PASS' if ok else 'FAILED'}\n")
if total["nonuni"] == 0 and ok:
    out.write("RESULT: every forest on <= 30 vertices has a unimodal "
              "independent-set sequence.\n")
out.close()
print(open(f"{BASE}/results/forest_sweep_summary.txt").read())
sys.exit(0 if (ok and total["nonuni"] == 0) else 1)
