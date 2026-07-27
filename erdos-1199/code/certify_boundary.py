#!/usr/bin/env python3
"""Produce and verify a DRAT unsatisfiability certificate for the boundary
instance (n, k) with n = n(k), i.e. the least n whose CNF is UNSAT.

Steps: regenerate the CNF deterministically, run kissat writing a DRAT
proof, then verify the proof independently with drat-trim.  Artifacts land
in certificates/k{k}/ and the outcome is appended to results/search_log.jsonl.

Usage: certify_boundary.py k n
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from generate_cnf import write_cnf  # noqa: E402

DRAT_TRIM = os.path.join(ROOT, "tools", "drat-trim", "drat-trim")


def main(k, n):
    cert_dir = os.path.join(ROOT, "certificates", f"k{k}")
    os.makedirs(cert_dir, exist_ok=True)
    cnf = os.path.join(cert_dir, f"owings_k{k}_n{n}.cnf")
    proof = os.path.join(cert_dir, f"owings_k{k}_n{n}.drat")
    nclauses = write_cnf(n, k, cnf)

    t0 = time.time()
    solver = subprocess.run(["kissat", "-q", cnf, proof],
                            capture_output=True, text=True)
    solve_s = time.time() - t0
    if solver.returncode != 20:
        raise RuntimeError(f"expected UNSAT (exit 20), got {solver.returncode}")

    t0 = time.time()
    checker = subprocess.run([DRAT_TRIM, cnf, proof],
                             capture_output=True, text=True)
    check_s = time.time() - t0
    verified = "s VERIFIED" in checker.stdout
    print(checker.stdout.strip().splitlines()[-1])
    entry = {"k": k, "n": n, "event": "drat_certificate",
             "clauses": nclauses,
             "kissat_exit": solver.returncode,
             "kissat_seconds": round(solve_s, 3),
             "drat_trim_verified": verified,
             "drat_trim_seconds": round(check_s, 3),
             "proof_bytes": os.path.getsize(proof),
             "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    with open(os.path.join(ROOT, "results", "search_log.jsonl"), "a") as f:
        f.write(json.dumps(entry) + "\n")
    if not verified:
        raise RuntimeError("drat-trim did NOT verify the proof")
    print(f"certified: every 2-colouring of [1..{n}] contains a {k}-element "
          f"A with A+A monochromatic (proof {os.path.getsize(proof)} bytes, "
          f"verified in {check_s:.2f}s)")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
