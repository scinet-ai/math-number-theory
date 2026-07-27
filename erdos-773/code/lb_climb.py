"""Certified lower bounds for S(N) at large N via kissat --sat target
climbing (method from the earlier partial attempt in prior-attempt/,
re-implemented against code/cnf.py).

For t = start, start+1, ...: solve 'exists square-Sidon subset of the
first N squares with size >= t' (no forced element, no profile bounds),
kissat --sat, cap seconds per target. First non-SAT outcome (UNSAT or
timeout) ends the climb. Every witness is re-verified in exact arithmetic
and checkpointed immediately to results/lb.jsonl.

Usage: lb_climb.py --n 100 --start-t 43 --cap-s 120 [--budget-s 600]
"""

import argparse, json, os, shutil, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sidon_common import is_square_sidon
from cnf import build_cnf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "results", "lb.jsonl")
SCRATCH = os.path.join(ROOT, "scratch")
KISSAT = shutil.which("kissat")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--start-t", type=int, required=True)
    ap.add_argument("--cap-s", type=float, default=120.0)
    ap.add_argument("--budget-s", type=float, default=600.0)
    args = ap.parse_args()
    N, t = args.n, args.start_t
    deadline = time.time() + args.budget_s
    while True:
        cap = min(args.cap_s, deadline - time.time())
        if cap < 5:
            print(f"[lb] N={N} budget exhausted at t={t}", flush=True)
            break
        nvars, clauses = build_cnf(N, t, force_last=False)
        path = os.path.join(SCRATCH, f"lb{N}t{t}.cnf")
        with open(path, "w") as f:
            f.write(f"p cnf {nvars} {len(clauses)}\n")
            for cl in clauses:
                f.write(" ".join(map(str, cl)) + " 0\n")
        t0 = time.time()
        try:
            p = subprocess.run([KISSAT, "--sat", f"--time={int(cap)}", path],
                               capture_output=True, text=True,
                               timeout=cap + 30)
        except subprocess.TimeoutExpired:
            os.remove(path)
            print(f"[lb] N={N} t={t}: hard timeout", flush=True)
            break
        wall = time.time() - t0
        os.remove(path)
        if p.returncode == 10:
            lits = []
            for line in p.stdout.splitlines():
                if line.startswith("v "):
                    lits += [int(x) for x in line[2:].split()]
            w = sorted(l for l in lits if 0 < l <= N)
            assert len(w) >= t and is_square_sidon(w), f"bad witness N={N}"
            rec = {"n": N, "lower_bound": len(w), "witness": w,
                   "engine": "kissat--sat", "target": t,
                   "wall": round(wall, 1), "cap_s": args.cap_s}
            with open(OUT, "a") as f:
                f.write(json.dumps(rec) + "\n")
            print(f"[lb] N={N} t={t}: SAT ({wall:.1f}s) -> S({N})>={len(w)}",
                  flush=True)
            t = len(w) + 1
        else:
            res = {10: "SAT", 20: "UNSAT"}.get(p.returncode, "TIMEOUT")
            print(f"[lb] N={N} t={t}: {res} ({wall:.1f}s); climb ends",
                  flush=True)
            break


if __name__ == "__main__":
    main()
