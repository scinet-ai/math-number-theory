"""Backfill DRAT certificates for UNSAT levels decided by CP-SAT (the early
part of the chain, before chain2.py switched the engine to kissat).

For each chain record with step == 'cpsat-unsat' and no cert record yet:
regenerate the CNF deterministically, run kissat (expect UNSAT), check the
DRAT proof with drat-trim, append to results/certs.jsonl.
"""

import json, os, sys, subprocess, time, hashlib, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cnf import write_cnf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
RESULTS = os.path.join(ROOT, "results", "chain.jsonl")
CERTS = os.path.join(ROOT, "results", "certs.jsonl")
SCRATCH = os.path.join(ROOT, "scratch")
KISSAT = shutil.which("kissat")
DRATTRIM = os.path.join(HERE, "drat-trim")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    done = set()
    if os.path.exists(CERTS):
        with open(CERTS) as f:
            for line in f:
                if line.strip():
                    done.add(json.loads(line)["n"])
    todo = []
    with open(RESULTS) as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("step") in ("cpsat-unsat", "kissat-unsat") \
                    and r["n"] not in done:
                todo.append((r["n"], r["target"]))
    print(f"[backfill] {len(todo)} UNSAT levels to certify: "
          f"{[n for n, _ in todo]}", flush=True)
    for N, t in todo:
        cnf_path = os.path.join(SCRATCH, f"bf_n{N}t{t}.cnf")
        drat_path = os.path.join(SCRATCH, f"bf_n{N}t{t}.drat")
        nvars, nclauses = write_cnf(cnf_path, N, t)
        t0 = time.time()
        p = subprocess.run([KISSAT, "-q", cnf_path, drat_path],
                           capture_output=True, text=True, timeout=3600)
        kw = time.time() - t0
        assert p.returncode == 20, f"N={N}: expected UNSAT, rc={p.returncode}"
        rec = {"n": N, "target": t, "nvars": nvars, "nclauses": nclauses,
               "cnf_sha256": sha256(cnf_path),
               "drat_bytes": os.path.getsize(drat_path),
               "drat_sha256": sha256(drat_path),
               "kissat_seconds": round(kw, 2), "backfill": True}
        t0 = time.time()
        q = subprocess.run([DRATTRIM, cnf_path, drat_path],
                           capture_output=True, text=True, timeout=3600)
        rec["verified"] = "s VERIFIED" in q.stdout
        rec["drat_trim_seconds"] = round(time.time() - t0, 2)
        if rec["verified"]:
            os.remove(drat_path)
            os.remove(cnf_path)
        with open(CERTS, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"[backfill] N={N} t={t} verified={rec['verified']} "
              f"kissat={rec['kissat_seconds']}s "
              f"drat-trim={rec['drat_trim_seconds']}s", flush=True)
    print("[backfill] done", flush=True)


if __name__ == "__main__":
    main()
