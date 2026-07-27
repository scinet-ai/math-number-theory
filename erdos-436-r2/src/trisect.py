#!/usr/bin/env python3
"""Checkpointed parallel interval search for the exact Lambda(8,2).

Maintains the invariant  lo = SAT (admissible assignment exists)
and  hi = UNSAT (no admissible assignment).  Terminates when hi - lo = 1,
at which point Lambda(8,2) = lo + 1 = hi.

Round-2 revision after the killed first launch:
  * kissat is run with --lucky=0: the lucky phase was observed to burn
    27 CPU-minutes on B=1499875 (24e9 propagations, zero conflicts)
    before SIGTERM; disabling it gets the real search started at once.
  * --time=3300 safety cap per solve; a timeout at an interior probe
    halts the search gracefully (state is saved), a timeout at the
    initial lo just marks it uncertified and continues.
  * probes are skewed LOW (lo + gap/6, lo + gap/3) instead of even
    thirds: Reble's 2019 lower-bound vector is expected to be optimal
    or near-optimal (as the analogous published vectors were for
    k = 2..7), so the true value should sit near lo; if both probes
    come back UNSAT the interval shrinks 6x per round instead of 3x.
  * the initial lo = 1499875 (Reble's bound is lo+1 = 1499876) starts
    UNcertified; round 1 spends one of its two solver slots re-solving
    it so the final chain rests on OUR certificate, not the citation.
    Its CNF from the killed run is reused if present.
  * the two probe CNFs of a round are encoded in parallel.

At most 2 solver processes + brief encoder subprocesses (machine shared
with sibling agents).  State goes to results/trisect_state.json after
EVERY verdict; every SAT probe is immediately decoded and independently
verified; CNFs are deleted after use; model lines are stripped from the
solver logs.  Safe to kill and restart at any time.

Usage: trisect.py [--deadline-epoch E]
"""
import json
import os
import subprocess
import sys
import time

K, M = 8, 2
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "results", "trisect_state.json")
LOG = os.path.join(ROOT, "results", "trisect_log.txt")
ENC = os.path.join(ROOT, "src", "encode_v2.py")
VER = os.path.join(ROOT, "src", "verify_certificate_v2.py")
KISSAT_ARGS = ["kissat", "--lucky=0", "--time=3300"]


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as fh:
        fh.write(line + "\n")


def load_state():
    with open(STATE) as fh:
        return json.load(fh)


def save_state(st):
    tmp = STATE + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(st, fh, indent=1)
    os.replace(tmp, STATE)


