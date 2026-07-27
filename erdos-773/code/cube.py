"""Cube-and-conquer for one hard chain level of Erdos #773.

Splits the level-N profile-strengthened decision on the signs of the given
split variables (2^k cubes, k = 1 or 2), runs kissat on the cubes in
parallel (respecting a global process budget of 3 incl. running cert
daemons), and combines:
  - any cube SAT             -> level SAT (witness re-verified exactly)
  - all cubes UNSAT          -> level UNSAT; each cube's DRAT is checked by
                                cert_daemon (record carries 'cube': [...]);
                                the complete sign family is the certificate
  - any cube TIMEOUT         -> inconclusive, nothing recorded
On a decided level, appends the chain record to results/chain.jsonl
(step 'cube-sat' / 'cube-unsat').

Usage: cube.py --split 54 [--split2 40] --cap-s 540
"""

import argparse, itertools, json, os, shutil, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sidon_common import is_square_sidon
from cnf import build_cnf_profile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
RESULTS = os.path.join(ROOT, "results", "chain.jsonl")
SCRATCH = os.path.join(ROOT, "scratch")
KISSAT = shutil.which("kissat")
ENCODING_TAG = "profile-v2"


def daemons_alive():
    out = subprocess.run(["pgrep", "-cf", "code/cert_daemon.py"],
                         capture_output=True, text=True).stdout.strip()
    return int(out or 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", type=int, required=True)
    ap.add_argument("--split2", type=int, default=0)
    ap.add_argument("--cap-s", type=float, default=540.0)
    ap.add_argument("--drat-cap", type=float, default=3000.0)
    ap.add_argument("--anchored", action="store_true",
                    help="operate on the anchored frontier chain "
                         "(results/anchored.jsonl, OEIS-completed profile)")
    args = ap.parse_args()

    global RESULTS, ENCODING_TAG
    if args.anchored:
        from anchored import load_profile
        S, witness_prev = load_profile()
        RESULTS = os.path.join(ROOT, "results", "anchored.jsonl")
        ENCODING_TAG = "profile-v2-anchored"
        N = len(S) + 1
        t = S[-1] + 1
    else:
        recs = [json.loads(l) for l in open(RESULTS) if l.strip()]
        S = [r["S"] for r in recs]
        N = recs[-1]["n"] + 1
        t = S[-1] + 1
        witness_prev = recs[-1]["witness"]
    nvars, base_clauses = build_cnf_profile(N, t, S)
    split_vars = [args.split] + ([args.split2] if args.split2 else [])
    cubes = list(itertools.product(*[(v, -v) for v in split_vars]))

    # Solver waves take priority on the <=3-process budget: our running
    # drat-trim checkers are SIGSTOPped for the duration of each wave
    # (zero CPU while paused) and resumed afterwards.
    width = 2
    subprocess.run(["pkill", "-STOP", "-f", "erdos-773/code/drat-trim"],
                   capture_output=True)
    results = []
    for w0 in range(0, len(cubes), width):
        wave = cubes[w0:w0 + width]
        procs = []
        for idx, cube in enumerate(wave, start=w0):
            cnf_path = os.path.join(SCRATCH, f"cube{N}t{t}_{idx}.cnf")
            drat_path = os.path.join(SCRATCH, f"cube{N}t{t}_{idx}.drat")
            with open(cnf_path, "w") as f:
                f.write(f"c erdos773 N={N} t={t} cube={list(cube)} "
                        f"profile-strengthened\n")
                f.write(f"p cnf {nvars} {len(base_clauses) + len(cube)}\n")
                for cl in base_clauses:
                    f.write(" ".join(map(str, cl)) + " 0\n")
                for lit in cube:
                    f.write(f"{lit} 0\n")
            p = subprocess.Popen([KISSAT, cnf_path, drat_path],
                                 stdout=subprocess.PIPE, text=True)
            procs.append((cube, cnf_path, drat_path, p))
            print(f"[cube] N={N} t={t} launched cube {list(cube)}",
                  flush=True)
        deadline = time.time() + args.cap_s
        for cube, cnf_path, drat_path, p in procs:
            try:
                out, _ = p.communicate(
                    timeout=max(5, deadline - time.time()))
            except subprocess.TimeoutExpired:
                p.kill()
                out = ""
            rc = p.returncode
            status = {10: "SAT", 20: "UNSAT"}.get(rc, "TIMEOUT")
            results.append((cube, cnf_path, drat_path, status, out))
            print(f"[cube] N={N} cube={list(cube)}: {status}", flush=True)
        if any(r[3] == "SAT" for r in results):
            break
    subprocess.run(["pkill", "-CONT", "-f", "erdos-773/code/drat-trim"],
                   capture_output=True)

    sat = [r for r in results if r[3] == "SAT"]
    if sat:
        cube, cnf_path, drat_path, _, out = sat[0]
        lits = []
        for line in out.splitlines():
            if line.startswith("v "):
                lits += [int(x) for x in line[2:].split()]
        w = sorted(l for l in lits if 0 < l <= N)
        assert N in w and len(w) == t and is_square_sidon(w)
        rec = {"n": N, "target": t, "engine": "kissat-profile-cube",
               "S": t, "step": "cube-sat", "witness": w,
               "cube": list(cube), "nvars": nvars}
        with open(RESULTS, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"[cube] N={N} decided SAT, S={t}", flush=True)
        for _, cnf_path, drat_path, _, _ in results:
            for pth in (cnf_path, drat_path):
                if os.path.exists(pth):
                    os.remove(pth)
    elif all(r[3] == "UNSAT" for r in results):
        rec = {"n": N, "target": t, "engine": "kissat-profile-cube",
               "S": S[-1], "step": "cube-unsat", "witness": witness_prev,
               "cubes": [list(r[0]) for r in results], "nvars": nvars}
        with open(RESULTS, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"[cube] N={N} decided UNSAT, S={S[-1]}", flush=True)
        for cube, cnf_path, drat_path, _, _ in results:
            cmd = [sys.executable, os.path.join(HERE, "cert_daemon.py"),
                   cnf_path, drat_path, str(N), str(t), str(nvars),
                   str(len(base_clauses) + len(cube)),
                   ENCODING_TAG + "-cube:" + json.dumps(list(cube)),
                   str(args.drat_cap)]
            if daemons_alive() >= 2:
                # leave files; cert_pending.py sweeps them up later
                print(f"[cube] cert queue full; deferring {drat_path}",
                      flush=True)
            else:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL,
                                 start_new_session=True)
    else:
        print(f"[cube] N={N} INCONCLUSIVE "
              f"({[(list(r[0]), r[3]) for r in results]})", flush=True)
        for _, cnf_path, drat_path, st, _ in results:
            for pth in (cnf_path, drat_path):
                if os.path.exists(pth):
                    os.remove(pth)
        sys.exit(3)


if __name__ == "__main__":
    main()
