#!/usr/bin/env python3
"""Independent spot-verification of cluster/non-cluster verdicts.

Uses pure-Python deterministic Miller-Rabin (bases valid to 3.3e24) — a
primality method independent of the C sieve — to verify:
  1. sampled NON-CLUSTER witnesses (p, j): p prime, j odd composite,
     and p-j+k composite for every odd prime k <= j  => p is non-cluster;
  2. sampled CLUSTER primes p: for every odd composite j in [9, JCAP]
     there is an odd prime k <= j with p-j+k prime. Combined with the
     run-certified global bound max k(m) (summary.json) < JCAP, this
     verifies p is a cluster prime.
Exits nonzero on any mismatch.
"""
import csv, json, os, random, sys

WD = os.path.dirname(os.path.abspath(__file__))
_summary = json.load(open(os.path.join(WD, "summary.json")))
JCAP = max(3600, _summary["max_k_m"] + 600)  # must exceed certified max k(m)

def is_prime(n):
    if n < 2: return False
    for p in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n % p == 0: return n == p
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2,3,5,7,11,13,17,19,23,29,31,37):
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True

odd_primes = [k for k in range(3, JCAP, 2) if is_prime(k)]

def blocked(p, j):
    """True iff no odd prime k <= j with p-j+k prime (=> j witnesses non-cluster)."""
    return all(not is_prime(p - j + k) for k in odd_primes if k <= j)

def check_noncluster(p, j):
    assert is_prime(p), f"{p} not prime"
    assert j % 2 == 1 and j >= 9 and not is_prime(j), f"bad witness j={j}"
    assert p - j >= 2
    return blocked(p, j)

def check_cluster(p, jmax):
    assert is_prime(p)
    for j in range(9, jmax, 2):
        if is_prime(j): continue
        if p - j < 2: continue
        if blocked(p, j):
            print(f"  CLUSTER FAIL: p={p} blocked by j={j}"); return False
    return True

summary = _summary
assert summary["max_k_m"] < JCAP, "JCAP too small for certified max k(m)"

rows = [r for r in csv.reader(open(os.path.join(WD, "results.csv")))]
rows = [r for r in rows if len(r) >= 19]
random.seed(17)
sample = random.sample(rows, min(6, len(rows)))

fails = 0
for r in sample:
    lo, samp_nc, samp_nc_j = int(r[0]), int(r[12]), int(r[13])
    samp_dem, samp_dem_j, last_cl = int(r[14]), int(r[15]), int(r[17])
    if samp_nc and samp_nc_j:
        ok = check_noncluster(samp_nc, samp_nc_j)
        print(f"block {lo}: non-cluster witness p={samp_nc} j={samp_nc_j}: {'OK' if ok else 'FAIL'}")
        fails += not ok
    if samp_dem and samp_dem_j:
        ok = check_noncluster(samp_dem, samp_dem_j)
        print(f"block {lo}: demoted witness p={samp_dem} j={samp_dem_j}: {'OK' if ok else 'FAIL'}")
        fails += not ok
    if last_cl:
        ok = check_cluster(last_cl, JCAP)
        print(f"block {lo}: cluster p={last_cl} (all j<{JCAP}): {'OK' if ok else 'FAIL'}")
        fails += not ok

# fixed canonical anchors
ok = check_noncluster(97, 9); print(f"anchor: 97 non-cluster (j=9): {'OK' if ok else 'FAIL'}"); fails += not ok
ok = check_cluster(summary["largest_cluster_prime"], JCAP)
print(f"anchor: largest cluster {summary['largest_cluster_prime']}: {'OK' if ok else 'FAIL'}"); fails += not ok
sys.exit(1 if fails else 0)
