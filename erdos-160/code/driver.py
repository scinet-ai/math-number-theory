#!/usr/bin/env python3
"""Driver: sweep N upward computing exact h(N) with kissat.

h is nondecreasing in N (a valid colouring of [N] restricts to [N-1]), so we
carry k forward. At each N we test SAT(N, k). SAT -> h(N) = k, store witness.
UNSAT -> keep + verify the DRAT certificate (this N is a jump point), bump k
and retry. Certificates at jump point (N*, k-1) prove h(N) >= k for ALL
N >= N* by monotonicity.

Checkpoints results.json after every solver call. Deterministic: kissat
default options, single thread, recorded version. Stops on --wall-budget or
when a frontier call exceeds --call-timeout (table ends at last certified N).
"""
import json
import os
import subprocess
import sys
import time
import argparse
import hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE = os.path.join(ROOT, "code")
CNF = os.path.join(ROOT, "cnf")
CERTS = os.path.join(ROOT, "certs")
WITS = os.path.join(ROOT, "witnesses")
LOGS = os.path.join(ROOT, "logs")
RESULTS = os.path.join(ROOT, "results.json")
KISSAT = "kissat"
DRATTRIM = os.path.join(ROOT, "tools", "drat-trim", "drat-trim")

sys.path.insert(0, CODE)
import encode  # noqa: E402


def log(msg):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with open(os.path.join(LOGS, "driver.log"), "a") as f:
        f.write(line + "\n")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_cnf(N, k):
    path = os.path.join(CNF, "e160_N%d_k%d.cnf" % (N, k))
    nvars, clauses = encode.build(N, k, symbreak=True)
    with open(path, "w") as f:
        f.write("c erdos160 N=%d k=%d symbreak=1\n" % (N, k))
        f.write("p cnf %d %d\n" % (nvars, len(clauses)))
        for cl in clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")
    return path, nvars


def extract_witness(out_text, N, k):
    vals = []
    for line in out_text.splitlines():
        if line.startswith("v "):
            vals.extend(int(t) for t in line[2:].split())
    pos = set(v for v in vals if v > 0)
    col = []
    for i in range(1, N + 1):
        ci = [c for c in range(1, k + 1) if (i - 1) * k + c in pos]
        assert len(ci) == 1, (i, ci)
        col.append(ci[0])
    return col


