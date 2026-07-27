"""Profile-strengthened kissat chain for S(N) (Erdos #773).

Same inductive scheme as chain2.py, but each level-N CNF additionally
carries the certified prefix profile S(1..N-1) as counter upper bounds
(see cnf.build_cnf_profile). This makes every UNSAT level a conditional
lemma: 'given S(1..N-1), no square-Sidon subset of the first N squares
has size S(N-1)+1'. The chain of lemmas + exactly-verified witnesses is
the full certificate. SAT answers are unconditional (witness re-verified
in exact arithmetic).

Modes:
  --mode validate --from A --to B : re-decide known levels with the
      profile encoder; compare against recorded outcomes; no state writes.
  --mode extend                    : continue the chain from the last
      checkpoint in results/chain.jsonl (same record format; engine field
      'kissat-profile').
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
cert_sem = threading.Semaphore(2)
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
               "encoding": "profile-v2",
               "cnf_sha256": sha256(cnf_path),
               "drat_bytes": os.path.getsize(drat_path),
               "drat_sha256": sha256(drat_path)}
        t0 = time.time()
        try:
            p = subprocess.run([DRATTRIM, cnf_path, drat_path],
                               capture_output=True, text=True, timeout=cap)
            rec["verified"] = "s VERIFIED" in p.stdout
        except subprocess.TimeoutExpired:
            rec["verified"] = False
            rec["error"] = "drat-trim timeout"
        rec["drat_trim_seconds"] = round(time.time() - t0, 2)
        if rec["verified"]:
            os.remove(drat_path)
            os.remove(cnf_path)
        with cert_lock:
            with open(CERTS, "a") as f:
                f.write(json.dumps(rec) + "\n")
        print(f"[cert] N={N} verified={rec['verified']} "
              f"({rec['drat_trim_seconds']}s, {rec['drat_bytes']}B proof)",
              flush=True)


def run_kissat(cnf_path, drat_path, cap, sat_mode=False):
    cmd = [KISSAT]
    if sat_mode:
        cmd.append("--sat")
    cmd += [cnf_path] + ([drat_path] if drat_path else [])
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=cap)
    except subprocess.TimeoutExpired:
        return "TIMEOUT", None, time.time() - t0
    wall = time.time() - t0
    if p.returncode == 10:
        lits = []
        for line in p.stdout.splitlines():
            if line.startswith("v "):
                lits += [int(x) for x in line[2:].split()]
        return "SAT", sorted(l for l in lits if l > 0), wall
    if p.returncode == 20:
        return "UNSAT", None, wall
    raise RuntimeError(f"kissat rc={p.returncode}: {p.stderr[:300]}")


def load_chain():
    recs = []
    with open(RESULTS) as f:
        for line in f:
            if line.strip():
                recs.append(json.loads(line))
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["validate", "extend"], required=True)
    ap.add_argument("--from", dest="lo", type=int, default=40)
    ap.add_argument("--to", dest="hi", type=int, default=53)
    ap.add_argument("--max-n", type=int, default=250)
    ap.add_argument("--deadline-min", type=float, default=60.0)
    ap.add_argument("--per-level-cap", type=float, default=2400.0)
    ap.add_argument("--drat-cap", type=float, default=3000.0)
    ap.add_argument("--detached-certs", action="store_true",
                    help="verify DRAT proofs in fully detached cert_daemon "
                         "processes (max 2 alive; 3rd runs inline) so this "
                         "process can exit right after solving")
    args = ap.parse_args()
    deadline = time.time() + args.deadline_min * 60.0
    recs = load_chain()
    S = [r["S"] for r in recs]  # S[m-1] = S(m)

    if args.mode == "validate":
        bad = 0
        for n in range(args.lo, args.hi + 1):
            r = recs[n - 1]
            assert r["n"] == n
            t = S[n - 2] + 1
            expect = "SAT" if r["step"].endswith("-sat") else "UNSAT"
            cnf_path = os.path.join(SCRATCH, f"val{n}.cnf")
            write_cnf(cnf_path, n, t, profile=S[:n - 1])
            status, pos, wall = run_kissat(cnf_path, None, 600)
            ok = status == expect
            if status == "SAT":
                w = [v for v in pos if v <= n]
                ok = ok and n in w and len(w) == t and is_square_sidon(w)
            print(f"[val] N={n} t={t} expect={expect} got={status} "
                  f"wall={wall:.1f}s {'OK' if ok else 'MISMATCH'}",
                  flush=True)
            bad += 0 if ok else 1
            os.remove(cnf_path)
        print(f"[val] done, mismatches={bad}", flush=True)
        sys.exit(1 if bad else 0)

    # extend
    S_prev, witness, n_start = recs[-1]["S"], recs[-1]["witness"], \
        recs[-1]["n"] + 1
    print(f"[chain3] extending at N={n_start}, S({n_start-1})={S_prev}",
          flush=True)
    for N in range(n_start, args.max_n + 1):
        remaining = deadline - time.time()
        if remaining <= 10:
            print(f"[chain3] deadline before N={N}; stopping", flush=True)
            break
        t = S_prev + 1
        t0 = time.time()
        rec = {"n": N, "target": t, "engine": "kissat-profile"}
        wit = sorted(witness + [N])
        if len(wit) == t and is_square_sidon(wit):
            S_prev, witness = t, wit
            rec.update({"S": t, "step": "heuristic-sat", "witness": wit,
                        "wall": round(time.time() - t0, 3)})
        else:
            cnf_path = os.path.join(SCRATCH, f"n{N}t{t}.cnf")
            drat_path = os.path.join(SCRATCH, f"n{N}t{t}.drat")
            nvars, nclauses = write_cnf(cnf_path, N, t, profile=S)
            # deadline gates STARTING levels; a started level gets the
            # full per-level cap (foreground batches rely on this)
            cap = args.per_level_cap
            status, pos, wall = run_kissat(cnf_path, drat_path, cap)
            if status == "SAT":
                w = [v for v in pos if v <= N]
                assert N in w and len(w) == t and is_square_sidon(w), \
                    f"bad witness at N={N}"
                S_prev, witness = t, w
                rec.update({"S": t, "step": "kissat-sat", "witness": w,
                            "wall": round(wall, 3), "nvars": nvars,
                            "nclauses": nclauses})
                for pth in (cnf_path, drat_path):
                    if os.path.exists(pth):
                        os.remove(pth)
            elif status == "UNSAT":
                rec.update({"S": S_prev, "step": "kissat-unsat",
                            "witness": witness, "wall": round(wall, 3),
                            "nvars": nvars, "nclauses": nclauses})
                if args.detached_certs:
                    alive = int(subprocess.run(
                        ["pgrep", "-cf", "code/cert_daemon.py"],
                        capture_output=True, text=True).stdout.strip()
                        or 0)
                    cmd = [sys.executable,
                           os.path.join(HERE, "cert_daemon.py"),
                           cnf_path, drat_path, str(N), str(t),
                           str(nvars), str(nclauses), "profile-v2",
                           str(args.drat_cap)]
                    if alive >= 2:
                        # leave files for cert_pending.py to sweep later
                        print(f"[chain3] cert queue full; deferring "
                              f"{drat_path}", flush=True)
                    else:
                        subprocess.Popen(
                            cmd, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            start_new_session=True)
                else:
                    th = threading.Thread(
                        target=certify_worker,
                        args=(N, t, cnf_path, drat_path, nvars, nclauses,
                              args.drat_cap))
                    th.start()
                    cert_threads.append(th)
            else:
                print(f"[chain3] N={N} TIMEOUT after {cap:.0f}s; stopping",
                      flush=True)
                for pth in (cnf_path, drat_path):
                    if os.path.exists(pth):
                        os.remove(pth)
                break
        S.append(rec["S"])
        with open(RESULTS, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"[chain3] N={N} S={rec['S']} {rec['step']} "
              f"wall={rec['wall']}s", flush=True)

    print("[chain3] waiting for cert workers...", flush=True)
    for th in cert_threads:
        th.join()
    print("[chain3] done", flush=True)


if __name__ == "__main__":
    main()
