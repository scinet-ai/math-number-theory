#!/usr/bin/env python3
"""Re-certify records from a sieve_fmin run via exact inverse-totient enumeration
(invphi.py — independent of the sieve).

For each selected record line "E a n" (first occurrence with n >= 2a) and each
running-record line "R a n r": enumerate ALL preimages of a and assert
min == n. Selection (to keep runtime sane while covering everything that the
write-up actually cites):
  * every R line (running record ratios),
  * every E line with a <= FULL_LIMIT (default 10^8),
  * the 50 E lines with largest a,
  * a deterministic pseudorandom sample of 200 further E lines (seed 51).
Usage: verify_records.py data/run_full.txt [FULL_LIMIT]
"""
import random
import sys

from invphi import invphi

path = sys.argv[1] if len(sys.argv) > 1 else "data/run_full.txt"
FULL_LIMIT = int(sys.argv[2]) if len(sys.argv) > 2 else 10**8

E, R = [], []
for line in open(path):
    t = line.split()
    if not t:
        continue
    if t[0] == "E":
        E.append((int(t[1]), int(t[2])))
    elif t[0] == "R":
        R.append((int(t[1]), int(t[2])))

sel = {(a, n) for (a, n) in R}
sel |= {(a, n) for (a, n) in E if a <= FULL_LIMIT}
sel |= set(sorted(E, key=lambda t: -t[0])[:50])
rng = random.Random(51)
rest = [t for t in E if t not in sel]
sel |= set(rng.sample(rest, min(200, len(rest))))

bad = 0
for i, (a, n) in enumerate(sorted(sel)):
    pre = invphi(a)
    if not pre or pre[0] != n:
        print("FAIL a=%d: sieve n=%d, invphi min=%s (#pre=%d)"
              % (a, n, pre[0] if pre else None, len(pre)))
        bad += 1
    if (i + 1) % 50 == 0:
        print("  ... %d/%d re-certified" % (i + 1, len(sel)), flush=True)

print("verify_records: %d checked (%d R-records, %d E-lines in file), %d failures"
      % (len(sel), len(R), len(E), bad))
sys.exit(1 if bad else 0)
