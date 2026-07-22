#!/usr/bin/env python3
"""Sharded driver for erdos699: split [2, N] into chunks of equal sum(n^2) cost
(cost per n scales ~n^2), run 12-way, merge census + CERT totals."""
import concurrent.futures
import json
import os
import subprocess
import sys
import time

BIN = os.path.join(os.path.dirname(__file__), "erdos699")

def main():
    N = int(sys.argv[1])
    K = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    jobs = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    outdir = sys.argv[4] if len(sys.argv) > 4 else "."

    # equal-cost boundaries: cumulative n^3 thirds
    bounds = [2]
    for k in range(1, K + 1):
        b = round((k / K) ** (1 / 3) * N)
        if b > bounds[-1]:
            bounds.append(b)
    shards = [(bounds[t] + (1 if t else 0), bounds[t + 1]) for t in range(len(bounds) - 1)]
    # heaviest (highest-n) shards first for balance
    shards.sort(key=lambda s: -s[1])
    print(f"N={N}: {len(shards)} shards, {jobs}-way", flush=True)

    t0 = time.time()
    lines, totals = [], {"pairs": 0, "weak": 0, "strong": 0, "anomalies": 0}
    done = 0

    def run(sh):
        lo, hi = sh
        t = time.time()
        r = subprocess.run([BIN, str(N), str(lo), str(hi)], capture_output=True, text=True)
        return lo, hi, r.returncode, r.stdout, r.stderr, time.time() - t

    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        for lo, hi, rc, out, err, dt in ex.map(run, shards):
            if rc != 0:
                print(f"SHARD FAIL [{lo},{hi}] rc={rc}: {err}", flush=True)
                sys.exit(1)
            done += 1
            for ln in out.splitlines():
                if ln.startswith("CERT"):
                    parts = dict(p.split("=") for p in ln.split()[3:])
                    for key in totals:
                        totals[key] += int(parts[key])
                else:
                    lines.append(ln)
                    print("CENSUS:", ln, flush=True)
            print(f"  shard [{lo},{hi}] done in {dt:.0f}s ({done}/{len(shards)}, "
                  f"{time.time()-t0:.0f}s elapsed)", flush=True)

    lines.sort(key=lambda l: [int(x) for x in l.split()[1:]])
    res = {"N": N, **totals, "census": lines,
           "wall_seconds": round(time.time() - t0, 1)}
    with open(os.path.join(outdir, f"result_N{N}.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(f"DONE N={N} pairs={totals['pairs']:,} weak={totals['weak']} "
          f"strong={totals['strong']} anomalies={totals['anomalies']} "
          f"wall={time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    main()
