"""Kick-and-refill local search over 4-free-mod-b digit sets at a fixed base.

Usage:  python3 search.py <label> <seconds> <rng_seed>

Labels select (base, seed digit set) pairs built from Walker's published sets
via the product construction (see products_scan.py / README.md).  The search
objective is float(certified lower bound) of H(K(S,b)+1) at a per-base depth,
so every reported value is a genuine lower bound at that depth.  Moves:
  KICK: remove 1-3 random non-zero digits (biased toward large digits),
  FILL: re-add addable digits greedily/randomly until the set is maximal,
accepted by Metropolis; the best state is checkpointed every minute and on
every improvement (results/anneal_<label>.json), so runs are resumable.
"""
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from kempner import (harmonic_sum_bounds, addable_digits, digit_is_addable,
                     is_kfree_mod, product_digit_set,
                     WALKER_S11, WALKER_S22, WALKER_S55)
import numpy as np

ROOT = __file__.rsplit("/", 2)[0]

SEEDS = {
    # label: (base, seed_set_builder, eval_depth)
    "3025sq":  (3025, lambda: product_digit_set(WALKER_S55, 55, WALKER_S55), 2),
    "3025sq2": (3025, lambda: product_digit_set(WALKER_S55, 55, WALKER_S55), 2),
    "605a":    (605,  lambda: product_digit_set(WALKER_S55, 55, WALKER_S11), 3),
    "605b":    (605,  lambda: product_digit_set(WALKER_S11, 11, WALKER_S55), 3),
    "1210a":   (1210, lambda: product_digit_set(WALKER_S55, 55, WALKER_S22), 2),
    "1210b":   (1210, lambda: product_digit_set(WALKER_S22, 22, WALKER_S55), 2),
}


def evaluate(S, b, depth):
    lo, _ = harmonic_sum_bounds(S, b, depth)
    return float(lo)


def refill(S_mask, b, rng):
    """Add addable digits until maximal; random order, small-digit biased."""
    S = sorted(np.flatnonzero(S_mask).tolist())
    cands = addable_digits(S, b, 4)
    while cands:
        # bias toward small digits (bigger harmonic contribution)
        weights = [1.0 / (c + 2) for c in cands]
        tot = sum(weights)
        r = rng.random() * tot
        acc = 0.0
        pick = cands[-1]
        for c, w in zip(cands, weights):
            acc += w
            if acc >= r:
                pick = c
                break
        S_mask[pick] = True
        cands = [c for c in cands
                 if c != pick and digit_is_addable(S_mask, b, c, 4)]
    return S_mask


def run(label, seconds, rng_seed):
    b, builder, depth = SEEDS[label]
    ckpt_path = f"{ROOT}/results/anneal_{label}.json"
    rng = random.Random(rng_seed)

    seed = builder()
    assert is_kfree_mod(seed, b, 4)
    if os.path.exists(ckpt_path):
        with open(ckpt_path) as f:
            ck = json.load(f)
        cur = ck["best_S"]
        print(f"[{label}] resuming from checkpoint H={ck['best_H']:.7f}")
    else:
        cur = seed
    H_cur = evaluate(cur, b, depth)
    best_S, H_best = list(cur), H_cur
    H_seed = evaluate(seed, b, depth)
    print(f"[{label}] b={b} depth={depth} seed H_lo={H_seed:.7f} "
          f"start H_lo={H_cur:.7f}", flush=True)

    T0, T1 = 3e-4, 1e-6
    t_start = time.time()
    t_ckpt = t_start
    kicks = since_improve = 0
    mask = np.zeros(b, dtype=bool)

    while time.time() - t_start < seconds:
        frac = (time.time() - t_start) / seconds
        T = T0 * (T1 / T0) ** frac
        kicks += 1

        mask[:] = False
        mask[cur] = True
        removable = [s for s in cur if s != 0]
        r = rng.choice([1, 1, 2, 2, 3])
        # bias removals toward large digits (cheap to lose, may unblock)
        for _ in range(r):
            if not removable:
                break
            if rng.random() < 0.7:
                pool = sorted(removable)[len(removable) // 2:]
            else:
                pool = removable
            drop = rng.choice(pool)
            removable.remove(drop)
            mask[drop] = False

        mask = refill(mask, b, rng)
        cand = sorted(np.flatnonzero(mask).tolist())
        H_cand = evaluate(cand, b, depth)

        if H_cand >= H_cur or rng.random() < math.exp((H_cand - H_cur) / T):
            cur, H_cur = cand, H_cand
        if H_cand > H_best + 1e-12:
            best_S, H_best = list(cand), H_cand
            since_improve = 0
            print(f"[{label}] kick {kicks}: NEW BEST H_lo={H_best:.9f} "
                  f"m={len(best_S)} (+{H_best - H_seed:+.2e} vs seed)",
                  flush=True)
        else:
            since_improve += 1
        if since_improve > 400:  # stagnation: jump back to best
            cur, H_cur = list(best_S), H_best
            since_improve = 0

        if time.time() - t_ckpt > 60 or since_improve == 0:
            t_ckpt = time.time()
            with open(ckpt_path, "w") as f:
                json.dump({"label": label, "b": b, "depth": depth,
                           "rng_seed": rng_seed, "kicks": kicks,
                           "seed_H": H_seed, "best_H": H_best,
                           "best_S": best_S,
                           "elapsed": time.time() - t_start}, f)

    with open(ckpt_path, "w") as f:
        json.dump({"label": label, "b": b, "depth": depth,
                   "rng_seed": rng_seed, "kicks": kicks,
                   "seed_H": H_seed, "best_H": H_best, "best_S": best_S,
                   "elapsed": time.time() - t_start, "done": True}, f)
    print(f"[{label}] finished: {kicks} kicks, best H_lo={H_best:.9f} "
          f"(seed {H_seed:.7f}, record bar 4.439753370)", flush=True)


if __name__ == "__main__":
    run(sys.argv[1], float(sys.argv[2]), int(sys.argv[3]))
