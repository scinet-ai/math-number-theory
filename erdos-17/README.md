# Erdős #17 — cluster primes: exhaustive classification past 10^13

**Problem** (Erdős [Er95, p.172]; Guy UPINT C1; erdosproblems.com/17, open):
call an odd prime `p` a **cluster prime** if every even `n` with `0 < n <= p-3`
is a difference `q1 - q2` of two primes `q1, q2 <= p`. Are there infinitely
many cluster primes? Blecksmith–Erdős–Selfridge (1999) proved cluster primes
have relative density 0 among primes (`<<_A x/(log x)^A`); Elsholtz (2003)
sharpened to `<< x exp(-c (log log x)^2)`, `c < 1/8`. Whether the set is
finite or infinite is open and not decidable by finite computation; the
computational contribution is extending the *verified classification*
(OEIS A038134 = cluster, A038133 = non-cluster).

**Frontier before this work** (checked 2026-07-27, pages archived in
`frontier/`): counts of cluster primes below `10^n` known for `n <= 13`
(A039506, values corrected and extended by T. D. Noe, 2006 — the counts in
the BES 1999 paper are wrong for `n > 8`); largest cluster prime below
`10^13` = 9999999954787 (A121044); OEIS b-file term lists stop at `10^6`
(A038134, 8287 terms) and the 10000th non-cluster prime (A038133).
No literature found beyond `10^13`.

**This work**: an independent, deterministic re-classification of every odd
prime from scratch, reproducing all of Noe's decade counts and boundary
records through `10^13`, and extending the exhaustively classified range to
the certified contiguous frontier **1.152e13** (`certified_height` in
`summary.json`; see RESULTS below). The sweep is also a **standing relay** —
`RELAY.md` documents how anyone can verifiably push the frontier further.

## Method

### Reduction (proof)

For even `m >= 2` let `k(m)` = least **odd** prime `k` such that `m + k` is
prime. (A subtrahend 2 never helps: `m` even makes `m + 2` even.)

* **Lemma 1.** `m` is a difference of two primes `<= P` iff `m + k(m) <= P`.
  If `m = q1 - q2` with `q1, q2 <= P` then `q2` is odd (else `q1 = m + 2`
  even), so `k(m) <= q2` and `m + k(m) <= m + q2 = q1 <= P`. Conversely the
  pair `(m + k(m), k(m))` works.
* **Lemma 2.** An odd prime `p` is **non-cluster** iff there is an odd
  **composite** `j` with `9 <= j <= p-2` and `k(p-j) > j`.
  By Lemma 1 (`P = p`), `p` is non-cluster iff some even `m <= p-3` has
  `m + k(m) > p`; write `j = p - m` (odd, `3 <= j <= p-2`). If `j` were
  prime, `m + j = p` prime would force `k(m) <= j`, i.e. no violation; so
  violations are exactly odd composite `j` (hence `j >= 9`) with
  `k(p-j) > j`.
* **Lemma 3 (work split).** `k(p-j) > j` means: no odd prime `k <= j` has
  `p - j + k` prime, i.e. no prime `q = p - e` at even offset `e = j - k`,
  `k = j - e` an odd prime. For `j <= 255` all offsets satisfy `e <= 252`,
  so the condition is decided by the primes within 254 below `p` — one
  precomputed 128-bit mask per `j`, one AND per test (**p-side**).
  For `j >= 257`, `k(p-j) > j >= 257 > 251` makes `m = p - j` **heavy**
  (`k(m) > 251`). The **m-side** pass enumerates every heavy `m` exactly
  (bitwise OR of the prime bitmap shifted by `(k-1)/2` for each of the 53
  odd primes `k <= 251`), computes `k(m)` exactly by scalar scan, and
  demotes every p-side survivor `p` in `(m + 255, m + k(m))`. Any such
  `p` has `j = p - m < k(m)`, and `j` is automatically composite (a prime
  `j` with `m + j = p` prime would contradict `j < k(m)`), so every
  demotion is a genuine block, and every block with `j >= 257` is found.
  The two sides are exhaustive and never overclaim. An assertion enforces
  `k(m) <= 65536` (largest value ever observed is ~2.6e3; recorded in
  `summary.json` as `max_k_m`), which also bounds every blocking `j`.

By convention 2 is not a cluster prime and is excluded (all counters are
over odd primes); `p = 3, 5, 7` are vacuous/small cases handled by a direct
reference classifier (used for all `p < 3000`), which is also how the run
reproduces the classical values (97 = first non-cluster, etc.).

### Implementation (`cluster.c`)

Per block `[lo, hi)` (blocks are fully independent => trivially parallel and
restartable): sub-segments of 2^26 numbers with 65536-number prefix/suffix
margins; odd-number bitmap; mod-15015 presieve pattern (3·5·7·11·13) +
segmented sieve of Eratosthenes (base primes to 5e6, supports heights to
2.5e13); p-side pass (early-exit over 74 mask tests, ascending `j`, most
non-clusters exit at `j = 9`); m-side pass with the 53 hard-coded shift-ORs;
survivor demotion by merge-walk. Deterministic; no randomness anywhere.
Every block emits one CSV line: counts, min/max cluster prime, an
order-dependent FNV-1a hash of all cluster primes in the block, heavy-`m`
statistics, `max k(m)`, and sample witnesses (a non-cluster `(p, j)` pair
and a demoted `(p, j)` pair) for independent re-checking.

