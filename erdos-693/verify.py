#!/usr/bin/env python3
"""verify.py — independent spot-verification for the Erdős #693 results.

Checks (all use methods independent of sieve.c's segmented bitset):
  1. OEIS cross-check: fresh `./sieve range 3 83 2` vs data/b391118.txt
     (81 published terms of A391118).
  2. Witness check for EVERY row of data/results.csv: with numpy divisibility
     (m % d for all d in (n,2n)), confirm gap_start and gap_end are members of
     A and every integer strictly between is a non-member — i.e. the reported
     pair really are consecutive elements of A at distance G.
  3. Full independent recompute of (n=2000,k=2) and (n=500,k=3) via a
     numpy multiples-union algorithm (no bitset); G, witness and |A| must
     match results.csv exactly.

Exit code 0 iff everything matches. Runtime ~1-2 min.
"""
import csv, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "data", "results.csv")
BFILE = os.path.join(HERE, "data", "b391118.txt")
SIEVE = os.path.join(HERE, "sieve")
fails = 0


def fail(msg):
    global fails
    fails += 1
    print("FAIL:", msg)


def member(m, n):
    """True iff m has a divisor in the open interval (n, 2n). Independent
    method: direct divisibility test against all d in [n+1, 2n-1]."""
    d = np.arange(n + 1, 2 * n, dtype=np.int64)
    return bool(np.any(m % d == 0))


def check_oeis():
    out = subprocess.run([SIEVE, "range", "3", "83", "2"],
                         capture_output=True, text=True, check=True).stdout
    mine = {}
    for line in out.strip().splitlines():
        p = line.split(",")
        mine[int(p[0])] = int(p[2])
    bf = {}
    for line in open(BFILE):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        a, b = line.split()
        bf[int(a)] = int(b)
    for n, v in sorted(bf.items()):
        if mine.get(n) != v:
            fail(f"OEIS A391118 mismatch at n={n}: ours={mine.get(n)} oeis={v}")
    print(f"[1] OEIS cross-check: {len(bf)} terms compared, "
          f"{'OK' if fails == 0 else 'MISMATCH'}")


def check_witnesses():
    rows = list(csv.reader(open(RESULTS)))
    nbad = 0
    for row in rows:
        n, k, G, gs, ge = (int(row[0]), int(row[1]), int(row[2]),
                           int(row[3]), int(row[4]))
        if ge - gs != G:
            fail(f"n={n} k={k}: gap_end-gap_start != G"); nbad += 1; continue
        if not member(gs, n):
            fail(f"n={n} k={k}: gap_start {gs} is NOT in A"); nbad += 1
        if not member(ge, n):
            fail(f"n={n} k={k}: gap_end {ge} is NOT in A"); nbad += 1
        d = np.arange(n + 1, 2 * n, dtype=np.int64)
        for m in range(gs + 1, ge):
            if np.any(m % d == 0):
                fail(f"n={n} k={k}: interior point {m} IS in A "
                     f"(witness pair not consecutive)")
                nbad += 1
                break
    print(f"[2] witness check: {len(rows)} rows, {nbad} bad")


def numpy_full(n, k):
    """Independent full recompute: union of multiples via numpy."""
    N = n ** k
    parts = [np.arange(d, N + 1, d, dtype=np.int64)
             for d in range(n + 1, 2 * n)]
    A = np.unique(np.concatenate(parts))
    A = A[(A >= n) & (A <= N)]
    diffs = np.diff(A)
    i = int(np.argmax(diffs))
    return int(diffs[i]), int(A[i]), int(A[i + 1]), int(len(A))


def check_full_recompute():
    rows = {(int(r[0]), int(r[1])): r for r in csv.reader(open(RESULTS))}
    for n, k in [(2000, 2), (500, 3)]:
        if (n, k) not in rows:
            fail(f"({n},{k}) missing from results.csv")
            continue
        r = rows[(n, k)]
        got = (int(r[2]), int(r[3]), int(r[4]), int(r[5]))
        exp = numpy_full(n, k)
        if got != exp:
            fail(f"full recompute n={n} k={k}: results={got} numpy={exp}")
        else:
            print(f"[3] full recompute n={n} k={k}: G={exp[0]} witness "
                  f"{exp[1]}->{exp[2]} |A|={exp[3]} OK")


if __name__ == "__main__":
    check_oeis()
    check_witnesses()
    check_full_recompute()
    if fails:
        print(f"VERIFICATION FAILED: {fails} problem(s)")
        sys.exit(1)
    print("VERIFICATION PASSED")
