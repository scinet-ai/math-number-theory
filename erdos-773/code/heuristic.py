"""Heuristic lower bounds for S(N) at N beyond the certified exact range.

Randomized greedy + insert-with-repair local search (GRASP-style), fixed
seed, exact integer arithmetic. Witnesses checkpointed per N to
results/heuristic.jsonl (best-so-far, one line per improvement).

Usage: heuristic.py --ns 100,150,200,300,500,750,1000 --seconds-per-n 90
"""

import argparse, json, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sidon_common import is_square_sidon

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "results", "heuristic.jsonl")


class SidonSet:
    """Incremental square-Sidon set over roots 1..N. Exact int arithmetic."""

    def __init__(self):
        self.members = set()
        self.pair_of = {}  # sum value -> (i,j) with i<=j, both in members

    def blockers(self, r):
        """Elements that collide if r is inserted; None if r's own sums
        collide internally (cannot insert even after removals of others)."""
        rr = r * r
        sums = [2 * rr] + [rr + m * m for m in self.members]
        if len(sums) != len(set(sums)):
            return None
        bl = set()
        for s in sums:
            if s in self.pair_of:
                i, j = self.pair_of[s]
                bl.add(i)
                bl.add(j)
        bl.discard(r)
        return bl

    def insert(self, r):
        rr = r * r
        for m in list(self.members) + [r]:
            self.pair_of[rr + m * m] = (min(r, m), max(r, m))
        self.members.add(r)

    def remove(self, r):
        self.members.discard(r)
        dead = [s for s, (i, j) in self.pair_of.items() if i == r or j == r]
        for s in dead:
            del self.pair_of[s]


def grasp(N, seconds, rng):
    best = []
    deadline = time.time() + seconds
    while time.time() < deadline:
        S = SidonSet()
        order = list(range(1, N + 1))
        rng.shuffle(order)
        for r in order:  # randomized greedy
            b = S.blockers(r)
            if b is not None and not b:
                S.insert(r)
        # insert-with-repair local search
        stall = 0
        while time.time() < deadline and stall < 4000:
            r = rng.randint(1, N)
            if r in S.members:
                stall += 1
                continue
            b = S.blockers(r)
            if b is None:
                stall += 1
                continue
            if len(b) == 0:
                S.insert(r)
                stall = 0
            elif len(b) == 1 and rng.random() < 0.5:
                S.remove(next(iter(b)))
                b2 = S.blockers(r)
                if b2 is not None and not b2:
                    S.insert(r)
                stall += 1
            else:
                stall += 1
        if len(S.members) > len(best):
            best = sorted(S.members)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", type=str, default="100,150,200,300,500,750,1000")
    ap.add_argument("--seconds-per-n", type=float, default=90.0)
    ap.add_argument("--seed", type=int, default=773)
    args = ap.parse_args()
    for N in [int(x) for x in args.ns.split(",")]:
        rng = random.Random(args.seed * 1000003 + N)
        t0 = time.time()
        w = grasp(N, args.seconds_per_n, rng)
        assert is_square_sidon(w) and (not w or w[-1] <= N)
        rec = {"n": N, "lower_bound": len(w), "witness": w,
               "wall": round(time.time() - t0, 1),
               "method": "grasp", "seed": args.seed}
        with open(OUT, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"[heur] N={N} S>={len(w)} ({rec['wall']}s)", flush=True)


if __name__ == "__main__":
    main()
