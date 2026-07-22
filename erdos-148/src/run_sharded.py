#!/usr/bin/env python3
"""Sharded runner: split the k=8 computation into depth-D prefix jobs and sum.

The C binary itself emits the depth-D prefixes its DFS would visit (--enum D),
so the sharding uses the binary's own loop bounds — no second implementation of
the bound logic that could drift. Each job = one prefix subtree, one process.
"""
import concurrent.futures
import json
import os
import subprocess
import sys
import time

BIN = os.path.join(os.path.dirname(__file__), "erdos148")


def main():
    k = int(sys.argv[1])
    variant = sys.argv[2]
    depth = int(sys.argv[3])
    jobs = int(sys.argv[4]) if len(sys.argv) > 4 else max(2, (os.cpu_count() or 4) - 2)
    outdir = sys.argv[5] if len(sys.argv) > 5 else "."

    t0 = time.time()
    prefixes = subprocess.run(
        [BIN, "-k", str(k), "-v", variant, "--enum", str(depth)],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    print(f"[{variant} k={k}] {len(prefixes)} prefix jobs at depth {depth}, "
          f"{jobs}-way parallel", flush=True)

    total = 0
    log = []
    done = 0

    def run(px):
        t = time.time()
        r = subprocess.run([BIN, "-k", str(k), "-v", variant, "--prefix", px],
                           capture_output=True, text=True)
        return px, r.returncode, r.stdout.strip(), r.stderr.strip(), time.time() - t

    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        for px, rc, out, err, dt in ex.map(run, prefixes):
            if rc != 0:
                print(f"JOB FAILED rc={rc} prefix={px}: {err}", flush=True)
                sys.exit(1)
            c = int(out)
            total += c
            done += 1
            log.append({"prefix": px, "count": c, "sec": round(dt, 3), "stats": err})
            if done % 200 == 0 or dt > 60:
                print(f"  {done}/{len(prefixes)} jobs, running total {total:,} "
                      f"({time.time()-t0:.0f}s elapsed; last {px}: {c:,} in {dt:.1f}s)",
                      flush=True)

    wall = time.time() - t0
    res = {"k": k, "variant": variant, "depth": depth, "total": total,
           "n_jobs": len(prefixes), "wall_seconds": round(wall, 1),
           "cpu_seconds": round(sum(j["sec"] for j in log), 1), "jobs": log}
    path = os.path.join(outdir, f"result_k{k}_{variant}.json")
    with open(path, "w") as f:
        json.dump(res, f, indent=0)
    print(f"TOTAL {variant} k={k}: {total:,}   wall {wall:.0f}s  -> {path}", flush=True)


if __name__ == "__main__":
    main()
