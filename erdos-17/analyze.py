#!/usr/bin/env python3
"""Merge results.csv into a certified summary for the cluster-prime sweep.

Checks contiguity of completed blocks, computes cumulative counts at powers
of 10, cross-checks against OEIS A039506 / A039507 / A121044 / A006880 (pi),
and reports the certified height (end of the contiguous prefix), the largest
cluster prime found, and max-k(m) records.

Writes summary.json and prints a human-readable report.
"""
import json, os, sys

WD = os.path.dirname(os.path.abspath(__file__))

# OEIS reference data (fetched 2026-07-27, frontier/ has raw pages)
A039506 = [3, 23, 99, 420, 1807, 8287, 40017, 202208, 1059807, 5736717,
           31911465, 182019293, 1060723057]          # clusters < 10^n, n=1..13
A039507 = [0, 1, 68, 808, 7784, 70210, 624561, 5559246, 49787726, 449315793,
           4086143347, 37425892724, 345004813781]    # odd non-clusters < 10^n
A121044 = [7, 89, 983, 9931, 99991, 999331, 9997879, 99999551, 999998693,
           9999995363, 99999976319, 999999998533, 9999999954787]  # max cluster < 10^n
PI10 = [4, 25, 168, 1229, 9592, 78498, 664579, 5761455, 50847534, 455052511,
        4118054813, 37607912018, 346065536839]       # pi(10^n)

rows = []
for line in open(os.path.join(WD, "results.csv")):
    f = line.strip().split(",")
    if len(f) < 19: continue
    rows.append(dict(lo=int(f[0]), hi=int(f[1]), odd=int(f[2]), cl=int(f[3]),
                     nc=int(f[4]), min_cl=int(f[5]), max_cl=int(f[6]), fnv=f[7],
                     heavy=int(f[8]), max_km=int(f[9]), arg_km=int(f[10]),
                     dem=int(f[11]), samp_nc=int(f[12]), samp_nc_j=int(f[13]),
                     samp_dem=int(f[14]), samp_dem_j=int(f[15]),
                     first_cl=int(f[16]), last_cl=int(f[17]), secs=float(f[18])))
rows.sort(key=lambda r: r["lo"])

# dedupe (restarts may duplicate a block) & contiguity
seen, uniq = set(), []
for r in rows:
    if r["lo"] in seen: continue
    seen.add(r["lo"]); uniq.append(r)
height, cum_odd, cum_cl, cum_nc, cpu = 0, 0, 0, 0, 0.0
max_cl, max_km, arg_km = 0, 0, 0
prefix = []
for r in uniq:
    if r["lo"] != height: break
    height = r["hi"]; prefix.append(r)
    cum_odd += r["odd"]; cum_cl += r["cl"]; cum_nc += r["nc"]; cpu += r["secs"]
    max_cl = max(max_cl, r["max_cl"])
    if r["max_km"] > max_km: max_km, arg_km = r["max_km"], r["arg_km"]

# cumulative checks at powers of 10
checks, cc_odd, cc_cl, cc_nc, cc_max = [], 0, 0, 0, 0
for r in prefix:
    cc_odd += r["odd"]; cc_cl += r["cl"]; cc_nc += r["nc"]
    cc_max = max(cc_max, r["max_cl"])
    hi = r["hi"]
    if hi in [10**n for n in range(1, 14)]:
        n = len(str(hi)) - 1
        ok_cl = cc_cl == A039506[n-1]
        ok_nc = cc_nc == A039507[n-1]
        ok_pi = cc_odd == PI10[n-1] - 1
        ok_mx = cc_max == A121044[n-1]
        checks.append(dict(power=n, clusters=cc_cl, ok_clusters=ok_cl,
                           nonclusters=cc_nc, ok_nonclusters=ok_nc,
                           odd_primes=cc_odd, ok_pi=ok_pi,
                           max_cluster=cc_max, ok_max_cluster=ok_mx))

all_ok = all(c["ok_clusters"] and c["ok_nonclusters"] and c["ok_pi"]
             and c["ok_max_cluster"] for c in checks)

# per-decade density table [10^n, 10^(n+1)) plus the tail past the last decade
decades = []
bounds = [10**n for n in range(1, 15)]
for i in range(len(bounds) - 1):
    lo_b, hi_b = bounds[i], bounds[i+1]
    d_cl = d_od = 0; d_hi = 0
    for r in prefix:
        if r["lo"] >= lo_b and r["hi"] <= hi_b:
            d_cl += r["cl"]; d_od += r["odd"]; d_hi = max(d_hi, r["hi"])
    if d_od:
        decades.append(dict(decade=f"[1e{i+1},1e{i+2})", covered_to=d_hi,
                            clusters=d_cl, odd_primes=d_od,
                            cluster_fraction=round(d_cl/d_od, 6)))
summary = dict(
    certified_height=height,
    blocks=len(prefix),
    odd_primes=cum_odd, clusters=cum_cl, nonclusters=cum_nc,
    largest_cluster_prime=max_cl,
    max_k_m=max_km, argmax_k_m=arg_km,
    cpu_seconds=round(cpu, 1),
    oeis_checks=checks, oeis_all_ok=all_ok,
    decade_table=decades,
)
with open(os.path.join(WD, "summary.json"), "w") as fh:
    json.dump(summary, fh, indent=1)
print(json.dumps(summary, indent=1))
if checks and not all_ok:
    print("!! OEIS CROSS-CHECK FAILURE", file=sys.stderr); sys.exit(1)
