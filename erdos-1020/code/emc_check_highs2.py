#!/usr/bin/env python3
"""
Independent HiGHS cross-check for cells whose full partition-constraint set
is too large to enumerate (r=4, k=5 has ~2.55e9 partitions).

Logic: any set of partition constraints is a valid RELAXATION, so any
proven optimum of the relaxed MIP is a certified upper bound on f(n;r,k).
We build the relaxation from `--sample M` uniformly random partitions drawn
with an independent seed (default 12345 != the CP-SAT run's seed 0), plus
the exact shift (down-closure) implications, and solve with HiGHS to proven
optimality (mip_rel_gap = mip_abs_gap = 0).

If the HiGHS relaxation optimum EQUALS the recorded f — whose lower bound
verify.py certifies directly from the stored edge list, with no solver and
no shifting assumption — then f is pinned from both sides by two different
solvers on independently sampled models. Exit nonzero otherwise.

Usage: emc_check_highs2.py R K N [N2 ...] [--sample M] [--seed S]
"""
import argparse
import json
import os
import random
import sys
import time
from itertools import combinations

import highspy


def random_partition(rk, r, rng):
    xs = list(range(1, rk + 1))
    rng.shuffle(xs)
    return tuple(sorted(tuple(sorted(xs[i:i + r])) for i in range(0, rk, r)))


def check(n, r, k, expected, sample, seed, warmstart=False):
    t0 = time.time()
    rng = random.Random(seed)
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
    lp.col_cost_ = [-1.0] * nv
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

    for B in sets:
        sB = set(B)
        for i, b in enumerate(B):
            if b - 1 >= 1 and (b - 1) not in sB:
                A = tuple(sorted(B[:i] + (b - 1,) + B[i + 1:]))
                add_row([idx[B], idx[A]], [1.0, -1.0], -inf, 0.0)

    parts = set()
    while len(parts) < sample:
        parts.add(random_partition(r * k, r, rng))
    for p in parts:
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
    if warmstart:
        # MIP start from the stored (independently verified) family; only
        # the DUAL side (the upper-bound proof) is then HiGHS's own work.
        sol_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "results", f"sol_r{r}_k{k}_n{n}.json")
        fam = {tuple(sorted(e))
               for e in json.load(open(sol_path))["family"]}
        vals = [1.0 if A in fam else 0.0 for A in sets]
        sol = highspy.HighsSolution()
        sol.col_value = vals
        h.setSolution(sol)
    h.run()
    status = h.getModelStatus()
    info = h.getInfo()
    obj = -info.objective_function_value
    ok = (status == highspy.HighsModelStatus.kOptimal
          and abs(obj - round(obj)) < 1e-6 and round(obj) == expected)
    print(json.dumps({
        "r": r, "k": k, "n": n, "mode": f"sampled-relaxation({sample},seed={seed})",
        "highs_status": str(status), "highs_relaxation_optimum": round(obj),
        "expected_f": expected,
        "upper_bound_matches_f": bool(ok),
        "walltime_s": round(time.time() - t0, 2),
    }), flush=True)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("r", type=int)
    ap.add_argument("k", type=int)
    ap.add_argument("ns", type=int, nargs="+")
    ap.add_argument("--sample", type=int, default=120_000)
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--warmstart", action="store_true")
    args = ap.parse_args()
    results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "results", "results.jsonl")
    expected = {}
    with open(results_path) as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("certified_optimal"):
                expected[(rec["r"], rec["k"], rec["n"])] = rec["f"]
    all_ok = True
    for n in args.ns:
        if (args.r, args.k, n) not in expected:
            print(f"SKIP r={args.r} k={args.k} n={n}: no certified result",
                  flush=True)
            all_ok = False
            continue
        all_ok &= check(n, args.r, args.k, expected[(args.r, args.k, n)],
                        args.sample, args.seed, warmstart=args.warmstart)
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
