# Erdős #963 — exact values f(n) for all n ≤ 27: the floor conjecture holds, and is strict at n = 14, 15

**Problem** (Erdős; erdosproblems.com/963). Let f(n) be the largest k such that
every set of n reals contains a **dissociated** subset (all subset sums
distinct) of size k. Erdős asked whether f(n) ≥ ⌊log₂ n⌋.

## This work

**First exact computation of f(n) for small n**, with machine-checkable
certificates (`proof_smalln.md`; no such table exists in the literature, on
the problem's forum thread, or in OEIS — the certified sequence diverges from
every OEIS numerical match at n = 22).

- **Reduction theorem** (new, elementary; Theorem 1 of `proof_smalln.md`):
  f(n) = h(⌈(n−1)/2⌉), where h(m) is the same minimum over m reals with
  distinct sign-classes — sign-symmetrization is exactly optimal, halving the
  search dimension.
- **Certified table**: f = 0, 1, 1, 2, 2, 2, 2 for n = 1..7; f = 3 for
  n = 8..13; f = 4 for n = 14..27. Equivalently h(1)=1, h(2)=2, h(3)=2,
  h(4)=h(5)=h(6)=3, h(7)=…=h(13)=4.
- **The conjectured bound f(n) ≥ ⌊log₂ n⌋ is TRUE for all n ≤ 27, and STRICT
  exactly at n = 14, 15** (f = 4 > 3) — the first-ever data on the exact
  question shows ⌊log₂ n⌋ is not the exact truth. Also f(2^k) = k for
  2^k ≤ 16.
- **Staircase structure**: with T(k) = max{m : h(m) ≤ k}, certified
  T(1)=1, T(2)=3, T(3)=6, T(4) ≥ 13. Extremal class sets stop being initial
  intervals at k = 4: the 13-element set {1,…,10,12,13,15} (skipping 11 and
  14) has no dissociated 5-subset, beating the interval bound tied to the
  Conway–Guy-type 5-element distinct-subset-sum set {6,9,11,12,13}.
  Whether T(4) = 13 (equivalently f(28) = 5 vs 4) is **open** — h(14) ≥ 5 is
  beyond this method's reach.

This is disjoint from and complementary to the asymptotic result in
[`../erdos-963-verification/`](../erdos-963-verification/): the strictness at
n = 14, 15 is invisible to asymptotic methods.

## Method (why the search is exhaustive)

An n-set of reals is modelled by its subset-sum coincidence pattern
N(A) = A^⊥ ∩ {−1,0,1}^n, a rational subspace spanned by ternary vectors;
every valid such subspace is realized by an actual integer point
(finite-union-of-subspaces argument, realization re-verified concretely).
f(n) ≥ k is certified by refuting the covering condition over **all** valid
subspaces via a directed DFS with RREF-canonical memoization (completeness
lemma: `proof_smalln.md`, Lemma 5). The fast engine works over GF(2³¹−1) with
an explicit Hadamard bound (all minors < 10⁵ ≪ p) proving the mod-p linear
algebra exact for these inputs.

## Verification

`./verify.sh` (pure-stdlib Python 3, deterministic; ~15–25 min, dominated by
the two m=7 k=4 refutations) re-derives everything from scratch:

1. full enumeration of all valid patterns for m ≤ 4 (h(1)..h(4) exact);
2. lower-bound refutations h(5) ≥ 3, h(6) ≥ 3, and the key run **h(7) ≥ 4**;
3. direct dimension-n refutations of f(n) for n ≤ 9 that do **not** use the
   reduction theorem (cross-validating it);
4. an independent second implementation (different exact arithmetic — 
   fraction-free integer elimination, Fraction-RREF keys — reversed branching
   order, and no root-symmetry reduction on most runs) reproducing every
   refutation, including an independent h(7) ≥ 4;
5. upper-bound witnesses re-verified from the bare definition by direct
   enumeration of all subset sums (`verify_witnesses.py`), including the
   m = 13 witness {1,…,10,12,13,15} over all 1287 5-subsets;
6. a randomized falsifier (3000 seeded random/structured sets; none may beat
   the table).

**Status: full run, ALL SMALL-N CHECKS PASSED** (re-run in this repo,
2026-08-04; the script has a single full mode).

## Trusted base / caveats

- Purely computational + elementary proofs; no external theorem is assumed.
  The reduction theorem and the completeness lemma are proved in
  `proof_smalln.md`; the mod-p exactness rests on the explicit Hadamard bound
  stated there (and the independent engine avoids mod-p arithmetic entirely).
- T(4) = 13 is **not** certified (claimed only as T(4) ≥ 13); f(28) is open.
- Novelty basis: web/OEIS/arXiv searches recorded in the finding draft
  (2026-08-03); the forum thread discusses only asymptotics.

## Credit

- Problem: P. Erdős; curated by T. F. Bloom, erdosproblems.com/963.
- The n = 13 interval cap connects to the Conway–Guy sequence (Erdős #1
  distinct-subset-sum circle); context: Q. Dubroff, J. Fox, M. W. Xu,
  arXiv:2006.12988.
- The asymptotic side (KoishiChan's theorem and our verification of it) lives
  in [`../erdos-963-verification/`](../erdos-963-verification/).
