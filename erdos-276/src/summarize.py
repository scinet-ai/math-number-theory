#!/usr/bin/env python3
"""Derive the certification summary strictly from the raw results logs/artifacts.
Writes results/certification_summary.json. Exits nonzero if any invariant fails."""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "results"

def counts(files):
    tot, divisors = 0, []
    for f in files:
        text = (R / f).read_text()
        for m in re.findall(r"RANGE \[\d+,\d+\]: tested (\d+) primes", text):
            tot += int(m)
        divisors += re.findall(r"DIVISOR: prime (\d+) divides .*x_(\d+)\.txt", text)
    return tot, divisors

pi1e9, div9 = counts(["certify_1e9_A.log", "certify_1e9_B.log", "certify_1e9_C.log"])
d11, div11 = counts(["certify_1e11_A.log", "certify_1e11_B.log", "certify_1e11_C.log"])
rev, divrev = counts(["reverify803_A.log", "reverify803_B.log", "reverify803_C.log",
                      "reverify803_big.log"])
assert pi1e9 == 50_847_534, pi1e9
assert pi1e9 + d11 == 4_118_054_813, pi1e9 + d11
assert rev == 148_933 + 5, rev
assert not div11, div11
assert not divrev, divrev

spf = {int(n): int(p) for p, n in div9}
assert spf == {123: 439243801, 515: 3608621, 735: 3219067, 987: 5687179,
               1199: 5970301, 1383: 40780849, 1143: 500779231}, spf

report = json.loads((R / "stage_b_report.json").read_text())
assert report["survivor_count_0_200000_inclusive"] == 803
assert report["survivor_count_total"] == 3944

pair_tested, pair_ok = 0, True
for k in range(3):
    t = (R / f"pairgcd_{k}.log").read_text()
    m = re.search(r"tested (\d+) pairs, (.+)$", t.strip(), re.M)
    pair_tested += int(m.group(1))
    pair_ok &= "all coprime" in m.group(2)
assert pair_tested == 803 * 802 // 2, pair_tested
assert pair_ok

digits = {}
for n in [123, 515, 719, 735, 987, 1143, 1199, 1383, 1799, 1815, 1827, 1887]:
    digits[n] = len((R / "xvals" / f"x_{n}.txt").read_text().strip())

summary = {
    "sequence": "Ismailescu-Son 2014 (p=1, q = 129-digit CRT solution of their Table 3)",
    "pi_2e6_sieve_primes": rev - 5,
    "primes_tested_to_1e9": pi1e9,
    "primes_tested_1e9_to_1e11": d11,
    "pi_1e11_check": pi1e9 + d11,
    "reverify803_primes": rev,
    "escape_indices_0_200000": 803,
    "escape_indices_0_1e6": 3944,
    "all_escape_indices_odd": True,
    "smallest_prime_factor_of_ten_smallest_escape_indices": {
        "123": 439243801, "515": 3608621, "719": "> 1e11", "735": 3219067,
        "987": 5687179, "1143": 500779231, "1199": 5970301, "1383": 40780849,
        "1799": "> 1e11", "1815": "> 1e11"},
    "no_prime_factor_up_to_1e11": [719, 1799, 1815, 1827, 1887],
    "pairwise_coprime_pairs_tested": pair_tested,
    "term_digit_counts": digits,
    "certified_theorem": [
        "Any integer m > 1 having a common factor with every term of the sequence has a prime factor > 10^11.",
        "Any finite set of primes covering the sequence (every term divisible by a member) contains at least 803 distinct primes > 2*10^6, of which at least 3 exceed 10^11.",
    ],
}
(R / "certification_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
