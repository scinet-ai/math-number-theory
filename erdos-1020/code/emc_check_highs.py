#!/usr/bin/env python3
"""
Independent cross-check of f(n;r,k) with HiGHS (a different solver, model
rebuilt from scratch here). Same exact reduction as emc_solve.py:
shifted-family down-closure + all k-block r-partitions of [rk].

MIP: max sum x_A, x_A binary,
     x_B - x_A <= 0 for each cover move A <= B (A obtained by decrementing),
     sum_{B in partition} x_B <= k-1 for each partition of [rk].
Solved with mip_rel_gap = mip_abs_gap = 0 (exact optimality proof).

Usage: emc_check_highs.py R K N [N2 ...]
Exits nonzero if any cell's proven optimum disagrees with results.jsonl.
"""
import json
import math
import os
import sys
import time
from itertools import combinations

import highspy

C = math.comb


def partitions_into_blocks(universe, r):
    universe = tuple(universe)
    if not universe:
        yield ()
        return
    first, rest = universe[0], universe[1:]
    for others in combinations(rest, r - 1):
        block = (first,) + others
        rem = tuple(x for x in rest if x not in set(others))
        for tail in partitions_into_blocks(rem, r):
            yield (block,) + tail


def check(n, r, k, expected):
    t0 = time.time()
    sets = list(combinations(range(1, n + 1), r))
    idx = {A: i for i, A in enumerate(sets)}
    nv = len(sets)

    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("threads", 3)
    h.setOptionValue("mip_rel_gap", 0.0)
    h.setOptionValue("mip_abs_gap", 0.0)
    h.setOptionValue("random_seed", 0)

    inf = highspy.kHighsInf
    lp = highspy.HighsLp()
    lp.num_col_ = nv
    lp.col_cost_ = [-1.0] * nv          # minimize -sum => maximize sum
    lp.col_lower_ = [0.0] * nv
    lp.col_upper_ = [1.0] * nv
    lp.integrality_ = [highspy.HighsVarType.kInteger] * nv

    rows_lower, rows_upper, starts, indices, values = [], [], [], [], []

    def add_row(cols, coefs, lo, up):
        starts.append(len(indices))
        indices.extend(cols)
        values.extend(coefs)
        rows_lower.append(lo)
        rows_upper.append(up)

    # shift cover implications: x_B <= x_A  (A = B with one element decremented)
    for B in sets:
        sB = set(B)
        for i, b in enumerate(B):
            if b - 1 >= 1 and (b - 1) not in sB:
                A = tuple(sorted(B[:i] + (b - 1,) + B[i + 1:]))
                add_row([idx[B], idx[A]], [1.0, -1.0], -inf, 0.0)

    # matching constraints
    for p in partitions_into_blocks(tuple(range(1, r * k + 1)), r):
        add_row([idx[Bl] for Bl in p], [1.0] * k, -inf, float(k - 1))

    starts.append(len(indices))
    lp.num_row_ = len(rows_lower)
    lp.row_lower_ = rows_lower
    lp.row_upper_ = rows_upper
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_ = starts
    lp.a_matrix_.index_ = indices
    lp.a_matrix_.value_ = values

    h.passModel(lp)
    h.run()
    status = h.getModelStatus()
    info = h.getInfo()
    obj = -info.objective_function_value
    bound = -info.mip_dual_bound
    ok = (status == highspy.HighsModelStatus.kOptimal
          and abs(obj - round(obj)) < 1e-6 and round(obj) == expected
          and abs(bound - obj) < 1e-6)
    print(json.dumps({
        "r": r, "k": k, "n": n, "highs_status": str(status),
        "highs_optimum": round(obj), "highs_dual_bound": bound,
        "expected_from_cpsat": expected, "agree": bool(ok),
        "walltime_s": round(time.time() - t0, 2),
    }), flush=True)
    return ok


def main():
    r, k = int(sys.argv[1]), int(sys.argv[2])
    ns = [int(a) for a in sys.argv[3:]]
    results_path = os.path.join(os.path.dirname(__file__), "..", "results", "results.jsonl")
    expected = {}
    with open(results_path) as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("certified_optimal"):
                expected[(rec["r"], rec["k"], rec["n"])] = rec["f"]
    all_ok = True
    for n in ns:
        if (r, k, n) not in expected:
            print(f"SKIP r={r} k={k} n={n}: no certified CP-SAT result", flush=True)
            all_ok = False
            continue
        all_ok &= check(n, r, k, expected[(r, k, n)])
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
