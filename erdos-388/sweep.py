#!/usr/bin/env python3
"""Erdos #388 exhaustive collision sweep (reference implementation, exact bigint).

Enumerates EVERY block of k >= 4 consecutive integers starting at s >= SMIN
whose product is <= N, via a k-way sorted merge (heapq.merge) over the
per-length streams (for fixed k the product is strictly increasing in s).
Detects every value attained by more than one block, classifies each colliding
pair as DISJOINT (e1 < s2 after ordering, i.e. m1+k1 <= m2) or OVERLAPPING,
and emits a checksum certificate:

  - count of enumerated blocks per length k
  - total count
  - checksum = sum of (product mod M) mod M, M = 2^61 - 1  (order-independent)
  - full list of collision groups

Usage: sweep.py EXP [SMIN]   -> N = 10**EXP  (default SMIN = 1)
"""
import heapq
import sys
import time

M = (1 << 61) - 1


def stream(k, N, smin):
    p = 1
    for i in range(smin, smin + k):
        p *= i
    s = smin
    while p <= N:
        yield (p, s, k)
        p = p // s * (s + k)
        s += 1


def sweep(N, smin=1):
    # kmax = largest k such that the smallest length-k product (start smin) is <= N
    kmax = 4
    while True:
        p = 1
        for i in range(smin, smin + kmax + 1):
            p *= i
        if p > N:
            break
        kmax += 1
    if smin * (smin + 1) * (smin + 2) * (smin + 3) > N:
        return {"kmax": 0, "counts": {}, "total": 0, "checksum": 0, "groups": []}

    streams = [stream(k, N, smin) for k in range(4, kmax + 1)]
    merged = heapq.merge(*streams)

    counts = {k: 0 for k in range(4, kmax + 1)}
    total = 0
    checksum = 0
    groups = []  # each: (p, [(s,k), ...]) with >= 2 members

    prev_p = -1
    buf = []
    for (p, s, k) in merged:
        counts[k] += 1
        total += 1
        checksum = (checksum + p % M) % M
        if p == prev_p:
            buf.append((s, k))
        else:
            if len(buf) > 1:
                groups.append((prev_p, buf))
            buf = [(s, k)]
            prev_p = p
    if len(buf) > 1:
        groups.append((prev_p, buf))

    return {"kmax": kmax, "counts": counts, "total": total,
            "checksum": checksum, "groups": groups}


def classify(groups):
    out = []
    for p, reps in groups:
        for i in range(len(reps)):
            for j in range(i + 1, len(reps)):
                (s1, k1), (s2, k2) = sorted([reps[i], reps[j]])
                e1 = s1 + k1 - 1
                kind = "DISJOINT" if e1 < s2 else "OVERLAP"
                out.append((p, s1, k1, s2, k2, kind))
    return out


def main():
    exp = int(sys.argv[1])
    smin = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    N = 10 ** exp
    t0 = time.time()
    r = sweep(N, smin)
    dt = time.time() - t0
    print(f"# sweep.py  N=10^{exp}  smin={smin}  kmax={r['kmax']}  time={dt:.2f}s")
    for k in sorted(r["counts"]):
        print(f"count k={k}: {r['counts'][k]}")
    print(f"total: {r['total']}")
    print(f"checksum: {r['checksum']}")
    for (p, s1, k1, s2, k2, kind) in classify(r["groups"]):
        print(f"collision {kind}: {p} = [{s1}..{s1+k1-1}] = [{s2}..{s2+k2-1}]")


if __name__ == "__main__":
    main()
