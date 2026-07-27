#!/usr/bin/env python3
"""Resolve the straggler families the C backtracking search left undecided.

Reads every "nongreedy ... code 3 ..." line from results/nN/chunk_*.txt and
solves that family's packing problem exactly with OR-Tools CP-SAT. The top
tree T_n stays fixed in its canonical position (tree vertex i -> board vertex
i; exact symmetry reduction, since Aut(K_n) acts transitively on the copies
of any spanning tree). A found packing is written as a witness line in the
same format the C solver uses, into results/nN/hard/sample_III.txt, so
check_witnesses.py validates these files unchanged. INFEASIBLE would mean a
counterexample to the tree packing conjecture and aborts loudly.

Usage: resolve_hard.py n results_dir trees_dir [time_limit_s_per_family]
Exit codes: 0 all resolved SAT, 2 any infeasible (!), 3 any timeout.
"""

import re
import sys
from pathlib import Path

from ortools.sat.python import cp_model

n = int(sys.argv[1])
results_dir = Path(sys.argv[2])
trees_dir = Path(sys.argv[3])
time_limit = float(sys.argv[4]) if len(sys.argv) > 4 else 300.0

DIGITS = "0123456789ab"
m = n * (n - 1) // 2
board_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
edge_id = {e: i for i, e in enumerate(board_edges)}

trees = {}
for k in range(2, n + 1):
    trees[k] = [
        list(map(int, line.split()))
        for line in (trees_dir / f"trees_{k:02d}.txt").read_text().splitlines()
    ]

hard = []  # (chunk_index, family_counter, [idx at sizes n-1..2])
for chunk_path in sorted(results_dir.glob("chunk_*.txt")):
    chunk_index = int(chunk_path.stem.split("_")[1])
    for line in chunk_path.read_text().splitlines():
        mm = re.match(r"nongreedy (\d+) code 3 family((?: \d+)+)$", line)
        if mm:
            hard.append((chunk_index, int(mm.group(1)), list(map(int, mm.group(2).split()))))

print(f"undecided families to resolve: {len(hard)}")

def solve_family(top_index: int, idxs: list[int]):
    """Return per-edge size labels for a packing, or 'infeasible'/'timeout'."""
    family = {n: top_index}
    for j, k in enumerate(range(n - 1, 1, -1)):
        family[k] = idxs[j]

    model = cp_model.CpModel()
    # canonical top tree occupies fixed edges
    top_parents = trees[n][top_index]
    top_used = set()
    for child, parent in enumerate(top_parents, start=1):
        top_used.add(edge_id[(min(parent, child), max(parent, child))])

    # z[(k, t, e)] <=> tree k's t-th edge is placed on board edge e
    edge_users = {e: [] for e in range(m)}
    for k in range(2, n):
        parents = trees[k][family[k]]
        x = [model.NewIntVar(0, n - 1, f"x{k}_{v}") for v in range(k)]
        model.AddAllDifferent(x)
        for t, parent in enumerate(parents):
            child = t + 1
            lits = []
            for e, (a, b) in enumerate(board_edges):
                if e in top_used:
                    continue
                z = model.NewBoolVar(f"z{k}_{t}_{e}")
                fwd = model.NewBoolVar("")
                rev = model.NewBoolVar("")
                model.Add(x[parent] == a).OnlyEnforceIf(fwd)
                model.Add(x[child] == b).OnlyEnforceIf(fwd)
                model.Add(x[parent] == b).OnlyEnforceIf(rev)
                model.Add(x[child] == a).OnlyEnforceIf(rev)
                model.AddBoolOr([fwd, rev]).OnlyEnforceIf(z)
                model.AddImplication(fwd, z)
                model.AddImplication(rev, z)
                lits.append(z)
                edge_users[e].append((z, k))
            model.AddExactlyOne(lits)  # each tree edge lands somewhere
    for e in range(m):
        if e in top_used:
            continue
        model.AddExactlyOne([z for z, _ in edge_users[e]])

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = 4
    solver.parameters.random_seed = 743
    status = solver.Solve(model)
    if status == cp_model.INFEASIBLE:
        return "infeasible"
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return "timeout"
    labels = [0] * m
    for e in top_used:
        labels[e] = n
    for e in range(m):
        if e in top_used:
            continue
        winners = [k for z, k in edge_users[e] if solver.Value(z)]
        assert len(winners) == 1, (e, winners)
        labels[e] = winners[0]
    return labels


hard_dir = results_dir / "hard"
hard_dir.mkdir(exist_ok=True)
by_chunk = {}
any_infeasible = any_timeout = False
for chunk_index, fam_counter, idxs in hard:
    res = solve_family(chunk_index, idxs)
    if res == "infeasible":
        any_infeasible = True
        print(f"*** INFEASIBLE: chunk {chunk_index} family {fam_counter} {idxs} — "
              f"COUNTEREXAMPLE CANDIDATE, verify independently! ***")
        continue
    if res == "timeout":
        any_timeout = True
        print(f"timeout: chunk {chunk_index} family {fam_counter} {idxs}")
        continue
    line = (f"{fam_counter} 1 " + " ".join(map(str, idxs)) + "  "
            + "".join(DIGITS[k] for k in res))
    by_chunk.setdefault(chunk_index, []).append(line)
    print(f"resolved: chunk {chunk_index} family {fam_counter} -> packing found")

for chunk_index, lines in sorted(by_chunk.items()):
    (hard_dir / f"sample_{chunk_index:03d}.txt").write_text("\n".join(lines) + "\n")

print(f"resolved {sum(len(v) for v in by_chunk.values())}/{len(hard)} "
      f"(infeasible: {any_infeasible}, timeouts: {any_timeout})")
sys.exit(2 if any_infeasible else 3 if any_timeout else 0)
