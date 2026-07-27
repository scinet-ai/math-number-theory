"""Incremental exact computation of S(N) = A390813(N) for Erdos #773.

Key fact: S(N) in {S(N-1), S(N-1)+1}, and S(N) = S(N-1)+1 iff there is a
square-Sidon subset of {1..N} (roots) of size S(N-1)+1 containing root N
(any such subset must contain N, else it would live in {1..N-1} and
contradict maximality of S(N-1)).

So each level N is ONE decision problem:
    exists A subseteq {1..N}, |A| = S(N-1)+1, N in A, A square-Sidon?
SAT  -> S(N) = S(N-1)+1 (witness recorded, independently re-verified)
UNSAT-> S(N) = S(N-1)   (CP-SAT infeasibility = optimality certificate;
                          re-certified later via kissat DRAT, see cert.py)

Checkpoints: one JSON line per level appended to results/chain.jsonl.
Restart-safe: resumes from the last completed level.

Usage: chain.py --max-n 250 --deadline-min 90 [--start-fresh]
"""

import argparse, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sidon_common import collision_clauses, is_square_sidon
from ortools.sat.python import cp_model

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "results", "chain.jsonl")
SEED = 773
WORKERS = 3
TIME_LADDER = [30.0, 120.0, 600.0, 1800.0]


def load_state():
    """Return (records, S_values dict, witness dict) from checkpoint file."""
    recs = []
    if os.path.exists(RESULTS):
        with open(RESULTS) as f:
            for line in f:
                line = line.strip()
                if line:
                    recs.append(json.loads(line))
    return recs


def try_heuristic_extend(N, t, prev_witness, clauses_N):
    """Cheap SAT-side shortcuts: extend/patch prev witness to size t incl. N.
    Returns witness list or None. Exact arithmetic checks only."""
    base = list(prev_witness)
    # direct extension only; anything subtler is left to CP-SAT (fast on SAT)
    cand = sorted(base + [N])
    if len(cand) == t and is_square_sidon(cand):
        return cand
    return None


def cpsat_decide(N, t, clauses, time_limit):
    """Decision: exists square-Sidon subset of roots {1..N}, size>=t, N in it.
    Returns (status_str, witness_or_None, wall, conflicts)."""
    m = cp_model.CpModel()
    x = [None] + [m.NewBoolVar(f"x{i}") for i in range(1, N + 1)]
    for cl in clauses:
        m.AddBoolOr([x[i].Not() for i in cl])
    m.Add(sum(x[1:]) >= t)
    m.Add(x[N] == 1)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = WORKERS
    solver.parameters.random_seed = SEED
    solver.parameters.max_time_in_seconds = time_limit
    t0 = time.time()
    st = solver.Solve(m)
    wall = time.time() - t0
    if st == cp_model.FEASIBLE or st == cp_model.OPTIMAL:
        wit = sorted(i for i in range(1, N + 1) if solver.Value(x[i]))
        return "SAT", wit, wall, solver.NumConflicts()
    if st == cp_model.INFEASIBLE:
        return "UNSAT", None, wall, solver.NumConflicts()
    return "UNKNOWN", None, wall, solver.NumConflicts()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=250)
    ap.add_argument("--deadline-min", type=float, default=90.0)
    ap.add_argument("--start-fresh", action="store_true")
    args = ap.parse_args()

    deadline = time.time() + args.deadline_min * 60.0
    if args.start_fresh and os.path.exists(RESULTS):
        os.remove(RESULTS)
    recs = load_state()
    if recs:
        S_prev = recs[-1]["S"]
        witness = recs[-1]["witness"]
        n_start = recs[-1]["n"] + 1
    else:
        # base case N=1: S(1)=1, witness {1}
        with open(RESULTS, "a") as f:
            f.write(json.dumps({"n": 1, "S": 1, "step": "base",
                                "witness": [1], "wall": 0.0}) + "\n")
        S_prev, witness, n_start = 1, [1], 2

    for N in range(n_start, args.max_n + 1):
        if time.time() > deadline:
            print(f"[chain] deadline reached before N={N}; stopping cleanly",
                  flush=True)
            break
        t = S_prev + 1
        cl = collision_clauses(N)
        t0 = time.time()
        rec = {"n": N, "target": t, "n_clauses": len(cl)}
        wit = try_heuristic_extend(N, t, witness, cl)
        if wit is not None:
            assert len(wit) == t and wit[-1] == N and is_square_sidon(wit)
            S_prev, witness = t, wit
            rec.update({"S": t, "step": "heuristic-sat", "witness": wit,
                        "wall": round(time.time() - t0, 3)})
        else:
            status, w, wall, confl = None, None, 0.0, 0
            for lim in TIME_LADDER:
                remaining = deadline - time.time()
                if remaining <= 5:
                    status = "DEADLINE"
                    break
                status, w, wall, confl = cpsat_decide(
                    N, t, cl, min(lim, max(5.0, remaining)))
                if status != "UNKNOWN":
                    break
            if status == "SAT":
                assert len(w) >= t and N in w and is_square_sidon(w)
                w = sorted(w)[:]
                S_prev, witness = len(w), w
                rec.update({"S": len(w), "step": "cpsat-sat", "witness": w,
                            "wall": round(time.time() - t0, 3),
                            "conflicts": confl})
            elif status == "UNSAT":
                rec.update({"S": S_prev, "step": "cpsat-unsat",
                            "witness": witness,
                            "wall": round(time.time() - t0, 3),
                            "conflicts": confl})
            else:
                print(f"[chain] N={N} unresolved ({status}); stopping",
                      flush=True)
                break
        with open(RESULTS, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"[chain] N={N} S={rec['S']} {rec['step']} "
              f"wall={rec['wall']}s", flush=True)
    print("[chain] done", flush=True)


if __name__ == "__main__":
    main()
