# Erdős #388 — exhaustive uniqueness certificate to 10³⁶, and a verified resolution of the (6,4) case

**Problem** (Erdős; erdosproblems.com/388). Can a product of ≥ 4 consecutive
positive integers equal a product of another ≥ 4 consecutive positive
integers, with the two blocks disjoint? The classical sporadic example is
17297280 = 8·9·10·11·12·13·14 = 63·64·65·66.

## This work

1. **New — exhaustive-search certificate to 10³⁶**: enumerating **every**
   product of k ≥ 4 consecutive positive integers up to 10³⁶ (1,017,038,196
   blocks, lengths 4 ≤ k ≤ 32) in two independently written implementations
   (pure-Python bigint `sweep.py`; C `unsigned __int128` `sweep.c`),
   17297280 = 8⋯14 = 63⋯66 is proved to be the **only** solution with both
   lengths ≥ 4 and disjoint blocks up to product 10³⁶. This extends the
   previously recorded search state (OEIS A163263 comment — gaps between the
   first 45,000 primes, roughly 10²²-equivalent for length-4 upper blocks) by
   about 14 orders of magnitude. Positive control: the expected infinite
   *overlapping* family (OEIS A064224: 5040, 19958400, …) is detected, so the
   collision detector has failure-power.
2. **Independent verification (NOT new) — the (6,4) length pair**: the only
   positive-integer solution of (x+1)⋯(x+6) = (y+1)⋯(y+4) is (x,y) = (1,6),
   i.e. 2⋯7 = 7⋯10 = 5040, whose blocks overlap at 7 — hence Erdős #388 has
   **no** solution with lengths (6,4). This was **first proved by L. Hajdu
   and Á. Pintér, *Combinatorial Diophantine equations*, Publ. Math.
   Debrecen 56 (2000), 391–403** (only positive solution (7,2) in their
   normalization, equivalent to ours); the directory's contribution is an
   independent modern proof that agrees. Via the symmetric substitutions
   t = x²+7x+6, u = y²+5y+5 the equation reduces exactly to integral points
   on the elliptic curve u² = t³+10t²+24t+1 (LMFDB **10388.b1**, rank 2,
   trivial torsion); SageMath `gens(proof=True)` + the provably complete
   `integral_points` routine yields exactly 14 integral points, of which only
   (t,u) = (14,71) survives the arithmetic filter (`proof_case_6_4.md`).
   Notably, the (6,4) pair is outside MacLeod–Barrodale's 1970 list, outside
   the Saradha–Shorey ratio theorems, and outside Hajdu–Tijdeman's 2022
   finiteness theorem (their Thm 10.1 requires k ∤ 2ℓ, but 4 | 12).

## Verification

`./verify.sh` — modes:

- `./verify.sh` (fast, ~15 s): witness identity + factorization; builds the C
  implementation from `sweep.c`; dual-implementation exhaustive sweeps at
  10¹⁸ and 10²⁴ (per-length counts, order-independent checksum, and full
  collision lists must agree exactly, with exactly one disjoint collision
  = 17297280); the (6,4) reduction script `case64_reduction.py` (sympy
  identities, direct searches, LMFDB point map, arithmetic filter).
- `./verify.sh full` (~8 min): adds the 10³⁰ and 10³⁶ dual sweeps — the
  headline certificate (checksum at 10³⁶: 349154945598101266; reference
  outputs `out_c_36.txt` / `out_py_36.txt`).
- `./verify.sh sage`: re-runs the Sage integral-point proof
  (`case64_sage.sage`; needs a Sage environment, e.g.
  `mamba create -n e388sage sage`) and asserts the certified rank bounds
  (2,2) and the unique solution (1,6).

**Status: `full` + `sage` run in this repo, 2026-08-04 — ALL CHECKS PASSED**
(both implementations agree at 10¹⁸/10²⁴/10³⁰/10³⁶; unique disjoint collision
17297280 at every bound; Sage rank certificate + integral points + unique
(6,4) solution reproduced). The C binary is built from source by verify.sh;
no prebuilt binary is shipped.

## Trusted base / caveats

- The 10³⁶ sweep is exact integer arithmetic throughout (Python bigints; C
  `unsigned __int128` with every intermediate bounded by 33·10³⁶ < 2¹²⁷),
  cross-validated between two independent implementations at four bounds.
- The (6,4) integral-point **completeness** rests on SageMath 10.7's
  `integral_points` (elliptic-logarithm method, provably complete given a
  full Mordell–Weil basis) with `gens(proof=True)` certified rank bounds
  (2,2) — a disclosed tool dependency, corroborated by the LMFDB 10388.b1
  point list and by direct searches (t ≤ 10⁷, x ≤ 2·10⁶).
- Prior-work status is disclosed prominently: the (6,4)=(4,6) pair was
  already resolved by Hajdu–Pintér 2000 (recorded in the historical overview,
  Section 2 p. 6, of Hajdu–Tijdeman arXiv:2204.12345: "Hajdu and Pintér [40]
  showed that the only positive integer solution for (k,ℓ)=(4,6) is (7,2)").
  Our result is an **independent verification**, not the first resolution.
- General problem remains OPEN: solutions with product > 10³⁶ and all other
  length pairs (e.g. (5,4), (7,4)) are not excluded.

## Credit

- Problem: P. Erdős; curated by T. F. Bloom, erdosproblems.com/388.
- Prior resolution of the (4,6) pair: **L. Hajdu, Á. Pintér**, *Combinatorial
  Diophantine equations*, Publ. Math. Debrecen 56 (2000), 391–403 (citation
  verified via Hajdu–Tijdeman, arXiv:2204.12345, Section 2 and reference
  [40]).
- Finiteness-theorem context: **L. Hajdu, R. Tijdeman**, *The Diophantine
  equation f(x)=g(y) for polynomials with simple rational roots*,
  arXiv:2204.12345.
- Earlier fixed-pair results: **R. A. MacLeod, I. Barrodale**, *On equal
  products of consecutive integers*, Canad. Math. Bull. 13 (1970), 255–259.
- Prior search state + prime-free observation: OEIS **A163263** (comment by
  **T. D. Noe**); overlapping-family positive control: OEIS **A064224**.
- Curve data: LMFDB elliptic curve 10388.b1
  (lmfdb.org/EllipticCurve/Q/10388/b/1); computation: SageMath 10.7.
