# Erdős #693 — maximal gap between integers in [n, n^k] with a divisor in (n, 2n)

**Problem** (Erdős 1979, [Er79e]; erdosproblems.com/693). Fix k ≥ 2 and let
A = {a_1 < a_2 < ...} be the set of integers in [n, n^k] having at least one
divisor in the open interval (n, 2n). Erdős asked to estimate the maximal gap

    G(n,k) = max_i (a_{i+1} - a_i),

and specifically whether G(n,k) ≤ (log n)^{O(1)}.

**Status of the frontier before this work** (checked 2026-07-27):

- erdosproblems.com/693: OPEN, no comments, no partial or complete solutions
  claimed.
- The only computational record is OEIS A391118 (Elijah Beregovsky,
  Dec 28 2025): G(n,2) for n = 3..83 only (naive Mathematica enumeration up to
  n^2 = 6889).
- No literature on the *gap* question. The adjacent count question
  H(x, y, z) = #{m ≤ x : ∃ d|m, y < d ≤ z} was resolved by K. Ford, "The
  distribution of integers with a divisor in a given interval", Ann. of
  Math. 168 (2008), 367-433, but Ford's results concern densities/counts,
  not maximal gaps.

**This work (frontier after).** First substantial computational record of the
gap function:

- G(n,2) exactly for **every** n in [3, 2000], plus a 20-per-decade log grid
  to n = 100000 and a 10-per-decade landmark set to **n = 10^6** (interval
  [n, n^2] reaching 10^12; ~0.7·10^12 divisor marks for the largest case).
- G(n,3) exactly for every n in [3, 500], plus a log grid to n = 5012 and
  landmarks 6310, 7943, **10^4** (interval [n, n^3] reaching 10^12).
- Witness gap locations (a_i, a_{i+1}) and |A ∩ [n, n^k]| for every n, each
  row independently machine-verifiable.
- Growth fit against (log n)^c — see RESULTS below.

All claims are **fully-swept**: every reported G(n,k) comes from sieving the
*entire* interval [n, n^k]; no localization heuristics were used anywhere.

## Method

`sieve.c` — segmented bitset sieve. For each divisor d in [n+1, 2n-1], mark
every multiple of d inside [n, n^k] (work ≈ log(2)·n^k marks); then a single
left-to-right scan of the bitset yields the maximal gap between consecutive
marked integers, the first witness pair achieving it, and |A| (popcount).
Segments of 2^27 bits (16 MiB) keep all writes in cache; a per-divisor
next-multiple table avoids per-segment divisions. Exact 64-bit integer
arithmetic throughout; fully deterministic; no randomness anywhere.

Long runs checkpoint every 30 s (`checkpoints/ck_{k}_{n}.txt`, atomic
tmp+rename) and resume exactly. `driver.py` orchestrates the sweep with 3
worker processes and is restart-safe at per-n granularity (results append as
atomic O_APPEND lines).

## Files

- `sieve.c` — core sieve (build: `clang -O3 -o sieve sieve.c`).
- `driver.py` — deterministic job plan + 3-process scheduler.
- `data/results.csv` — one row per (n,k):
  `n,k,G,gap_start,gap_end,count,seconds` where `gap_end - gap_start = G`,
  `count = |A ∩ [n,n^k]|`.
- `data/b391118.txt` — the 81 published terms of OEIS A391118 (n = 3..83).
- `data/fit_summary.txt` — (log n)^c fits, per-decade maxima, witness
  locations (`python3 fit.py`).
- `verify.sh` / `verify.py` — independent spot-verification, ~1-2 min,
  nonzero exit on mismatch:
  1. fresh sieve vs all 81 OEIS A391118 terms;
  2. every row's witness pair re-checked by direct numpy divisibility
     (endpoints in A, all interior points not in A);
  3. full independent recompute of (n=2000, k=2) and (n=500, k=3) by a
     different algorithm (numpy union-of-multiples), compared exactly.
- `logs/` — driver + per-job logs (exact invocations and timings).

## Results

Headline values (from `data/results.csv`; witness pair in brackets):

| n       | G(n,2) | witness                             | \|A ∩ [n,n²]\|   |
|---------|--------|-------------------------------------|------------------|
| 83      | 12     | [3978, 3990] (= OEIS a(83))         | 2,894            |
| 1000    | 23     | [956091, 956114]                    | 363,896          |
| 10000   | 40     | [53270168, 53270208]                | 32,896,587       |
| 100000  | 61     | [8549181964, 8549182025]            | 3,059,442,219    |
| 1000000 | 77     | [787148268885, 787148268962]        | 289,032,444,529  |

| n     | G(n,3) | witness                      |
|-------|--------|------------------------------|
| 500   | 33     | [599205, 599238]             |
| 1000  | 40     | [142838876, 142838916]       |
| 5012  | 52     | [22321540352, 22321540404]   |
| 10000 | 60     | [233690691, 233690751]       |

Growth (see `data/fit_summary.txt`):

- Fit of log G(n,2) on log log n gives slope c ≈ 1.65 (n ≥ 100, R² = 0.85;
  c = 1.64 over n ≥ 10^5). G/(log n)^1.5 stays within [1.46, 1.73] across
  every decade from n = 100 to n = 10^6, while G/(log n)^2 decreases
  monotonically (0.72 → 0.40). The data are consistent with
  G(n,2) = Θ((log n)^{3/2})-ish growth in the accessible range and provide
  **no evidence against** Erdős's (log n)^{O(1)} hypothesis — they support it.
- k=3 behaves the same (c ≈ 1.5, n ≥ 100, R² = 0.93).
- Quantitative heuristic match: Ford's theorem gives the density of integers
  with a divisor in (n, 2n) near x ≍ n² as ≍ 1/((log n)^δ (log log n)^{3/2}),
  δ = 1 − (1 + log log 2)/log 2 ≈ 0.086. A Poisson-spacings model on the
  sparsest zone then predicts G(n,k) ≍ (log n)^{1+δ} (log log n)^{3/2},
  whose *local* log-log slope at n = 10^6 is 1 + δ + 1.5/log log n ≈ 1.66 —
  matching the fitted 1.63–1.65. (Heuristic, clearly not a proof.)
- Witness structure: for k=2 every landmark witness lies at 0.53–0.96 · n²;
  for k=3 the maximal gap does *not* sit near n³ — witnesses sit at
  ≤ 0.18 · n³ (n ≤ 5012) or just above n² (2.34 · n² for n = 10^4), and
  G(n,3) > G(n,2) at equal n (60 vs 40 at n = 10^4): the sparsest zone —
  the multiplication-table regime — extends to just above x ≍ n².

`data/b391118_extended.txt` extends OEIS A391118 from 81 to 1998 terms
(n = 3..2000).

**Verification** (`./verify.sh`, ~25 s): all 81 published OEIS terms
reproduced; all 2563 witness pairs re-checked by independent direct
divisibility (endpoints in A, interior points not in A); full independent
recomputes of (n=2000, k=2) and (n=500, k=3) by a numpy union-of-multiples
algorithm match exactly (G, witness, |A|).

## Credit

- Problem: Paul Erdős, "Some unconventional problems in number theory",
  Astérisque 61 (1979), 73-82; curated as #693 by Thomas Bloom,
  erdosproblems.com/693.
- Prior data: OEIS A391118 by Elijah Beregovsky (Dec 2025) — used here as an
  independent cross-check for n = 3..83.
- Context: Kevin Ford, Ann. of Math. 168 (2008) 367-433 (distribution of
  integers with a divisor in a given interval; the count analogue).