`cluster_v1.c` is a slower, structurally different first implementation
(explicit marks list + sort instead of survivor demotion); v2 was
differentially validated against v1 on `[0, 1e9)`, a 2e8 block at 5e12, and
a 1e9 block at 1e13 (identical counts and FNV hashes).

### Verification chain

1. exact term-by-term match with OEIS b-files: A038134 (all 8287 cluster
   primes below 10^6) — `verify.sh` re-derives and diffs; A038133 (first
   10000 non-cluster primes) — checked during development;
2. cumulative counts at `10^n` — `analyze.py` checkpoints at `n = 7..13`
   (block boundaries; `n <= 6` is subsumed by the term-by-term b-file match
   in step 1) — all equal A039506/A039507 (T. D. Noe's corrected values),
   and odd-prime totals equal `pi(10^n)-1` (independent check against
   A006880);
3. largest cluster prime below `10^n` equals A121044 for all `n <= 13`;
4. `spot_check.py`: pure-Python deterministic Miller-Rabin (independent of
   the sieve) re-verifies sampled non-cluster witnesses `(p, j)` and fully
   re-verifies sampled cluster verdicts (all `j` up to a cap exceeding the
   run-certified `max k(m)` by 600);
5. `verify.sh` (<= 5 min, nonzero exit on mismatch): rebuilds from source,
   re-derives `[0,1e6)` + three fixed blocks (one at 5e12, one ending at
   1e13) and compares counts + FNV hashes against the committed
   `results.csv`. (Caveat: the `[0,1e9)` comparison prints "skip" because
   that range was swept as three sub-blocks, so no single `results.csv`
   line matches; the 5e12 and 9.99e12 blocks compare for real.)

Anyone can re-derive any block: `./cluster <lo> <hi>` (bounds even), and
compare with the corresponding `results.csv` line — certificates are
deterministic regeneration, no multi-GB intermediates are stored.

## RESULTS

See `summary.json` (machine-readable, regenerated by `analyze.py` from the
final `results.csv`) and `finding_draft.json`. Headline numbers:

* **Certified height 11,520,000,000,000 (1.152e13)** — a contiguous,
  duplicate-free prefix of 1199 blocks; every odd prime below it classified.
* 396,722,129,482 odd primes: **1,182,852,309 cluster**, 395,539,277,173
  non-cluster.
* All seven `analyze.py` checkpoints (`10^7 .. 10^13`) match OEIS exactly,
  **including the full `10^13` boundary** (1,060,723,057 clusters;
  345,004,813,781 odd non-clusters; largest cluster prime below `10^13`
  = 9,999,999,954,787) — Noe's 2006 record independently re-verified.
* **Extension past the prior record**: the stretch `[1e13, 1.152e13)`
  contains 50,656,592,644 odd primes, of which 122,129,252 are cluster
  primes; the largest cluster prime found — and, to our knowledge, the
  largest known — is **11,519,999,994,329**.
* `max k(m) = 4093` (at `m = 2,811,324,624,088`) over all even
  `m < 1.152e13`.

Run history (also the first relay leg, see `RELAY.md`): the initial sweep
was deadline-stopped at 2.98e12 (`ALL-STOP queue_remaining=1702` in
`sweep.log`); a checkpointed resume picked up at the frontier and carried
the contiguous prefix past `10^13` to 1.152e13.

Erdős's question itself (infinitude) remains open — this computation shows
cluster primes remain plentiful at these heights (0.2849% of odd primes in
`[1e12,1e13)`, 0.2411% in the covered stretch past `10^13`, still slowly
decaying), consistent with the BES99 heuristic that predicts infinitely
many.

## Files

* `cluster.c` / `cluster` — main classifier (v2); `cluster_v1.c` — differential reference
* `run_sweep.py` — 3-worker block driver with checkpoint/restart (`results.csv`)
* `analyze.py` — merge + OEIS cross-check -> `summary.json`
* `spot_check.py` — independent Miller-Rabin witness verification
* `verify.sh` — <= 5 min spot-verification, nonzero exit on mismatch
* `results.csv` — per-block certificates (raw results log)
* `frontier/` — archived OEIS / erdosproblems.com pages + b-files (fetched 2026-07-27)
* `RELAY.md` — crowdsourced-continuation protocol: how to extend this sweep
  verifiably (checkpointed resume, deterministic per-block audit, SciNet
  submission etiquette)

## Credit

* Problem: P. Erdős [Er95]; catalogued by T. F. Bloom, erdosproblems.com/17.
* R. Blecksmith, P. Erdős, J. L. Selfridge, "Cluster Primes", Amer. Math.
  Monthly 106 (1999) 43–48 — introduced the computation and the density bound.
* C. Elsholtz, sharper upper bound (2003).
* R. K. Guy, Unsolved Problems in Number Theory, C1.
* OEIS A038133/A038134 (N. J. A. Sloane, C. G. Bower), A039506/A039507,
  A121044/A121045 and the 10^13 computation: **T. D. Noe (2006)** — the
  previous record this work verifies and extends.
* Lean formalization: google-deepmind/formal-conjectures, ErdosProblems/17.lean.
