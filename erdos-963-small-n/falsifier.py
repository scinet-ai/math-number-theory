#!/usr/bin/env python3
"""
Randomized falsifier for the claimed f(n) table (Erdős #963).

f(n) is a min over ALL n-element real sets, so ANY set with md(A) < f_claimed(n)
would disprove the table's lower-bound side. We hammer the claim with random and
structured integer sets (including 0, sign-pairs, dilates, unions of scales,
2-D lattice projections). Every trial asserts md(A) >= f_claimed(n).

Also: probe mode searches for a 13-class set with md <= 4 (which would prove
h(13) = 4 and extend the table to n = 27). Local search over integer sets.
"""
import random, sys
from itertools import combinations

CLAIMED_F = {1:0, 2:1, 3:1, 4:2, 5:2, 6:2, 7:2, 8:3, 9:3, 10:3, 11:3, 12:3,
             13:3, 14:4, 15:4, 16:4, 17:4, 18:4, 19:4, 20:4, 21:4, 22:4,
             23:4, 24:4, 25:4, 26:4, 27:4}

def is_dissociated(B):
    sums = set()
    for mask in range(1 << len(B)):
        s = sum(B[i] for i in range(len(B)) if mask >> i & 1)
        if s in sums:
            return False
        sums.add(s)
    return True

def has_diss_of_size(A, k):
    return any(is_dissociated(B) for B in combinations(A, k))

def md_at_least(A, k):
    return has_diss_of_size(A, k)

def random_set(rng, n):
    style = rng.randrange(6)
    if style == 0:
        M = max(n, rng.choice([10, 30, 100, 1000]))
        pool = list(range(-M, M + 1))
        return rng.sample(pool, n)
    if style == 1:  # heavy sign-pairing + 0
        m = (n - 1 + 1) // 2
        M = rng.choice([m + 2, 3 * m, 50])
        U = rng.sample(range(1, M + 1), m)
        A = [0]
        p = n - 1 - m
        for u in U[:p]:
            A += [u, -u]
        A += U[p:]
        return A
    if style == 2:  # two scales
        M = rng.choice([5, 8, 12])
        big = rng.choice([1000, 10000])
        a = rng.sample(range(1, M + 1), min(n // 2, M))
        rest = n - len(a)
        b = rng.sample(range(1, 50), rest)
        return [x for x in a] + [big * x for x in b]
    if style == 3:  # 2-D lattice projection u·(1,T), T large
        T = 10 ** 5
        pts = set()
        while len(pts) < n:
            pts.add((rng.randint(-6, 6), rng.randint(-6, 6)))
        return [x + T * y for (x, y) in pts]
    if style == 4:  # arithmetic-progression-ish
        d = rng.randint(1, 5)
        a0 = rng.randint(-20, 20)
        return [a0 + d * i for i in range(n)]
    # random small with duplicates-of-negation encouraged
    vals = []
    while len(set(vals)) < n:
        v = rng.randint(1, n + 3) * rng.choice([-1, 1])
        vals.append(v)
        vals = list(set(vals))
    return vals[:n] if len(vals) >= n else vals + [0]

def falsify(trials, seed):
    rng = random.Random(seed)
    worst = {}
    for t in range(trials):
        n = rng.randint(1, 27)
        A = random_set(rng, n)
        A = list(dict.fromkeys(A))
        n = len(A)
        if n < 1 or n > 27:
            continue
        k = CLAIMED_F[n]
        if k == 0:
            continue
        if not md_at_least(A, k):
            print(f"FALSIFIED f({n}) >= {k} by A = {sorted(A)}")
            return False
        worst[n] = worst.get(n, 0) + 1
    print(f"falsifier: {trials} trials, no counterexample; per-n coverage: "
          f"{ {k: worst[k] for k in sorted(worst)} }")
    return True

def probe_h(seed, iters, m):
    """Search for m distinct positive integers (class-distinct by positivity)
    with NO dissociated 5-subset. Found => h(m) = 4 => f(2m) = f(2m+1) = 4."""
    rng = random.Random(seed)
    best = None
    for M in (m + 5, m + 7, m + 11, 2 * m + 4, 3 * m):
        for it in range(iters):
            A = sorted(rng.sample(range(1, M + 1), m))
            # local search: count dissociated 5-subsets, try to reduce
            def bad_count(S):
                c = 0
                for B in combinations(S, 5):
                    if is_dissociated(B):
                        c += 1
                        if c > 40:
                            return c
                return c
            cur = A
            cb = bad_count(cur)
            for step in range(200):
                if cb == 0:
                    break
                i = rng.randrange(m)
                x = rng.randint(1, M)
                if x in cur:
                    continue
                nxt = sorted(cur[:i] + [x] + cur[i+1:])
                if len(set(nxt)) < m:
                    continue
                nb = bad_count(nxt)
                if nb <= cb:
                    cur, cb = nxt, nb
            if cb == 0:
                # exhaustive confirmation with the plain definition
                assert not any(is_dissociated(B) for B in combinations(cur, 5))
                print(f"FOUND md<=4 {m}-class set: {cur}")
                return cur
            if best is None or cb < best[0]:
                best = (cb, cur)
    print(f"h({m}) probe: no md<=4 {m}-class set found; best had {best[0]}+ "
          f"dissociated 5-subsets: {best[1]}")
    return None

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'falsify'
    if cmd == 'falsify':
        trials = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
        seed = int(sys.argv[3]) if len(sys.argv) > 3 else 963
        ok = falsify(trials, seed)
        sys.exit(0 if ok else 1)
    elif cmd == 'probe':
        m = int(sys.argv[2])
        iters = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        probe_h(963, iters, m)
