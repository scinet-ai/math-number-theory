#!/usr/bin/env python3
"""Produce and verify a DRAT unsatisfiability certificate for instance (n, 4)
over the FULL canonical CNF (no symmetry breaking) — the certificate then
covers all 2-colourings of [1..n] with no side argument.

Steps: regenerate the CNF deterministically, run kissat writing a DRAT
proof, verify with drat-trim, record sha256+size of both files, and (by
default) delete the proof if it exceeds --keep-mb, keeping the verification
log as evidence plus deterministic regeneration.

Usage: certify.py n [--time SECONDS] [--keep-mb MB]
"""
import argparse
import hashlib
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
K = 4


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(n, time_cap, keep_mb):
    cert_dir = os.path.join(ROOT, "certificates", f"k{K}")
    os.makedirs(cert_dir, exist_ok=True)
    cnf = os.path.join(cert_dir, f"owings_k{K}_n{n}.cnf")
    proof = os.path.join(cert_dir, f"owings_k{K}_n{n}.drat")
    nclauses = write_cnf(n, K, cnf)

    cmd = ["kissat", "-q", "--unsat"]
    if time_cap:
        cmd.append(f"--time={int(time_cap)}")
    cmd += [cnf, proof]
    t0 = time.time()
    solver = subprocess.run(cmd, capture_output=True, text=True)
    solve_s = time.time() - t0
    if solver.returncode != 20:
        print(f"kissat exit {solver.returncode} after {solve_s:.1f}s "
              f"(not UNSAT) — no certificate")
        sys.exit(2)

    t0 = time.time()
    checker = subprocess.run([DRAT_TRIM, cnf, proof],
                             capture_output=True, text=True)
    check_s = time.time() - t0
    verified = "s VERIFIED" in checker.stdout
    proof_bytes = os.path.getsize(proof)
    entry = {"k": K, "n": n, "event": "drat_certificate",
             "method": "direct-full", "clauses": nclauses,
             "kissat_exit": solver.returncode,
             "kissat_seconds": round(solve_s, 3),
             "drat_trim_verified": verified,
             "drat_trim_seconds": round(check_s, 3),
             "proof_bytes": proof_bytes,
             "proof_sha256": sha256(proof),
             "cnf_sha256": sha256(cnf),
             "invocation": " ".join(cmd),
             "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if proof_bytes > keep_mb * (1 << 20):
        os.remove(proof)
        entry["proof_kept"] = False
    else:
        entry["proof_kept"] = True
    with open(os.path.join(ROOT, "results", "search_log.jsonl"), "a") as f:
        f.write(json.dumps(entry) + "\n")
    if not verified:
        raise RuntimeError("drat-trim did NOT verify the proof")
    print(f"certified n(4) <= {n}: kissat {solve_s:.1f}s, proof "
          f"{proof_bytes} bytes, drat-trim VERIFIED in {check_s:.1f}s, "
          f"kept={entry['proof_kept']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--time", type=float, default=None)
    ap.add_argument("--keep-mb", type=float, default=200.0)
    args = ap.parse_args()
    main(args.n, args.time, args.keep_mb)
