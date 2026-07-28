#!/usr/bin/env python3
"""Binary-search driver for one cell N(k,l), using kissat.

Ramp N up while SAT (saving witnesses), then bisect [max-SAT, min-UNSAT].
Finally re-certify the crossover: witness at N*-1 checked independently,
UNSAT at N* with DRAT proof checked by drat-trim.

Every solver call is logged as one JSON line in results/log.jsonl (checkpoint).
Exact invocations recorded. Deterministic: kissat --seed=42, encoder is
deterministic.

Usage: solve_cell.py k l [--start S] [--deadline EPOCH] [--calltime SEC]
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from encode import encode, write_dimacs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KISSAT = "/opt/homebrew/bin/kissat"
DRATTRIM = os.path.join(ROOT, "tools-drat-trim", "drat-trim")
RESULTS = os.path.join(ROOT, "results")
WITNESS = os.path.join(ROOT, "witnesses")
CERTS = os.path.join(ROOT, "certs")
SCRATCH = os.path.join(ROOT, "scratch")
for d in (RESULTS, WITNESS, CERTS, SCRATCH):
    os.makedirs(d, exist_ok=True)


def log(rec):
    rec["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(os.path.join(RESULTS, "log.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")


def run_kissat(cnf, timeout, proof=None):
    cmd = [KISSAT, "--seed=42", f"--time={int(timeout)}", cnf]
    if proof:
        cmd = [KISSAT, "--seed=42", f"--time={int(timeout)}", "--no-binary",
               cnf, proof]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    dt = time.time() - t0
    out = p.stdout
    if p.returncode == 10:
        status = "SAT"
    elif p.returncode == 20:
        status = "UNSAT"
    else:
        status = "UNKNOWN"
    model = None
    if status == "SAT":
        lits = []
        for line in out.splitlines():
            if line.startswith("v "):
                lits.extend(int(x) for x in line[2:].split())
        model = set(x for x in lits if x != 0)
    return status, dt, model, " ".join(cmd)


def solve_at(k, l, N, timeout, proof=None):
    cnf = os.path.join(SCRATCH, f"k{k}l{l}_N{N}.cnf")
    clauses, nvars = encode(N, k, l)
    write_dimacs(cnf, clauses, nvars)
    status, dt, model, cmd = run_kissat(cnf, timeout, proof)
    rec = {"cell": f"N({k},{l})", "N": N, "status": status, "sec": round(dt, 2),
           "vars": nvars, "clauses": len(clauses), "cmd": cmd}
    witness = None
    if status == "SAT" and model is not None:
        witness = "".join("+" if (i in model) else "-" for i in range(1, N + 1))
        wpath = os.path.join(WITNESS, f"k{k}l{l}_N{N}.txt")
        with open(wpath, "w") as f:
            f.write(witness + "\n")
        chk = subprocess.run(
            [sys.executable, os.path.join(ROOT, "code", "check_witness.py"),
             str(k), str(l), witness], capture_output=True, text=True)
        rec["witness_check"] = chk.stdout.strip()
        if chk.returncode != 0:
            rec["witness_check"] = "FAILED: " + chk.stdout + chk.stderr
            log(rec)
            raise RuntimeError(f"witness check failed at N={N}")
    if status != "SAT":
        os.remove(cnf)  # keep scratch lean; cnf regenerable
    log(rec)
    return status, dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("k", type=int)
    ap.add_argument("l", type=int)
    ap.add_argument("--start", type=int, default=None)
    ap.add_argument("--deadline", type=float, default=time.time() + 6600)
    ap.add_argument("--calltime", type=int, default=1200)
    ap.add_argument("--maxn", type=int, default=100000,
                    help="abort ramp if still SAT beyond this N")
    args = ap.parse_args()
    k, l = args.k, args.l
    lo = args.start or k + 1  # will confirm SAT here first
    hi = None

    def budget():
        return min(args.calltime, max(30, args.deadline - time.time()))

    N = lo
    # ramp
    while hi is None:
        if N > args.maxn:
            log({"cell": f"N({k},{l})", "event": "maxn-abort", "N": N,
                 "bracket": [lo, None]})
            return
        if time.time() > args.deadline:
            log({"cell": f"N({k},{l})", "event": "deadline", "phase": "ramp",
                 "bracket": [lo, hi]})
            return
        st, dt = solve_at(k, l, N, budget())
        if st == "SAT":
            lo = N
            N = max(N + 1, int(N * 1.25) + 1)
        elif st == "UNSAT":
            hi = N
        else:
            log({"cell": f"N({k},{l})", "event": "unknown-abort",
                 "phase": "ramp", "N": N, "bracket": [lo, None]})
            return
    # bisect
    while hi - lo > 1:
        if time.time() > args.deadline:
            log({"cell": f"N({k},{l})", "event": "deadline", "phase": "bisect",
                 "bracket": [lo, hi]})
            return
        mid = (lo + hi) // 2
        st, dt = solve_at(k, l, mid, budget())
        if st == "SAT":
            lo = mid
        elif st == "UNSAT":
            hi = mid
        else:
            log({"cell": f"N({k},{l})", "event": "unknown-abort",
                 "phase": "bisect", "N": mid, "bracket": [lo, hi]})
            return
    # certify: UNSAT at hi with DRAT + drat-trim
    proof = os.path.join(CERTS, f"k{k}l{l}_N{hi}.drat")
    cnf = os.path.join(CERTS, f"k{k}l{l}_N{hi}.cnf")
    clauses, nvars = encode(hi, k, l)
    write_dimacs(cnf, clauses, nvars)
    st, dt, model, cmd = run_kissat(cnf, budget(), proof)
    if st != "UNSAT":
        log({"cell": f"N({k},{l})", "event": "certify-fail", "N": hi,
             "status": st, "cmd": cmd})
        return
    t0 = time.time()
    chk = subprocess.run([DRATTRIM, cnf, proof], capture_output=True, text=True)
    verified = "s VERIFIED" in chk.stdout
    log({"cell": f"N({k},{l})", "event": "certified", "value": hi,
         "witness_at": lo, "unsat_at": hi, "kissat_sec": round(dt, 2),
         "drat_trim_sec": round(time.time() - t0, 2),
         "drat_verified": verified, "cmd": cmd,
         "drat_trim_tail": chk.stdout.strip().splitlines()[-3:]})
    subprocess.run(["gzip", "-f", proof])
    print(f"RESULT N({k},{l}) = {hi} (witness at {lo}, drat_verified={verified})")


if __name__ == "__main__":
    main()
