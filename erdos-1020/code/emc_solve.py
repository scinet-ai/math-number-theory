#!/usr/bin/env python3
"""
Exact computation of f(n; r, k) = max #edges of an r-uniform hypergraph on n
vertices with NO k pairwise disjoint edges (Erdos matching conjecture, #1020).

Method (exact, certified):
  1. WLOG the extremal family is *shifted* (stable): (i,j)-shifts preserve the
     number of edges and never increase the matching number (Frankl 1987,
     "The shifting technique in extremal set theory"). A family is shifted iff
     it is down-closed in the coordinatewise domination order on sorted r-sets.
  2. For a down-closed family F, F contains k pairwise disjoint edges  <=>
     F contains k pairwise disjoint edges partitioning [rk].
     Proof (descent): given disjoint A_1..A_k with union U, if some u in U has
     u-1 >= 1 and u-1 not in U, replace u by u-1 (stays a valid r-set, stays
     pairwise disjoint, stays in F by down-closure, total sum decreases).
     At termination every u in U with u > 1 has u-1 in U, so U = [rk].
  3. Hence f(n;r,k) = max sum(x_A) over 0/1 x indexed by r-subsets of [n] s.t.
       (shift)  x_A >= x_B whenever A is obtained from B by decrementing one
                element (cover relations generate the domination order), and
       (match)  for every partition of [rk] into k r-blocks B_1..B_k:
                x_{B_1} + ... + x_{B_k} <= k-1.
     This integer program is solved to proven optimality by CP-SAT (and
     independently cross-checked with HiGHS via emc_check_highs.py).

Deterministic: fixed seeds, fixed worker count (3 = machine budget cap).
Checkpointing: one JSON line appended to results/results.jsonl per finished
cell; full 0/1 solution written per cell.

Usage: emc_solve.py R K N [N2 ...] [--time-limit S] [--lazy] [--outdir DIR]
"""
import argparse
import json
import math
import os
import sys
import time
from itertools import combinations

from ortools.sat.python import cp_model

C = math.comb


def conjectured(n, r, k):
    a = C(r * k - 1, r)
    b = C(n, r) - C(n - k + 1, r)
    return max(a, b), a, b


def rsets(n, r):
    return list(combinations(range(1, n + 1), r))


def shift_covers(A):
    """Sets A' <= A obtained by decrementing one element of A (cover moves)."""
    out = []
    s = set(A)
    for i, a in enumerate(A):
        if a - 1 >= 1 and (a - 1) not in s:
            B = A[:i] + (a - 1,) + A[i + 1:]
            out.append(tuple(sorted(B)))
    return out


def partitions_into_blocks(universe, r):
    """All partitions of `universe` (a sorted tuple) into blocks of size r.
    Canonical: each block starts with the smallest uncovered element."""
    universe = tuple(universe)
    if not universe:
        yield ()
        return
    first, rest = universe[0], universe[1:]
    for others in combinations(rest, r - 1):
        block = (first,) + others
        remaining = tuple(x for x in rest if x not in set(others))
        for tail in partitions_into_blocks(remaining, r):
            yield (block,) + tail


def count_partitions(rk, r):
    k = rk // r
    total = 1
    left = rk
    for _ in range(k):
        total *= C(left - 1, r - 1)
        left -= r
    return total


def find_violated_partitions(selected, r, k, cap):
    """DFS: partitions of [rk] into k r-blocks all of which lie in `selected`
    (a set of sorted tuples). Yields up to `cap` violated partitions."""
    rk = r * k
    found = []
    inside = [A for A in selected if A[-1] <= rk]
    by_min = {}
    for A in inside:
        by_min.setdefault(A[0], []).append(A)

    def rec(uncovered, acc):
        if len(found) >= cap:
            return
        if not uncovered:
            found.append(tuple(acc))
            return
        first = min(uncovered)
        for A in by_min.get(first, ()):
            if all(x in uncovered for x in A):
                acc.append(A)
                rec(uncovered - set(A), acc)
                acc.pop()
                if len(found) >= cap:
                    return

    rec(frozenset(range(1, rk + 1)), [])
    return found


