"""Spot-verifier for the Erdos #773 computation (target: < 5 minutes).

Checks:
 1. chain.jsonl is a contiguous, monotone chain n=1..N*, steps +0/+1,
    +1 exactly on sat steps.
 2. every recorded witness is a genuine square-Sidon set of the claimed
    size within {1..n} (exact integer arithmetic, full pairwise check).
 3. values match OEIS A390813 for n <= 68 (independent published values).
 4. fresh brute-force recomputation for n <= 18 matches.
 5. every UNSAT level has a cert record with verified=True (drat-trim).
 6. spot re-solve: 3 small UNSAT levels re-encoded from scratch, kissat
    must return UNSAT again and drat-trim must verify the fresh proof.
 7. heuristic.jsonl witnesses are genuine square-Sidon sets.

Exit code 0 iff all checks pass.
"""

import json, os, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sidon_common import is_square_sidon, brute_force_S, OEIS_A390813
from cnf import write_cnf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
KISSAT = shutil.which("kissat")
DRATTRIM = os.path.join(HERE, "drat-trim")
fails = []


def check(cond, msg):
    tag = "ok " if cond else "FAIL"
    print(f"[{tag}] {msg}")
    if not cond:
        fails.append(msg)


def main():
    recs = [json.loads(l) for l in open(os.path.join(ROOT, "results",
            "chain.jsonl")) if l.strip()]
    ns = [r["n"] for r in recs]
    Nstar = ns[-1]
    check(ns == list(range(1, Nstar + 1)), f"chain contiguous 1..{Nstar}")
    ok_steps = True
    for a, b in zip(recs, recs[1:]):
        d = b["S"] - a["S"]
        sat = b["step"].endswith("sat") and not b["step"].endswith("unsat")
        if not ((d == 1 and sat) or (d == 0 and not sat)):
            ok_steps = False
    check(ok_steps, "chain steps consistent (+1 on sat, +0 on unsat)")
    ok_wit = all(
        is_square_sidon(r["witness"]) and len(r["witness"]) == r["S"]
        and max(r["witness"]) <= r["n"] for r in recs)
    check(ok_wit, f"all {Nstar} chain witnesses are square-Sidon of size S(n)")
    k = min(Nstar, 68)
    check([r["S"] for r in recs[:k]] == OEIS_A390813[:k],
          f"values match OEIS A390813 for n<=68 (checked n<={k})")
    bf = [brute_force_S(n) for n in range(1, 19)]
    check(bf == [r["S"] for r in recs[:18]],
          "fresh brute force matches for n<=18")

    certs = {}
    for l in open(os.path.join(ROOT, "results", "certs.jsonl")):
        if l.strip():
            c = json.loads(l)
            certs.setdefault(c["n"], []).append(c)

    def level_certified(n):
        """Plain verified cert, or a complete verified 1-var cube family
        (both signs of the same split variable)."""
        pos, neg = set(), set()
        for c in certs.get(n, []):
            enc = c.get("encoding", "v1")
            if not c["verified"]:
                continue
            if "-cube:" in enc:
                cube = json.loads(enc.split("-cube:", 1)[1])
                if len(cube) == 1:
                    (pos if cube[0] > 0 else neg).add(abs(cube[0]))
            else:
                return True
        return bool(pos & neg)

    unsat_levels = [r["n"] for r in recs if r["step"].endswith("unsat")]
    bad_levels = [n for n in unsat_levels if not level_certified(n)]
    check(not bad_levels,
          f"DRAT cert verified for all {len(unsat_levels)} UNSAT levels"
          + (f" (uncertified: {bad_levels})" if bad_levels else ""))

    spot = sorted(unsat_levels)[:3]
    tgt = {r["n"]: r["target"] for r in recs if "target" in r}
    ok_spot = True
    with tempfile.TemporaryDirectory() as td:
        for n in spot:
            cnf = os.path.join(td, f"s{n}.cnf")
            drat = os.path.join(td, f"s{n}.drat")
            write_cnf(cnf, n, tgt[n])
            p = subprocess.run([KISSAT, "-q", cnf, drat],
                               capture_output=True, timeout=240)
            q = subprocess.run([DRATTRIM, cnf, drat],
                               capture_output=True, text=True, timeout=240)
            if p.returncode != 20 or "s VERIFIED" not in q.stdout:
                ok_spot = False
    check(ok_spot, f"spot re-solve+DRAT-recheck of UNSAT levels {spot}")

    lbs = []
    lbp = os.path.join(ROOT, "results", "lb.jsonl")
    if os.path.exists(lbp):
        lbs += [json.loads(l) for l in open(lbp) if l.strip()]
    ppath = os.path.join(ROOT, "results", "lb_prior_verified.json")
    if os.path.exists(ppath):
        lbs += list(json.load(open(ppath)).values())
    if lbs:
        ok_h = all(is_square_sidon(h["witness"])
                   and len(h["witness"]) == h["lower_bound"]
                   and max(h["witness"]) <= h["n"] for h in lbs)
        check(ok_h, f"all {len(lbs)} lower-bound witnesses are square-Sidon "
                    f"of claimed size")

    print()
    if fails:
        print(f"VERIFY: FAILED ({len(fails)}): {fails}")
        sys.exit(1)
    print(f"VERIFY: ALL CHECKS PASSED (exact table certified to N={Nstar}, "
          f"S({Nstar})={recs[-1]['S']})")


if __name__ == "__main__":
    main()
