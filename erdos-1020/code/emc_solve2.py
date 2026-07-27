#!/usr/bin/env python3
"""
Improved lazy-constraint solver for f(n;r,k) — same exact model as
emc_solve.py (shifted/down-closed reduction + k-block r-partitions of [rk]),
but with a DIVERSIFIED cut separation designed for large partition spaces
(r=4, k=5 has ~2.55e9 partitions; the v1 lexicographic-DFS-with-cap
separation added 200k highly-correlated cuts per round and never converged).

Changes vs emc_solve.py:
  1. Round-0 injection of `--init-rand` uniformly random partition
     constraints (every partition constraint is valid a priori).
  2. Per-round separation = complete bitmask enumeration of violated
     partitions with support pruning + min-support pivoting (find_viol,
     shuffled adjacency for cut diversity), merged with cheap uniform
     random sampling; batches capped (default 40k) so re-solves stay fast.
  3. Per-round checkpoint line (JSON) with the round's proven relaxation
     optimum — a certified UPPER bound on f(n;r,k) even if killed mid-run.

Certification criterion: CP-SAT status OPTIMAL *and* the deterministic
complete search (find_viol with cap=1, rng=None — support pruning only
discards branches that provably cannot complete a partition) finds no
partition of [rk] inside the incumbent.

Determinism: fixed RNG seed (--seed, default 0) drives all sampling;
CP-SAT random_seed fixed; workers fixed.

Usage: emc_solve2.py R K N [N2 ...] [--time-limit S] [--workers W]
                     [--init-rand M] [--batch B] [--seed S] [--outdir DIR]
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ortools.sat.python import cp_model

from emc_solve import (C, conjectured, rsets, shift_covers,
                       count_partitions)


def canon(p):
    return tuple(sorted(tuple(sorted(b)) for b in p))


def random_partition(rk, r, rng):
    xs = list(range(1, rk + 1))
    rng.shuffle(xs)
    return canon(xs[i:i + r] for i in range(0, rk, r))


def find_viol(selected, r, k, cap, rng=None):
    """Complete search for partitions of [rk] into k r-blocks all lying in
    `selected`; returns up to `cap` of them (empty list == none exist).

    Bitmask DFS with two exactness-preserving accelerations:
      - support pruning: a branch dies as soon as some uncovered element is
        contained in no available block inside the uncovered set (such a
        branch can never complete a partition);
      - min-support pivot: branch on the uncovered element with the fewest
        available blocks (each partition of the uncovered set has exactly
        one block through the pivot, so nothing is enumerated twice).
    `rng` (optional) shuffles adjacency lists for cut diversity; rng=None is
    fully deterministic and is what the certification path uses.
    """
    rk = r * k
    full = (1 << rk) - 1
    by_elem = {u: [] for u in range(1, rk + 1)}
    mask_to_block = {}
    for A in selected:
        if A[-1] <= rk:
            m = 0
            for v in A:
                m |= 1 << (v - 1)
            mask_to_block[m] = A
            for v in A:
                by_elem[v].append(m)
    if rng is not None:
        for lst in by_elem.values():
            rng.shuffle(lst)
    found = []

    def transversal_prune(U, needed, avail_by_elem):
        """Greedy small-transversal (pigeonhole) prune. If some set T of
        elements with |T| < needed hits EVERY available block, then at most
        |T| pairwise disjoint blocks exist inside U — a partition needing
        `needed` blocks is impossible. Greedy failure to conclude => no
        prune (never unsound)."""
        blocks = set()
        for lst in avail_by_elem.values():
            blocks.update(lst)
        tsize = 0
        while blocks and tsize < needed:
            # element of U hitting the most remaining blocks
            cnt = {}
            for bm in blocks:
                mm = bm
                while mm:
                    low = mm & -mm
                    cnt[low] = cnt.get(low, 0) + 1
                    mm ^= low
            e = max(cnt, key=cnt.get)
            blocks = {bm for bm in blocks if not (bm & e)}
            tsize += 1
        return not blocks and tsize < needed

    def rec(U, acc, depth):
        if len(found) >= cap:
            return
        if U == 0:
            found.append(canon(mask_to_block[m] for m in acc))
            return
        # support check on every uncovered element (scarce, high elements
        # first); remember the pivot with fewest available blocks
        best_avail = None
        avail_by_elem = {}
        for u in range(rk, 0, -1):
            if not (U >> (u - 1)) & 1:
                continue
            avail = [bm for bm in by_elem[u] if not (bm & ~U)]
            if not avail:
                return  # prune: u can never be covered
            avail_by_elem[u] = avail
            if best_avail is None or len(avail) < len(best_avail):
                best_avail = avail
        # pigeonhole prune at shallow depths (cheap where it matters:
        # cover-family-like incumbents die at the root)
        if depth <= 2:
            needed = bin(U).count("1") // r
            if transversal_prune(U, needed, avail_by_elem):
                return
        for bm in best_avail:
            acc.append(bm)
            rec(U & ~bm, acc, depth + 1)
            acc.pop()
            if len(found) >= cap:
                return

    rec(full, [], 0)
    return found


def solve_cell(n, r, k, time_limit, outdir, seed=0, workers=3,
               init_rand=120_000, batch=40_000):
    t0 = time.time()
    rng = random.Random(seed)
    conj, cand_clique, cand_cover = conjectured(n, r, k)
    sets = rsets(n, r)
    idx = {A: i for i, A in enumerate(sets)}
    nparts_total = count_partitions(r * k, r)

    model = cp_model.CpModel()
    x = [model.new_bool_var(f"x{i}") for i in range(len(sets))]
    nshift = 0
    for A in sets:
        for B in shift_covers(A):
            model.add_implication(x[idx[A]], x[idx[B]])
            nshift += 1

    added = set()

    def add_parts(parts):
        cnt = 0
        for p in parts:
            key = canon(p)
            if key in added:
                continue
            added.add(key)
            model.add_bool_or([x[idx[B]].Not() for B in key])
            cnt += 1
        return cnt

    # round-0 injection: uniform random partitions (valid constraints a priori)
    target = min(init_rand, nparts_total // 2)
    while len(added) < target:
        add_parts([random_partition(r * k, r, rng)])

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
    prog_path = os.path.join(outdir, f"progress_r{r}_k{k}_n{n}.jsonl")

    rounds = 0
    status = None
    while True:
        rounds += 1
        solver.parameters.max_time_in_seconds = max(
            5.0, time_limit - (time.time() - t0))
        status = solver.solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            break
        selected = {A for A in sets if solver.value(x[idx[A]])}
        # checkpoint: this round's relaxation optimum is a certified upper
        # bound on f(n;r,k) whenever status == OPTIMAL.
        with open(prog_path, "a") as pf:
            pf.write(json.dumps({
                "round": rounds, "n_constraints": len(added),
                "status": solver.status_name(status),
                "relaxation_optimum": int(solver.objective_value),
                "upper_bound_on_f": (int(solver.objective_value)
                                     if status == cp_model.OPTIMAL else None),
                "elapsed_s": round(time.time() - t0, 1)}) + "\n")
        if status != cp_model.OPTIMAL or time.time() - t0 > time_limit:
            break
        # --- separation: complete pruned enumeration, shuffled for diversity
        selset = {A for A in selected if A[-1] <= r * k}
        viol = set(find_viol(selected, r, k, cap=batch, rng=rng))
        # plus cheap uniform random sampling for global coverage
        hits = 0
        for _ in range(100_000):
            p = random_partition(r * k, r, rng)
            if all(b in selset for b in p):
                viol.add(p)
                hits += 1
                if hits > batch // 4:
                    break
        if not viol:
            break
        add_parts(viol)

    wall = time.time() - t0
    status_name = solver.status_name(status)
    obj = int(solver.objective_value) if status in (
        cp_model.OPTIMAL, cp_model.FEASIBLE) else None
    bound = int(solver.best_objective_bound) if status in (
        cp_model.OPTIMAL, cp_model.FEASIBLE) else None
    selected = sorted(A for A in sets if solver.value(x[idx[A]])) \
        if obj is not None else []
    certified = (status == cp_model.OPTIMAL and obj is not None
                 and not find_viol(set(selected), r, k, cap=1, rng=None))

    rec = {
        "r": r, "k": k, "n": n,
        "status": status_name, "certified_optimal": bool(certified),
        "f": obj, "upper_bound": bound,
        "conjectured": conj, "cand_clique": cand_clique,
        "cand_cover": cand_cover,
        "matches_conjecture": (obj == conj and certified)
        if obj is not None else None,
        "n_vars": len(sets), "n_shift_constraints": nshift,
        "n_matching_constraints": len(added),
        "matching_mode": "lazy-diversified",
        "n_partitions_total": nparts_total,
        "lazy_rounds": rounds, "walltime_s": round(wall, 2),
        "solver": "ortools-cpsat", "workers": workers, "seed": seed,
        "solver_code": "emc_solve2.py",
    }
    with open(os.path.join(outdir, f"sol_r{r}_k{k}_n{n}.json"), "w") as f:
        json.dump({"r": r, "k": k, "n": n, "f": obj,
                   "family": [list(A) for A in selected]}, f)
    with open(os.path.join(outdir, "results.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec), flush=True)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("r", type=int)
    ap.add_argument("k", type=int)
    ap.add_argument("ns", type=int, nargs="+")
    ap.add_argument("--time-limit", type=float, default=2400.0)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--init-rand", type=int, default=120_000)
    ap.add_argument("--batch", type=int, default=40_000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--outdir",
                    default=os.path.join(os.path.dirname(
                        os.path.abspath(__file__)), "..", "results"))
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    for n in args.ns:
        solve_cell(n, args.r, args.k, args.time_limit, args.outdir,
                   seed=args.seed, workers=args.workers,
                   init_rand=args.init_rand, batch=args.batch)


if __name__ == "__main__":
    main()
