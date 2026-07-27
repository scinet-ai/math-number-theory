#!/usr/bin/env python3
"""Determine n(k) = least n such that every 2-colouring of {1,...,n}
contains a k-element A with A+A monochromatic (doubles included).

Strategy: the avoidance property is monotone (a colouring of [n] that avoids
monochromatic A+A restricts to one of [n-1]), so SAT at n implies SAT below
and UNSAT at n implies UNSAT above.  We probe upward from n = 2k by doubling
until the first UNSAT, then binary-search the boundary.

Every kissat invocation, result, and timing is appended to
results/search_log.jsonl so partial sweeps are banked and resumable.
SAT models are saved as witness colourings and immediately re-checked with
the independent checker (check_coloring.py).  The boundary UNSAT instance is
re-run with DRAT proof output and verified by drat-trim in a separate step
(certify_boundary.py) to keep this driver fast.

Usage: search_thresholds.py k [n_cap]
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "results")
LOG = os.path.join(RESULTS, "search_log.jsonl")
KISSAT = "kissat"

sys.path.insert(0, HERE)
from generate_cnf import write_cnf  # noqa: E402
from check_coloring import find_mono_set  # noqa: E402


def log_entry(entry):
    entry["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def load_known(k):
    """Recover already-decided n values for this k from the log."""
    known = {}
    if os.path.exists(LOG):
        for line in open(LOG):
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("k") == k and e.get("status") in ("SAT", "UNSAT"):
                known[e["n"]] = e["status"]
    return known


def solve(n, k, known):
    """Run kissat on instance (n,k); return 'SAT' or 'UNSAT'. Cached via log."""
    if n in known:
        return known[n]
    cnf = os.path.join(RESULTS, f"owings_k{k}_n{n}.cnf")
    t0 = time.time()
    nclauses = write_cnf(n, k, cnf)
    gen_s = time.time() - t0
    t0 = time.time()
    proc = subprocess.run([KISSAT, "-q", cnf], capture_output=True, text=True)
    solve_s = time.time() - t0
    if proc.returncode == 10:
        status = "SAT"
        model = {}
        for line in proc.stdout.splitlines():
            if line.startswith("v "):
                for tok in line[2:].split():
                    lit = int(tok)
                    if lit != 0:
                        model[abs(lit)] = 1 if lit > 0 else 0
        bits = "".join(str(model.get(i, 0)) for i in range(1, n + 1))
        wit = os.path.join(RESULTS, f"witness_k{k}_n{n}.txt")
        with open(wit, "w") as f:
            f.write(bits + "\n")
        colours = [int(ch) for ch in bits]
        recheck = find_mono_set(colours, k)
        if recheck is not None:
            raise RuntimeError(
                f"model for n={n} k={k} FAILED independent recheck: {recheck}")
        log_entry({"k": k, "n": n, "status": status, "clauses": nclauses,
                   "gen_seconds": round(gen_s, 3),
                   "solve_seconds": round(solve_s, 3),
                   "witness": os.path.basename(wit),
                   "independent_recheck": "AVOIDING"})
    elif proc.returncode == 20:
        status = "UNSAT"
        log_entry({"k": k, "n": n, "status": status, "clauses": nclauses,
                   "gen_seconds": round(gen_s, 3),
                   "solve_seconds": round(solve_s, 3)})
    else:
        raise RuntimeError(f"kissat exit {proc.returncode} on {cnf}")
    known[n] = status
    # keep the CNF only around the eventual boundary; delete big SAT ones later
    print(f"  k={k} n={n}: {status} "
          f"({nclauses} clauses, {solve_s:.2f}s solve)", flush=True)
    return status


def find_threshold(k, n_cap):
    known = load_known(k)
    lo = 2 * k          # smallest n with any valid A at all; SAT for k >= 2
    if solve(lo, k, known) == "UNSAT":
        raise RuntimeError(f"unexpected UNSAT at minimal n={lo}")
    hi = None
    n = lo
    while hi is None:
        n = min(2 * n, n_cap) if n < n_cap else n_cap
        st = solve(n, k, known)
        if st == "UNSAT":
            hi = n
        else:
            lo = n
            if n >= n_cap:
                print(f"k={k}: still SAT at cap n={n_cap}; n({k}) > {n_cap}")
                log_entry({"k": k, "event": "cap_reached", "cap": n_cap,
                           "conclusion": f"n({k}) > {n_cap}"})
                return None
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if solve(mid, k, known) == "UNSAT":
            hi = mid
        else:
            lo = mid
    print(f"n({k}) = {hi}  (SAT witness at {lo}, UNSAT at {hi})")
    log_entry({"k": k, "event": "threshold", "n_of_k": hi,
               "sat_below": lo})
    return hi


if __name__ == "__main__":
    k = int(sys.argv[1])
    n_cap = int(sys.argv[2]) if len(sys.argv) > 2 else 4096
    os.makedirs(RESULTS, exist_ok=True)
    find_threshold(k, n_cap)
