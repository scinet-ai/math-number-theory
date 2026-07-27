#!/usr/bin/env python3
"""Cube-and-conquer for hard finite Owings instances (k=4), UNSAT direction.

Split on the colours of chosen "cube variables" (default: the doubled
elements 4,6,8,10,12 — every 4-set A containing a small a forces the colour
of 2a, so these are the most constrained variables).  For each assignment
(cube) we solve  full-CNF + unit clauses  with kissat, emitting a DRAT proof
that drat-trim verifies immediately; the proof is then deleted (deterministic
regeneration is the evidence chain), keeping sha256+size in the cube log.

Colour-swap symmetry: the canonical CNF is invariant under flipping all
colours (its clauses come in mirror pairs), so CNF+cube is UNSAT iff
CNF+flipped-cube is.  With --half we therefore only run the cubes in which
the FIRST cube variable is 0; the other half follows by the documented
involution.  Run without --half for a purely mechanical cover of all cubes.

Soundness of the combination: the 2^m cubes are all assignments of the cube
variables, so every truth assignment extends some cube; if CNF+cube is UNSAT
for every cube, CNF is UNSAT, i.e. n(4) <= n.

A SAT cube yields a witness colouring (independently re-checked) and stops
the run: n(4) > n.

Checkpointing: each cube's outcome is appended to results/cube_log_n{n}.jsonl
the moment it finishes; a restarted run skips finished cubes.

Usage: cube_conquer.py n [--vars 4,6,8,10,12] [--half] [--time-per-cube S]
                         [--jobs 3]
"""
import argparse
import hashlib
import itertools
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "results")
DRAT_TRIM = os.path.join(ROOT, "tools", "drat-trim", "drat-trim")
K = 4

sys.path.insert(0, HERE)
from generate_cnf import sumset_clauses       # noqa: E402
from check_coloring import find_mono_set      # noqa: E402
from solve_direct import parse_model          # noqa: E402


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def base_clause_lines(n):
    lines = []
    for S in sumset_clauses(n, K):
        lines.append(" ".join(map(str, S)) + " 0\n")
        lines.append(" ".join(str(-s) for s in S) + " 0\n")
    return lines


def write_cube_cnf(path, n, base_lines, cube):
    units = [f"{v if bit else -v} 0\n" for v, bit in cube]
    with open(path, "w") as f:
        f.write(f"c Owings k={K} n={n} cube={cube}\n")
        f.write(f"p cnf {n} {len(base_lines) + len(units)}\n")
        f.writelines(units)
        f.writelines(base_lines)


def run_cube(n, base_lines, cube, time_cap, workdir):
    tag = "_".join(f"{v}{'1' if b else '0'}" for v, b in cube)
    cnf = os.path.join(workdir, f"cube_{tag}.cnf")
    proof = os.path.join(workdir, f"cube_{tag}.drat")
    write_cube_cnf(cnf, n, base_lines, cube)
    cmd = ["kissat", "-q", "--unsat", f"--time={int(time_cap)}", cnf, proof]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    solve_s = time.time() - t0
    entry = {"n": n, "cube": [[v, b] for v, b in cube],
             "solve_seconds": round(solve_s, 3), "invocation": " ".join(cmd)}
    if proc.returncode == 20:
        chk = subprocess.run([DRAT_TRIM, cnf, proof],
                             capture_output=True, text=True)
        entry["status"] = "UNSAT"
        entry["drat_trim_verified"] = "s VERIFIED" in chk.stdout
        entry["proof_bytes"] = os.path.getsize(proof)
        entry["proof_sha256"] = sha256(proof)
        os.remove(proof)
    elif proc.returncode == 10:
        colours = parse_model(proc.stdout, n)
        bits = "".join(map(str, colours))
        wit = os.path.join(RESULTS, f"witness_k{K}_n{n}.txt")
        with open(wit, "w") as f:
            f.write(bits + "\n")
        hit = find_mono_set(colours, K)
        entry["status"] = "SAT"
        entry["witness"] = os.path.basename(wit)
        entry["independent_recheck"] = ("AVOIDING" if hit is None
                                        else f"VIOLATED:{hit}")
    else:
        entry["status"] = "UNDECIDED"
        entry["kissat_exit"] = proc.returncode
    os.remove(cnf)
    return entry


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--vars", default="4,6,8,10,12")
    ap.add_argument("--half", action="store_true")
    ap.add_argument("--time-per-cube", type=float, default=600)
    ap.add_argument("--jobs", type=int, default=3)
    args = ap.parse_args()
    n = args.n
    cube_vars = [int(v) for v in args.vars.split(",")]
    log_path = os.path.join(RESULTS, f"cube_log_n{n}.jsonl")

    done = set()
    if os.path.exists(log_path):
        for line in open(log_path):
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("status") in ("UNSAT", "SAT"):
                done.add(tuple(tuple(x) for x in e["cube"]))

    cubes = []
    for bits in itertools.product([0, 1], repeat=len(cube_vars)):
        if args.half and bits[0] == 1:
            continue
        cube = tuple(zip(cube_vars, bits))
        if cube not in done:
            cubes.append(cube)
    print(f"n={n}: {len(cubes)} cubes to run over vars {cube_vars} "
          f"(half={args.half}, {len(done)} already done)", flush=True)

    workdir = os.path.join(RESULTS, f"cubes_n{n}")
    os.makedirs(workdir, exist_ok=True)
    base_lines = base_clause_lines(n)

    t_all = time.time()
    n_unsat = n_sat = n_undecided = 0
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {ex.submit(run_cube, n, base_lines, c,
                          args.time_per_cube, workdir): c for c in cubes}
        for fut in as_completed(futs):
            e = fut.result()
            e["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            with open(log_path, "a") as f:
                f.write(json.dumps(e) + "\n")
            st = e["status"]
            n_unsat += st == "UNSAT"
            n_sat += st == "SAT"
            n_undecided += st == "UNDECIDED"
            print(f"  cube {e['cube']}: {st} ({e['solve_seconds']}s)",
                  flush=True)
            if st == "SAT":
                print(f"SAT cube => n(4) > {n}; witness saved "
                      f"({e['independent_recheck']}); stopping.", flush=True)
                for other in futs:
                    other.cancel()
                break
    print(f"n={n} cube summary: UNSAT={n_unsat} SAT={n_sat} "
          f"UNDECIDED={n_undecided} in {time.time()-t_all:.0f}s", flush=True)


if __name__ == "__main__":
    main()
