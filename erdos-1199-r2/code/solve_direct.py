#!/usr/bin/env python3
"""Round-2 direct solver for finite Owings instances (n, k=4).

Generates the FULL canonical CNF (no symmetry breaking, no lazy pools) via
round-1's generate_cnf.write_cnf and runs kissat on it with an optional
time cap and an optional --sat/--unsat mode hint.

  SAT   -> model saved as results/witness_k4_n{n}.txt, then INDEPENDENTLY
           re-checked by the clique-based checker (check_coloring.py, which
           shares no code with the CNF generator).  Certifies n(4) > n.
  UNSAT -> certifies n(4) <= n (for a DRAT-certified run use certify.py).

Every solver call is appended to results/search_log.jsonl immediately
(checkpoint discipline: a killed run loses at most the call in flight).

Usage: solve_direct.py n [--mode sat|unsat|default] [--time SECONDS]
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "results")
LOG = os.path.join(RESULTS, "search_log.jsonl")
K = 4

sys.path.insert(0, HERE)
from generate_cnf import write_cnf            # noqa: E402
from check_coloring import find_mono_set      # noqa: E402


def log_entry(entry):
    entry["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def parse_model(stdout, n):
    model = {}
    for line in stdout.splitlines():
        if line.startswith("v "):
            for tok in line[2:].split():
                lit = int(tok)
                if lit:
                    model[abs(lit)] = 1 if lit > 0 else 0
    return [model.get(i, 0) for i in range(1, n + 1)]


def solve(n, mode="default", time_cap=None):
    cnf = os.path.join(RESULTS, f"owings_k{K}_n{n}.cnf")
    t0 = time.time()
    nclauses = write_cnf(n, K, cnf)
    gen_s = time.time() - t0

    cmd = ["kissat", "-q"]
    if mode == "sat":
        cmd.append("--sat")
    elif mode == "unsat":
        cmd.append("--unsat")
    if time_cap:
        cmd.append(f"--time={int(time_cap)}")
    cmd.append(cnf)

    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    solve_s = time.time() - t0

    if proc.returncode == 10:
        colours = parse_model(proc.stdout, n)
        bits = "".join(map(str, colours))
        wit = os.path.join(RESULTS, f"witness_k{K}_n{n}.txt")
        with open(wit, "w") as f:
            f.write(bits + "\n")
        hit = find_mono_set(colours, K)
        recheck = "AVOIDING" if hit is None else f"VIOLATED:{hit}"
        log_entry({"k": K, "n": n, "status": "SAT", "method": "direct-full",
                   "mode": mode, "clauses": nclauses,
                   "gen_seconds": round(gen_s, 3),
                   "solve_seconds": round(solve_s, 3),
                   "witness": os.path.basename(wit),
                   "independent_recheck": recheck,
                   "invocation": " ".join(cmd)})
        if hit is not None:
            raise RuntimeError(f"model FAILED independent recheck: {hit}")
        print(f"n={n}: SAT in {solve_s:.1f}s (recheck AVOIDING) => n(4) > {n}")
        return "SAT"
    if proc.returncode == 20:
        log_entry({"k": K, "n": n, "status": "UNSAT", "method": "direct-full",
                   "mode": mode, "clauses": nclauses,
                   "gen_seconds": round(gen_s, 3),
                   "solve_seconds": round(solve_s, 3),
                   "invocation": " ".join(cmd)})
        print(f"n={n}: UNSAT in {solve_s:.1f}s => n(4) <= {n}")
        return "UNSAT"
    log_entry({"k": K, "n": n, "status": "UNDECIDED", "method": "direct-full",
               "mode": mode, "clauses": nclauses,
               "solve_seconds": round(solve_s, 3),
               "kissat_exit": proc.returncode,
               "invocation": " ".join(cmd)})
    print(f"n={n}: UNDECIDED after {solve_s:.1f}s (exit {proc.returncode})")
    return "UNDECIDED"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--mode", default="default",
                    choices=["sat", "unsat", "default"])
    ap.add_argument("--time", type=float, default=None)
    args = ap.parse_args()
    solve(args.n, args.mode, args.time)
