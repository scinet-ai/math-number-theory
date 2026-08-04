# Erdős #411 — certificate equivalence, parity, and an exhaustive multiplier-orbit catalogue for n + φ(n) to 10⁷

**Problem** (Erdős–Graham 1980, p. 81; erdosproblems.com/411). Iterate
g(n) = n + φ(n). Erdős and Graham asked about eventual multiplicative
relations g_{k+r}(n) = c·g_k(n) — the literal question being whether
g_{k+2}(n) = 2·g_k(n) for all large k has solutions other than the known
even-orbit families.

## This work

Structural theorems (proved in full in `proof_structural_lemmas.md`) plus an
exhaustive computational catalogue (`proof_catalogue.md`). All of the
following is **new** except where flagged:

1. **Certificate-equivalence theorem**: g_{k+r}(n) = c·g_k(n) holds for all
   large k **iff** some orbit point x = g_K(n) satisfies the finite
   certificate g_r(x) = c·x together with rad(c) | g_j(x) for 0 ≤ j < r —
   and then the relation holds for **every** k ≥ K, with the certificate-index
   set upward closed (so the least certificate index is the sharp onset).
   Proof: a two-line φ-scaling lemma (φ(cm) = cφ(m) ⟺ rad(c) | m) plus
   well-founded double induction. *The special case (r,c) = (2,2) of the
   forward direction appears inside Steinerberger's equivalence proof
   (arXiv:2504.08023); the general statement, the converse, and the
   sharp-onset clause are not recorded there or on the problem page.*
2. **Parity theorem**: for m ≥ 3, g(m) ≡ m (mod 2), so orbit parity is
   constant from value 3 on. Hence any eventual relation with even multiplier
   c (in particular the literal Erdős–Graham c = 2) forces n even with an
   all-even orbit, and odd starts admit only odd multipliers.
3. **Exhaustive catalogue (Theorem A)**: in the box 2 ≤ x ≤ 10⁷, 1 ≤ r ≤ 40,
   the complete list of raw hits g_r(x) = c·x (integer c ≥ 2) has exactly
   16,361 elements (no truncated orbit); exactly 10,536 are certificates;
   under orbit/scaling/power reductions they collapse to **19 primitive
   orbits** (`certificates/witnesses.json`, Table 1 of `proof_catalogue.md`).
   Only c ∈ {2, 3, 4, 9, 729, 6561} occurs among primitives, and no primitive
   relation has 25 < r ≤ 40. The growth bound c ≤ (3/2)^r at even certificate
   points (Lemma 6) rules out missed large multipliers within the box.
4. **New primitive witness orbits** (each an unconditional theorem via its
   verified certificate): three (r=4, c=3) orbits at x = 11202, 13890, 42498,
   pairwise independent of Cambie's 738 (up to 2^a·3^b-scalings ≤ 2000, 200
   steps); (r=9, c=9) root 28002 whose scaled orbits absorb all five recorded
   Steinerberger starts; (r=25, c=729) root 15702; odd (r=20, c=6561) orbits
   6075 and 965505; odd (r=14, c=729) entry branches 11739 and 31851.
5. **Sharp onset indices** upgrading every recorded empirical example to a
   theorem — including the correction that Weintraub's
   g_{k+25}(3114) = 729·g_k(3114) holds for all k ≥ 5 and fails at k = 4
   (the problem page records k ≥ 6), and that Cambie's 738, 148646, 4325798
   carry certificates already at k = 0.

## Verification

`./verify.sh` (~10–20 min; needs gcc + Python 3, stdlib only) re-verifies the
whole chain from scratch:

1. recompiles the C sweep (`code/sweep.c`) and re-runs it on x ≤ 10⁵, r ≤ 25;
2. re-runs the **independent pure-Python probe** (`code/probe.py` — own totient
   sieve, deterministic Miller–Rabin, Brent rho; no shared code) on the same
   range and checks the two raw-hit sets are IDENTICAL (2,998 hits);
3. re-checks **every one of the 10,536 certificates** in
   `certificates/witnesses.json` by direct iteration of g, using a third
   self-contained implementation (`code/verify_certificates.py`): every stored
   orbit value, the identity g_r(x) = c·x, and rad(c) | g_j(x) for j < r;
4. re-checks the OEIS A383044 cross-validation ((2,2)-certificate points
   ≤ 8960 exactly match the OEIS terms).

**Status: full run, ALL CHECKS PASSED** (re-run in this repo, 2026-08-04;
10536/10536 certificates verified, 0 failures; the script has a single mode —
the full 10⁷×40 production sweep itself is not re-run by verify.sh, but its
outputs are in `logs/sweep_1e7_r40/` and every certificate derived from it is
re-verified independently).

## Trusted base / caveats

- Computational finding + elementary proved lemmas; no external theorem
  assumed. The structural proofs are prose (not formalized).
- Exhaustiveness is claimed only for the stated box (x ≤ 10⁷, r ≤ 40). An
  incomplete 10⁸ extension run from the attack workspace is **not** included
  here and is not part of any claim (its partial outputs contained ~65k
  overflow-truncated odd orbits, so a sound 10⁸ box needs big-integer
  completion first).
- Novelty caveats (disclosed in the finding draft): Steinerberger's r=9 list
  carries an ellipsis ("Many more such solutions exist"), and the original
  Selfridge–Weintraub r=9 solution values are not listed in any accessible
  source — so the (9,9), (20,6561), (25,729), (14,729) novelty claims are
  relative to the *explicitly recorded* examples. Stijn Cambie is active on
  this problem and may hold unpublished sweeps.
- Orbit-independence claims for the (4,3) family are bounded computations
  (scalings 2^a·3^b ≤ 2000, 120–200 steps, values to ~10¹⁸), as stated.

## Credit

- Problem: P. Erdős, R. L. Graham, *Old and new problems and results in
  combinatorial number theory* (1980), p. 81; curated by T. F. Bloom,
  erdosproblems.com/411 (examples credited there to **Selfridge and
  Weintraub**, **Weintraub**, and **Cambie**; the page thanks **Stijn
  Cambie**).
- Prior equivalence for (r,c) = (2,2) and the recorded odd examples
  (385, 3393, 6175, 6969): **Stefan Steinerberger**, *On an iterated
  arithmetic function problem of Erdos and Graham*, arXiv:2504.08023.
- OEIS **A383044** (author **Michel Marcus**; family-decomposition comment by
  **Michael De Vlieger**) — the (2,2) anchor sequence.
- Context on the residual φ(m) = (2/3)(m+1) branch: **Christian Hercher**,
  arXiv:2504.19915.

## Update: 10^8 box completed (2026-08-04)

The extension sweep referenced above completed after staging: exhaustive box **x ≤ 10^8, r ≤ 40** —
25,513 raw hits, 16,832 certificates (all re-verified by direct orbit iteration: `logs/verify_1e8.log`,
0 failures), **20 primitive families** (`certificates/catalogue_1e8.json`). Exactly one new primitive
family appears beyond the 10^7 box: a second orbit-independent **(r=25, c=729)** witness at
**x = 71,912,934**, independent of Weintraub's 3114 orbit. Reproduce: rebuild `code/sweep.c`, run
`sweep 2 100000000 40 1000000000 12`, then `code/postprocess.py hits.txt 100000000 40` and
`code/verify_certificates.py` on the output.