def solve_cell(n, r, k, time_limit, lazy, outdir, seed=0, workers=3):
    t0 = time.time()
    conj, cand_clique, cand_cover = conjectured(n, r, k)
    sets = rsets(n, r)
    idx = {A: i for i, A in enumerate(sets)}
    nparts_total = count_partitions(r * k, r)

    model = cp_model.CpModel()
    x = [model.new_bool_var(f"x{i}") for i in range(len(sets))]

    # shift (down-closure) implications
    nshift = 0
    for A in sets:
        for B in shift_covers(A):
            model.add_implication(x[idx[A]], x[idx[B]])
            nshift += 1

    # matching constraints
    added = set()

    def add_partition_constraints(parts):
        cnt = 0
        for p in parts:
            key = tuple(sorted(p))
            if key in added:
                continue
            added.add(key)
            model.add_bool_or([x[idx[B]].Not() for B in p])
            cnt += 1
        return cnt

    use_lazy = lazy or nparts_total > 400_000
    if not use_lazy:
        add_partition_constraints(partitions_into_blocks(tuple(range(1, r * k + 1)), r))

    # objective + hint (cover family if it wins, else clique on [rk-1])
    model.maximize(sum(x))
    if cand_cover >= cand_clique:
        hintset = {A for A in sets if A[0] <= k - 1}
    else:
        hintset = {A for A in sets if A[-1] <= r * k - 1}
    for A in sets:
        model.add_hint(x[idx[A]], 1 if A in hintset else 0)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed
    solver.parameters.max_time_in_seconds = time_limit
    log_path = os.path.join(outdir, f"log_r{r}_k{k}_n{n}.txt")

    rounds = 0
    status = None
    while True:
        rounds += 1
        with open(log_path, "a") as lf:
            lf.write(f"\n===== round {rounds} constraints={len(added) if use_lazy else 'all'} =====\n")
        solver.parameters.max_time_in_seconds = max(5.0, time_limit - (time.time() - t0))
        status = solver.solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            break
        selected = {A for A in sets if solver.value(x[idx[A]])}
        viol = find_violated_partitions(selected, r, k, cap=int(os.environ.get("EMC_SEP_CAP", "200000")))
        if not viol:
            break
        add_partition_constraints(viol)
        # re-hint with current best known feasible (the cover family)
        if status != cp_model.OPTIMAL or time.time() - t0 > time_limit:
            break

    wall = time.time() - t0
    status_name = solver.status_name(status)
    obj = int(solver.objective_value) if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None
    bound = int(solver.best_objective_bound) if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None
    selected = sorted(A for A in sets if solver.value(x[idx[A]])) if obj is not None else []
    # certified only if solver proved optimality AND no violated partition remains
    certified = (status == cp_model.OPTIMAL and obj is not None
                 and not find_violated_partitions(set(selected), r, k, cap=1))

    rec = {
        "r": r, "k": k, "n": n,
        "status": status_name, "certified_optimal": bool(certified),
        "f": obj, "upper_bound": bound,
        "conjectured": conj, "cand_clique": cand_clique, "cand_cover": cand_cover,
        "matches_conjecture": (obj == conj and certified) if obj is not None else None,
        "n_vars": len(sets), "n_shift_constraints": nshift,
        "n_matching_constraints": len(added) if use_lazy else nparts_total,
        "matching_mode": "lazy" if use_lazy else "full",
        "lazy_rounds": rounds,
        "walltime_s": round(wall, 2),
        "solver": f"ortools-cpsat", "workers": workers, "seed": seed,
    }
    sol_path = os.path.join(outdir, f"sol_r{r}_k{k}_n{n}.json")
    with open(sol_path, "w") as f:
        json.dump({"r": r, "k": k, "n": n, "f": obj, "family": [list(A) for A in selected]}, f)
    with open(os.path.join(outdir, "results.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec), flush=True)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("r", type=int)
    ap.add_argument("k", type=int)
    ap.add_argument("ns", type=int, nargs="+")
    ap.add_argument("--time-limit", type=float, default=600.0)
    ap.add_argument("--lazy", action="store_true")
    ap.add_argument("--outdir", default=os.path.join(os.path.dirname(__file__), "..", "results"))
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    for n in args.ns:
        solve_cell(n, args.r, args.k, args.time_limit, args.lazy, args.outdir)


if __name__ == "__main__":
    main()
