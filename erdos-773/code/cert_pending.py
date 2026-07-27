"""Sweep scratch/ for solved-but-unverified DRAT proofs (left when the
detached-cert queue was full) and verify them sequentially with drat-trim,
appending records to results/certs.jsonl and deleting verified files.

CNF metadata (N, t, cube) is parsed from the file's 'c erdos773' comment
line; nvars/nclauses from the p-line.
"""

import hashlib, json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
CERTS = os.path.join(ROOT, "results", "certs.jsonl")
SCRATCH = os.path.join(ROOT, "scratch")
DRATTRIM = os.path.join(HERE, "drat-trim")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    cap = float(sys.argv[1]) if len(sys.argv) > 1 else 3600.0
    pairs = []
    for fn in sorted(os.listdir(SCRATCH)):
        if fn.endswith(".cnf"):
            drat = fn[:-4] + ".drat"
            if os.path.exists(os.path.join(SCRATCH, drat)):
                pairs.append((os.path.join(SCRATCH, fn),
                              os.path.join(SCRATCH, drat)))
    print(f"[pending] {len(pairs)} proof(s) to verify", flush=True)
    for cnf, drat in pairs:
        head = open(cnf).readline()
        m = re.search(r"N=(\d+) t=(\d+)(?: cube=(\[[-\d, ]*\]))?", head)
        if not m:
            print(f"[pending] skip {cnf}: no metadata", flush=True)
            continue
        n, t = int(m.group(1)), int(m.group(2))
        cube = json.loads(m.group(3)) if m.group(3) else None
        with open(cnf) as f:
            for line in f:
                if line.startswith("p cnf"):
                    nvars, ncl = map(int, line.split()[2:4])
                    break
        enc = "profile-v2" + (f"-cube:{json.dumps(cube)}" if cube else "")
        rec = {"n": n, "target": t, "nvars": nvars, "nclauses": ncl,
               "encoding": enc, "cnf_sha256": sha256(cnf),
               "drat_bytes": os.path.getsize(drat),
               "drat_sha256": sha256(drat)}
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
        print(f"[pending] N={n} cube={cube} verified={rec['verified']} "
              f"({rec['drat_trim_seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
