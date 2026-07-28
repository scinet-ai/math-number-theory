#!/usr/bin/env python3
"""Upper-bound sweep: for N beyond the certified table, find witnesses with
the fewest colours local search can manage, seeding from the previous N's
witness. Records ub(N) results in ub_results.json (upper bounds ONLY)."""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "code"))
import localsearch as LS

OUT = os.path.join(ROOT, "ub_results.json")


def main():
    n_start, n_end, k_lo = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    iters = int(sys.argv[4]) if len(sys.argv) > 4 else 1500000
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    prev = None
    pw = os.path.join(ROOT, "witnesses", "N%d.json" % (n_start - 1))
    if os.path.exists(pw):
        prev = json.load(open(pw))["colouring"]
    k = k_lo
    for N in range(n_start, n_end + 1):
        col = None
        for kk in range(k, k + 3):
            for seed in (1, 2, 3):
                col = LS.solve(N, kk, seed, iters, prev)
                if col:
                    break
            if col:
                k = kk
                break
        if not col:
            print("N=%d: no witness up to k=%d; stopping" % (N, k + 2), flush=True)
            break
        for ap in LS.all_aps(N):
            assert len({col[t - 1] for t in ap}) >= 3
        res[str(N)] = {"ub": k}
        json.dump({"N": N, "k": k, "colouring": col, "method": "localsearch"},
                  open(os.path.join(ROOT, "witnesses", "ub_N%d_k%d.json" % (N, k)), "w"))
        json.dump(res, open(OUT, "w"), indent=0)
        print("N=%d ub=%d" % (N, k), flush=True)
        prev = col
    print("sweep done", flush=True)


if __name__ == "__main__":
    main()