def encode_parallel(bs):
    """Encode all bounds in bs concurrently; return {b: cnf_path}."""
    cnfs, procs = {}, []
    for b in bs:
        cnf = os.path.join(ROOT, "cnf", f"k8_B{b}.cnf")
        cnfs[b] = cnf
        if not os.path.exists(cnf):
            # encode to .tmp then rename, so a killed run can never leave a
            # truncated CNF that a resume would mistake for a complete one
            procs.append((b, cnf, subprocess.Popen(
                [sys.executable, ENC, "encode", str(K), str(M), str(b), cnf + ".tmp"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)))
    for b, cnf, p in procs:
        if p.wait() != 0:
            log(f"ENCODER FAILED for B={b}")
            sys.exit(1)
        os.replace(cnf + ".tmp", cnf)
    return cnfs


def launch(b, cnf):
    out = os.path.join(ROOT, "results", f"sat_k8_B{b}.out")
    fh = open(out, "w")
    t0 = time.time()
    proc = subprocess.Popen(KISSAT_ARGS + [cnf], stdout=fh,
                            stderr=subprocess.STDOUT)
    return {"b": b, "cnf": cnf, "out": out, "fh": fh, "proc": proc, "t0": t0}


def finish(job):
    rc = job["proc"].wait()
    job["fh"].close()
    dt = time.time() - job["t0"]
    verdict = {10: "SAT", 20: "UNSAT"}.get(rc, f"rc={rc}")
    if verdict == "SAT":
        cert = os.path.join(ROOT, "certs", f"k8_B{job['b']}_cert.txt")
        subprocess.run([sys.executable, ENC, "decode", str(K), str(M), str(job["b"]),
                        job["out"], cert], check=True, capture_output=True)
        v = subprocess.run([sys.executable, VER, cert], capture_output=True, text=True)
        if v.returncode != 0:
            log(f"B={job['b']}: SAT but CERT VERIFICATION FAILED: {v.stdout}{v.stderr}")
            sys.exit(1)
        log(f"B={job['b']}: SAT in {dt:.1f}s, certificate verified ({cert})")
        # strip huge model lines from the solver log, keep header/stats
        subprocess.run(f"grep -v '^v ' '{job['out']}' > '{job['out']}.slim' && "
                       f"mv '{job['out']}.slim' '{job['out']}'", shell=True)
    else:
        log(f"B={job['b']}: {verdict} in {dt:.1f}s")
    os.unlink(job["cnf"])
    return verdict, dt


def pick_probes(st):
    lo, hi = st["lo"], st["hi"]
    gap = hi - lo
    probes = []
    if not st.get("lo_certified"):
        probes.append(lo)
    # neutral trisection: probes at thirds guarantee the interval shrinks
    # 3x per round WHATEVER the verdicts are.  (The first launch skewed the
    # probes low on the prior that Reble's lower-bound vector was optimal;
    # round 1 refuted that prior — B = 1501283 is SAT — so neutral it is.)
    c1 = lo + max(1, gap // 3)
    c2 = lo + max(2, (2 * gap) // 3)
    for c in (c1, c2):
        if lo < c < hi and c not in probes and len(probes) < 2:
            probes.append(c)
    return probes


def main():
    deadline = None
    if "--deadline-epoch" in sys.argv:
        deadline = float(sys.argv[sys.argv.index("--deadline-epoch") + 1])
    st = load_state()
    while st["hi"] - st["lo"] > 1:
        if deadline and time.time() > deadline:
            log(f"deadline reached; stopping with interval [{st['lo']}, {st['hi']}]")
            return 2
        probes = pick_probes(st)
        log(f"interval [{st['lo']}, {st['hi']}] gap={st['hi']-st['lo']}: probing {probes}")
        cnfs = encode_parallel(probes)
        jobs = [launch(p, cnfs[p]) for p in probes]
        results = {}
        for job in jobs:
            results[job["b"]], dt = finish(job)
            st["history"].append({"B": job["b"], "verdict": results[job["b"]],
                                  "seconds": round(dt, 1)})
            save_state(st)
        for p in sorted(probes):
            v = results[p]
            if p == st["lo"]:
                if v == "SAT":
                    st["lo_certified"] = True
                elif v == "UNSAT":
                    log(f"CONTRADICTION: initial lo B={p} is UNSAT, i.e. "
                        f"Lambda(8,2) <= {p} < Reble's lower bound. HALTING "
                        f"for manual review.")
                    save_state(st)
                    return 4
                else:
                    log(f"lo B={p} verdict {v} (timeout?); continuing uncertified")
                    st["lo_certified"] = "timeout"
            elif v == "SAT":
                st["lo"] = max(st["lo"], p)
                st["lo_certified"] = True   # our own verified certificate
            elif v == "UNSAT":
                st["hi"] = min(st["hi"], p)
            else:
                log(f"unexpected verdict at B={p}: {v}; halting (state saved)")
                save_state(st)
                return 3
        save_state(st)
    log(f"largest SAT B = {st['lo']} (certified={st.get('lo_certified')}), "
        f"smallest UNSAT B = {st['hi']}")
    if st.get("lo_certified") is True:
        log(f"DONE: Lambda(8,2) = {st['hi']}")
    else:
        log(f"interval closed but lo NOT self-certified; re-run to certify")
    return 0


if __name__ == "__main__":
    sys.exit(main())
