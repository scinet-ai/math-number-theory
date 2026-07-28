#!/usr/bin/env python3
"""Sharded driver for erdos700. Cost per n grows superlinearly (hard-n tail), so
shard boundaries use equal sum(n^2); heaviest shards first. Default 4-way parallel
per the fleet CPU pact of 2026-07-27 (wave D/E + kissat runs own the other cores)."""
import concurrent.futures
import json
import os
import subprocess
import sys
import time

BIN = os.path.join(os.path.dirname(__file__), "erdos700")

def main():
    N = int(sys.argv[1])
    K = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    jobs = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    outdir = sys.argv[4] if len(sys.argv) > 4 else "."
    bounds = [4]
    for t in range(1, K + 1):
        b = round((t / K) ** (1 / 3) * N)
        if b > bounds[-1]:
            bounds.append(b)
    shards = [(bounds[t] + (1 if t else 0), bounds[t + 1]) for t in range(len(bounds) - 1)]
    shards.sort(key=lambda s: -s[1])
    print(f"N={N}: {len(shards)} shards, {jobs}-way (fleet pact)", flush=True)

    t0 = time.time()
    totals = {"composites": 0, "bigs": 0}
    bigs, ftab = [], []
    done = 0

    def run(sh):
        lo, hi = sh
        t = time.time()
        r = subprocess.run([BIN, str(N), str(lo), str(hi), "1"],
                           capture_output=True, text=True)
        return lo, hi, r.returncode, r.stdout, time.time() - t

    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        for lo, hi, rc, out, dt in ex.map(run, shards):
            if rc != 0:
                print(f"SHARD FAIL [{lo},{hi}] rc={rc}", flush=True)
                sys.exit(1)
            done += 1
            for ln in out.splitlines():
                if ln.startswith("CERT"):
                    parts = dict(p.split("=") for p in ln.split()[3:])
                    for key in totals:
                        totals[key] += int(parts[key])
                elif ln.startswith("BIG"):
                    bigs.append(ln)
                elif ln.startswith("F"):
                    ftab.append(ln)
            print(f"  shard [{lo},{hi}] {dt:.0f}s ({done}/{len(shards)}, "
                  f"{time.time()-t0:.0f}s)", flush=True)

    bigs.sort(key=lambda l: int(l.split()[1]))
    ftab.sort(key=lambda l: int(l.split()[1]))
    with open(os.path.join(outdir, f"ftable_N{N}.txt"), "w") as f:
        f.write("\n".join(ftab) + "\n")
    with open(os.path.join(outdir, f"result_N{N}.json"), "w") as f:
        json.dump({"N": N, **totals, "bigs": [l.split()[1:] for l in bigs],
                   "wall_seconds": round(time.time() - t0, 1)}, f, indent=1)
    print(f"DONE N={N} composites={totals['composites']:,} bigs={totals['bigs']} "
          f"wall={time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    main()