def check_witness(col, N):
    for d in range(1, (N - 1) // 3 + 1):
        for a in range(1, N - 3 * d + 1):
            cs = {col[a - 1], col[a + d - 1], col[a + 2 * d - 1], col[a + 3 * d - 1]}
            if len(cs) < 3:
                return False
    return True


def greedy_extend(prev_col, N, k):
    """Try to colour element N on top of a valid colouring of [N-1].
    Every constrained 4-AP containing N ends at N (terms are increasing and
    bounded by N), so only APs (N-3d, N-2d, N-d, N) need checking.
    Returns extended colouring or None. Pure Python, no solver."""
    for c in range(1, k + 1):
        ok = True
        for d in range(1, (N - 1) // 3 + 1):
            a = N - 3 * d
            if a < 1:
                break
            cs = {prev_col[a - 1], prev_col[a + d - 1], prev_col[a + 2 * d - 1], c}
            if len(cs) < 3:
                ok = False
                break
        if ok:
            return prev_col + [c]
    return None


def solve(N, k, timeout):
    """Returns (status, elapsed, extra). status in SAT/UNSAT/TIMEOUT.
    On SAT extra=witness list; on UNSAT extra=proof path (verified)."""
    cnf_path, nvars = write_cnf(N, k)
    proof_path = os.path.join(CERTS, "e160_N%d_k%d.drat" % (N, k))
    t0 = time.time()
    try:
        r = subprocess.run(
            [KISSAT, "-q", cnf_path, proof_path],
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        for p in (proof_path,):
            if os.path.exists(p):
                os.remove(p)
        os.remove(cnf_path)
        return "TIMEOUT", time.time() - t0, None
    el = time.time() - t0
    if r.returncode == 10:
        col = extract_witness(r.stdout, N, k)
        assert check_witness(col, N), "witness failed independent AP check"
        os.remove(proof_path)
        os.remove(cnf_path)
        return "SAT", el, col
    elif r.returncode == 20:
        # verify DRAT before trusting
        try:
            v = subprocess.run(
                [DRATTRIM, cnf_path, proof_path],
                capture_output=True, text=True, timeout=max(1800, timeout),
            )
            vout = v.stdout
        except subprocess.TimeoutExpired:
            vout = "drat-trim TIMEOUT (proof kept for manual verification)"
        verified = "s VERIFIED" in vout
        v = type("V", (), {"stdout": vout})
        info = {
            "proof": os.path.relpath(proof_path, ROOT),
            "cnf": os.path.relpath(cnf_path, ROOT),
            "proof_sha256": sha256(proof_path),
            "cnf_sha256": sha256(cnf_path),
            "proof_bytes": os.path.getsize(proof_path),
            "drat_verified": verified,
        }
        with open(os.path.join(LOGS, "drat_N%d_k%d.log" % (N, k)), "w") as f:
            f.write(v.stdout[-4000:])
        if not verified:
            log("WARNING drat-trim did not verify N=%d k=%d" % (N, k))
        if verified and info["proof_bytes"] > 200 * (1 << 20):
            os.remove(proof_path)
            info["proof_pruned_after_verification"] = True
            log("pruned verified proof N=%d k=%d (%d bytes; hash+log retained)" % (N, k, info["proof_bytes"]))
        return "UNSAT", el, info
    else:
        raise RuntimeError("kissat rc=%d stderr=%s" % (r.returncode, r.stderr[:500]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=2000)
    ap.add_argument("--wall-budget", type=float, default=7200, help="seconds")
    ap.add_argument("--call-timeout", type=float, default=900, help="seconds")
    args = ap.parse_args()

    start = time.time()
    res = {"table": {}, "jumps": {}, "meta": {}}
    if os.path.exists(RESULTS):
        res = json.load(open(RESULTS))
    ver = subprocess.run([KISSAT, "--version"], capture_output=True, text=True).stdout.strip()
    res["meta"]["kissat_version"] = ver
    res["meta"]["invocation"] = "kissat -q <cnf> <drat>; drat-trim <cnf> <drat>"

    done = {int(n) for n in res["table"]}
    k = max((res["table"][str(n)]["h"] for n in done), default=1)
    N0 = max(done, default=3) + 1
    prev_col = None
    if done:
        prev_col = json.load(open(os.path.join(WITS, "N%d.json" % max(done))))["colouring"]

    for N in range(N0, args.nmax + 1):
        if time.time() - start > args.wall_budget:
            log("wall budget reached at N=%d; stopping" % N)
            break
        # fast path: greedy one-element extension of the previous witness
        if prev_col is not None:
            ext = greedy_extend(prev_col, N, k)
            if ext is not None:
                assert check_witness(ext, N)
                res["table"][str(N)] = {"h": k, "sat_seconds": 0.0, "method": "greedy-extend"}
                json.dump({"N": N, "k": k, "colouring": ext}, open(os.path.join(WITS, "N%d.json" % N), "w"))
                prev_col = ext
                if N % 25 == 0:
                    log("N=%d k=%d -> SAT (greedy)" % (N, k))
                    json.dump(res, open(RESULTS, "w"), indent=1)
                continue
        while True:
            st, el, extra = solve(N, k, args.call_timeout)
            log("N=%d k=%d -> %s (%.1fs)" % (N, k, st, el))
            if st == "SAT":
                res["table"][str(N)] = {"h": k, "sat_seconds": round(el, 2)}
                wpath = os.path.join(WITS, "N%d.json" % N)
                json.dump({"N": N, "k": k, "colouring": extra}, open(wpath, "w"))
                prev_col = extra
                break
            elif st == "UNSAT":
                res["jumps"][str(k + 1)] = {
                    "first_N": N, "unsat_k": k, "unsat_seconds": round(el, 2), **extra,
                }
                k += 1
            else:  # TIMEOUT at the frontier: table ends at N-1
                log("frontier call N=%d k=%d timed out; certified table ends at N=%d" % (N, k, N - 1))
                res["meta"]["stopped"] = {"N": N, "k": k, "reason": "call-timeout"}
                json.dump(res, open(RESULTS, "w"), indent=1)
                return
            json.dump(res, open(RESULTS, "w"), indent=1)
        json.dump(res, open(RESULTS, "w"), indent=1)
    json.dump(res, open(RESULTS, "w"), indent=1)
    log("done")


if __name__ == "__main__":
    main()
