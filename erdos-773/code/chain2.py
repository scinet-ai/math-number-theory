"""kissat-based incremental chain for S(N) (Erdos #773), with DRAT
certificates for every UNSAT (optimality) step.

Per level N (knowing S(N-1) and a witness):
  target t = S(N-1)+1
  1. try direct witness extension (exact Python check) -> heuristic-sat
  2. else encode the decision as CNF (cnf.py) and run kissat:
       exit 10 (SAT):   parse witness, re-verify exactly, S(N)=t
       exit 20 (UNSAT): S(N)=S(N-1); DRAT proof checked by drat-trim in a
                        background worker (<=2 concurrent); cert record
                        appended to results/certs.jsonl
Checkpoints: results/chain.jsonl (one line per level, restart-safe).

Usage: chain2.py --max-n 250 --deadline-min 75 [--per-level-cap 1800]
"""

import argparse, hashlib, json, os, shutil, subprocess, sys, threading, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sidon_common import is_square_sidon
from cnf import write_cnf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
RESULTS = os.path.join(ROOT, "results", "chain.jsonl")
CERTS = os.path.join(ROOT, "results", "certs.jsonl")
SCRATCH = os.path.join(ROOT, "scratch")
KISSAT = shutil.which("kissat")
DRATTRIM = os.path.join(HERE, "drat-trim")

cert_lock = threading.Lock()
cert_sem = threading.Semaphore(2)  # max 2 concurrent drat-trim processes
cert_threads = []


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def certify_worker(N, t, cnf_path, drat_path, nvars, nclauses, cap):
    with cert_sem:
        rec = {"n": N, "target": t, "nvars": nvars, "nclauses": nclauses,
               "cnf_sha256": sha256(cnf_path),
               "drat_bytes": os.path.getsize(drat_path),
               "drat_sha256": sha256(drat_path)}
        t0 = time.time()
        try:
            p = subprocess.run([DRATTRIM, cnf_path, drat_path],
                               capture_output=True, text=True, timeout=cap)
            out = p.stdout
            rec["verified"] = "s VERIFIED" in out
            rec["drat_trim_seconds"] = round(time.time() - t0, 2)
        except subprocess.TimeoutExpired:
            rec["verified"] = False
            rec["drat_trim_seconds"] = round(time.time() - t0, 2)
            rec["error"] = "drat-trim timeout"
        if rec["verified"]:
            os.remove(drat_path)
            os.remove(cnf_path)
        with cert_lock:
            with open(CERTS, "a") as f:
                f.write(json.dumps(rec) + "\n")
        print(f"[cert] N={N} verified={rec['verified']} "
              f"({rec['drat_trim_seconds']}s, {rec['drat_bytes']}B proof)",
              flush=True)


def run_kissat(cnf_path, drat_path, cap):
    """Returns (status, witness_vars, wall). status in SAT/UNSAT/TIMEOUT."""
    t0 = time.time()
    try:
        p = subprocess.run([KISSAT, cnf_path, drat_path],
                           capture_output=True, text=True, timeout=cap)
    except subprocess.TimeoutExpired:
        return "TIMEOUT", None, time.time() - t0
    wall = time.time() - t0
    if p.returncode == 10:
        lits = []
        for line in p.stdout.splitlines():
            if line.startswith("v "):
                lits += [int(x) for x in line[2:].split()]
        pos = sorted(l for l in lits if l > 0)
        return "SAT", pos, wall
    if p.returncode == 20:
        return "UNSAT", None, wall
    raise RuntimeError(f"kissat rc={p.returncode}: {p.stderr[:500]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=250)
    ap.add_argument("--deadline-min", type=float, default=75.0)
    ap.add_argument("--per-level-cap", type=float, default=1800.0)
    ap.add_argument("--drat-cap", type=float, default=2400.0)
    args = ap.parse_args()
    deadline = time.time() + args.deadline_min * 60.0
    os.makedirs(SCRATCH, exist_ok=True)

    recs = []
    with open(RESULTS) as f:
        for line in f:
            if line.strip():
                recs.append(json.loads(line))
    assert recs, "chain.jsonl must exist (run chain.py first for base)"
    S_prev = recs[-1]["S"]
    witness = recs[-1]["witness"]
    n_start = recs[-1]["n"] + 1
    print(f"[chain2] resuming at N={n_start}, S({n_start-1})={S_prev}",
          flush=True)

    for N in range(n_start, args.max_n + 1):
        remaining = deadline - time.time()
        if remaining <= 10:
            print(f"[chain2] deadline before N={N}; stopping", flush=True)
            break
        t = S_prev + 1
        t0 = time.time()
        rec = {"n": N, "target": t, "engine": "kissat"}
        wit = sorted(witness + [N])
        if len(wit) == t and is_square_sidon(wit):
            S_prev, witness = t, wit
            rec.update({"S": t, "step": "heuristic-sat", "witness": wit,
                        "wall": round(time.time() - t0, 3)})
        else:
            cnf_path = os.path.join(SCRATCH, f"n{N}t{t}.cnf")
            drat_path = os.path.join(SCRATCH, f"n{N}t{t}.drat")
            nvars, nclauses = write_cnf(cnf_path, N, t)
            cap = min(args.per_level_cap, max(10.0, remaining - 10))
            status, pos, wall = run_kissat(cnf_path, drat_path, cap)
            if status == "SAT":
                w = [v for v in pos if v <= N]
                assert N in w and len(w) == t and is_square_sidon(w), \
                    f"bad witness at N={N}"
                S_prev, witness = t, w
                rec.update({"S": t, "step": "kissat-sat", "witness": w,
                            "wall": round(wall, 3),
                            "nvars": nvars, "nclauses": nclauses})
                for pth in (cnf_path, drat_path):
                    if os.path.exists(pth):
                        os.remove(pth)
            elif status == "UNSAT":
                rec.update({"S": S_prev, "step": "kissat-unsat",
                            "witness": witness, "wall": round(wall, 3),
                            "nvars": nvars, "nclauses": nclauses})
                th = threading.Thread(
                    target=certify_worker,
                    args=(N, t, cnf_path, drat_path, nvars, nclauses,
                          args.drat_cap))
                th.start()
                cert_threads.append(th)
            else:
                print(f"[chain2] N={N} kissat TIMEOUT after {cap:.0f}s; "
                      f"stopping chain", flush=True)
                for pth in (cnf_path, drat_path):
                    if os.path.exists(pth):
                        os.remove(pth)
                break
        with open(RESULTS, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"[chain2] N={N} S={rec['S']} {rec['step']} "
              f"wall={rec['wall']}s", flush=True)

    print("[chain2] waiting for cert workers...", flush=True)
    for th in cert_threads:
        th.join()
    print("[chain2] done", flush=True)


if __name__ == "__main__":
    main()
