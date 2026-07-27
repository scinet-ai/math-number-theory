"""Anchored frontier chain for Erdos #773: extend the exact S(N) table
into NEW territory (N >= 69) using as prefix profile:

  - our self-certified chain values S(1..N0) from results/chain.jsonl
    (N0 = its last level), and
  - the published OEIS A390813 values a(N0+1..68) (independently computed
    by Kalogeropoulos/Sievers, 2025) as ASSUMED lemmas, and
  - previously decided anchored levels from results/anchored.jsonl.

Consequences (recorded honestly): witnesses (SAT side) remain
unconditional lower bounds; UNSAT lemmas and hence exact-value claims for
N >= 69 are conditional on the assumed published values (which our own
chain independently re-derived and matched for all n <= N0).

Records go to results/anchored.jsonl. DRAT proofs via detached
cert_daemon, encoding tag 'profile-v2-anchored'.

Usage: anchored.py [--levels K] [--per-level-cap S] [--drat-cap S]
"""

import argparse, json, os, shutil, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sidon_common import is_square_sidon, OEIS_A390813
from cnf import write_cnf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
CHAIN = os.path.join(ROOT, "results", "chain.jsonl")
ANCH = os.path.join(ROOT, "results", "anchored.jsonl")
SCRATCH = os.path.join(ROOT, "scratch")
KISSAT = shutil.which("kissat")


def load_profile():
    """Return (S list for 1..last, witness_of_last, own_chain_top)."""
    recs = [json.loads(l) for l in open(CHAIN) if l.strip()]
    S = [r["S"] for r in recs]
    n0 = recs[-1]["n"]
    assert S[:min(n0, 68)] == OEIS_A390813[:min(n0, 68)], \
        "own chain disagrees with OEIS -- refuse to anchor"
    witness = recs[-1]["witness"]
    if n0 < 68:
        S = S + OEIS_A390813[n0:68]
    # sanity: monotone steps 0/+1
    for a, b in zip(S, S[1:]):
        assert b - a in (0, 1)
    if os.path.exists(ANCH):
        for l in open(ANCH):
            if l.strip():
                r = json.loads(l)
                assert r["n"] == len(S) + 1
                S.append(r["S"])
                if r.get("witness"):
                    witness = r["witness"]
    return S, witness


def run_kissat(cnf_path, drat_path, cap):
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
        return "SAT", sorted(l for l in lits if l > 0), wall
    if p.returncode == 20:
        return "UNSAT", None, wall
    raise RuntimeError(f"kissat rc={p.returncode}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", type=int, default=1)
    ap.add_argument("--per-level-cap", type=float, default=480.0)
    ap.add_argument("--drat-cap", type=float, default=3600.0)
    args = ap.parse_args()
    for _ in range(args.levels):
        S, witness = load_profile()
        N = len(S) + 1
        t = S[-1] + 1
        rec = {"n": N, "target": t, "engine": "kissat-profile-anchored"}
        t0 = time.time()
        wit = sorted(witness + [N])
        if len(wit) == t and is_square_sidon(wit):
            rec.update({"S": t, "step": "heuristic-sat", "witness": wit,
                        "wall": round(time.time() - t0, 3)})
        else:
            cnf_path = os.path.join(SCRATCH, f"a{N}t{t}.cnf")
            drat_path = os.path.join(SCRATCH, f"a{N}t{t}.drat")
            nvars, nclauses = write_cnf(cnf_path, N, t, profile=S)
            status, pos, wall = run_kissat(cnf_path, drat_path,
                                           args.per_level_cap)
            if status == "SAT":
                w = [v for v in pos if v <= N]
                assert N in w and len(w) == t and is_square_sidon(w)
                rec.update({"S": t, "step": "kissat-sat", "witness": w,
                            "wall": round(wall, 3), "nvars": nvars,
                            "nclauses": nclauses})
                for pth in (cnf_path, drat_path):
                    if os.path.exists(pth):
                        os.remove(pth)
            elif status == "UNSAT":
                rec.update({"S": S[-1], "step": "kissat-unsat",
                            "witness": witness, "wall": round(wall, 3),
                            "nvars": nvars, "nclauses": nclauses})
                alive = int(subprocess.run(
                    ["pgrep", "-cf", "code/cert_daemon.py"],
                    capture_output=True, text=True).stdout.strip() or 0)
                cmd = [sys.executable, os.path.join(HERE, "cert_daemon.py"),
                       cnf_path, drat_path, str(N), str(t), str(nvars),
                       str(nclauses), "profile-v2-anchored",
                       str(args.drat_cap)]
                if alive >= 2:
                    print(f"[anchored] cert queue full; deferring "
                          f"{drat_path}", flush=True)
                else:
                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL,
                                     start_new_session=True)
            else:
                print(f"[anchored] N={N} TIMEOUT; stopping", flush=True)
                for pth in (cnf_path, drat_path):
                    if os.path.exists(pth):
                        os.remove(pth)
                break
        with open(ANCH, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"[anchored] N={N} S={rec['S']} {rec['step']} "
              f"wall={rec.get('wall')}s", flush=True)


if __name__ == "__main__":
    main()
