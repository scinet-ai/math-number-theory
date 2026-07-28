#!/usr/bin/env python3
"""Min-conflicts local search for upper-bound witnesses (no exactness claim).

Given (N, k) and optionally a seed colouring of a smaller N, searches for a
colouring of [N] where every 4-AP sees >= 3 distinct colours. Success yields
a *witness* (upper bound h(N) <= k) that is independently checkable; failure
proves nothing. Deterministic for a fixed --seed.

Usage: localsearch.py N k [--seed S] [--iters I] [--init witnesses/Nxx.json]
Writes witnesses/ub_N<N>_k<k>.json on success, exits 0; exits 1 on failure.
"""
import argparse
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def all_aps(N):
    out = []
    for d in range(1, (N - 1) // 3 + 1):
        for a in range(1, N - 3 * d + 1):
            out.append((a, a + d, a + 2 * d, a + 3 * d))
    return out


def violated(ap, col):
    return len({col[ap[0] - 1], col[ap[1] - 1], col[ap[2] - 1], col[ap[3] - 1]}) < 3


def solve(N, k, seed, iters, init):
    rng = random.Random(seed)
    aps = all_aps(N)
    aps_by_elem = [[] for _ in range(N + 1)]
    for idx, ap in enumerate(aps):
        for t in ap:
            aps_by_elem[t].append(idx)

    if init:
        col = list(init[:N]) + [rng.randint(1, k) for _ in range(max(0, N - len(init)))]
        col = [c if 1 <= c <= k else rng.randint(1, k) for c in col]
    else:
        col = [rng.randint(1, k) for _ in range(N)]

    viol = set(i for i, ap in enumerate(aps) if violated(ap, col))
    best = len(viol)
    for it in range(iters):
        if not viol:
            return col
        idx = rng.choice(tuple(viol))
        elem = rng.choice(aps[idx])
        # best recolouring of elem by local delta
        cur = col[elem - 1]
        best_c, best_delta = None, None
        for c in rng.sample(range(1, k + 1), k):
            if c == cur:
                continue
            delta = 0
            col[elem - 1] = c
            for j in aps_by_elem[elem]:
                v_new = violated(aps[j], col)
                v_old = j in viol
                delta += v_new - v_old
            col[elem - 1] = cur
            if best_delta is None or delta < best_delta:
                best_delta, best_c = delta, c
        # accept best move (min-conflicts; sideways/uphill allowed with noise)
        if best_delta is not None and (best_delta <= 0 or rng.random() < 0.15):
            col[elem - 1] = best_c
            for j in aps_by_elem[elem]:
                if violated(aps[j], col):
                    viol.add(j)
                else:
                    viol.discard(j)
        best = min(best, len(viol))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("N", type=int)
    ap.add_argument("k", type=int)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--iters", type=int, default=2000000)
    ap.add_argument("--init", default=None)
    args = ap.parse_args()

    init = None
    if args.init:
        init = json.load(open(args.init))["colouring"]
    col = solve(args.N, args.k, args.seed, args.iters, init)
    if col is None:
        print("FAIL N=%d k=%d seed=%d" % (args.N, args.k, args.seed))
        sys.exit(1)
    # independent check
    for a, b, c, d in all_aps(args.N):
        assert len({col[a - 1], col[b - 1], col[c - 1], col[d - 1]}) >= 3
    out = os.path.join(ROOT, "witnesses", "ub_N%d_k%d.json" % (args.N, args.k))
    json.dump({"N": args.N, "k": args.k, "colouring": col,
               "method": "localsearch", "seed": args.seed}, open(out, "w"))
    print("OK N=%d k=%d seed=%d -> %s" % (args.N, args.k, args.seed, out))


if __name__ == "__main__":
    main()
