"""Standalone DRAT certificate checker: verifies one proof with drat-trim
and appends the record to results/certs.jsonl (O_APPEND single-write, safe
for concurrent daemons). Deletes cnf+proof on success. Launched detached
by chain3.py --detached-certs; can also be run by hand.

Usage: cert_daemon.py CNF DRAT N TARGET NVARS NCLAUSES ENCODING [CAP_S]
"""

import hashlib, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
CERTS = os.path.join(ROOT, "results", "certs.jsonl")
DRATTRIM = os.path.join(HERE, "drat-trim")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    cnf, drat = sys.argv[1], sys.argv[2]
    n, t, nvars, ncl = map(int, sys.argv[3:7])
    encoding = sys.argv[7]
    cap = float(sys.argv[8]) if len(sys.argv) > 8 else 3000.0
    rec = {"n": n, "target": t, "nvars": nvars, "nclauses": ncl,
           "encoding": encoding, "cnf_sha256": sha256(cnf),
           "drat_bytes": os.path.getsize(drat), "drat_sha256": sha256(drat)}
    t0 = time.time()
    try:
        p = subprocess.run([DRATTRIM, cnf, drat], capture_output=True,
                           text=True, timeout=cap)
        rec["verified"] = "s VERIFIED" in p.stdout
    except subprocess.TimeoutExpired:
        rec["verified"] = False
        rec["error"] = "drat-trim timeout"
    rec["drat_trim_seconds"] = round(time.time() - t0, 2)
    if rec["verified"]:
        os.remove(drat)
        os.remove(cnf)
    fd = os.open(CERTS, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    os.write(fd, (json.dumps(rec) + "\n").encode())
    os.close(fd)
    print(f"[cert-daemon] N={n} verified={rec['verified']}")


if __name__ == "__main__":
    main()
