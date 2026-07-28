#!/usr/bin/env python3
"""Merge the 3 partial sieve bitmaps (OR), extract survivor indices n in [0, 10^6]
with x_n not divisible by any prime <= 2*10^6 nor any Table-2 prime, and report:
  - survivor count on [0, 200000] (paper's range; IsSo14 report 803)
  - smallest survivors, parity split, per-100k density profile
Writes results/survivors.txt (one index per line) and results/stage_b_report.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "results"
N = 1_000_000

bm = bytearray((N + 1 + 7) // 8)
for i in range(3):
    part = (R / f"bitmap_{i}.bin").read_bytes()
    assert len(part) == len(bm), (i, len(part), len(bm))
    for j, byte in enumerate(part):
        bm[j] |= byte

survivors = [n for n in range(N + 1) if not (bm[n >> 3] >> (n & 7)) & 1]
(R / "survivors.txt").write_text("\n".join(map(str, survivors)) + "\n")

s200k = [n for n in survivors if n <= 200_000]
odd = sum(1 for n in survivors if n % 2)
even = len(survivors) - odd
profile = {}
for lo in range(0, N, 100_000):
    c = sum(1 for n in survivors if lo <= n < lo + 100_000)
    profile[f"[{lo},{lo+100_000})"] = {"count": c, "density": c / 100_000}

report = {
    "prime_bound": 2_000_000,
    "extra_primes": [35239681, 764940961, 8288823481, 10783342081, 571385160581761],
    "index_range": [0, N],
    "survivor_count_total": len(survivors),
    "survivor_count_0_200000_inclusive": len(s200k),
    "isso14_reported_count_0_200000": 803,
    "match_isso14": len(s200k) == 803,
    "survivors_even": even,
    "survivors_odd": odd,
    "smallest_20_survivors": survivors[:20],
    "largest_5_survivors": survivors[-5:],
    "density_total": len(survivors) / (N + 1),
    "density_profile_per_100k": profile,
}
(R / "stage_b_report.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "density_profile_per_100k"}, indent=2))
print("profile:", {k: v["count"] for k, v in profile.items()})
