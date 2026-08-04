# Erdős #1041 — the collinear-roots case proved, and a first explicit uniform path-length bound

**Problem** (Erdős–Herzog–Piranian; erdosproblems.com/1041). Let f be a monic
polynomial of degree n with all roots in the closed unit disk, and
E(f) = {z : |f(z)| < 1}. Erdős, Herzog and Piranian proved (1958) that some
component of E(f) contains two roots, and asked for quantitative control:
must two roots be joined by a short path inside E(f)?

## This work

Two new partial results (both **new**; prior proved configuration classes were
only degree ≤ 4 — Venkata Siddharth Pendyala, arXiv:2606.24875, June 2026 —
plus the qualitative EHP 1958 component theorem; no uniform root-to-root
length bound of any kind was previously recorded).

1. **Collinear case, fully proved** (`proof_collinear.md`): if f is monic of
   degree n ≥ 2 with all roots in the **open** unit disk lying on a common
   line (in particular, all real-rooted f), then two roots (with
   multiplicity; degenerate 0-length paths per the accepted convention) are
   joined inside E(f) by a straight **segment of length < 2**; for distinct
   roots the witness segment joins a pair of *consecutive* roots, with the
   quantitative bound min_i max_{[z_i,z_{i+1}]} |f| ≤ (disc/n^n)^{1/(n−1)} < 1.
   The proof chain is elementary: restriction to the chord, Rolle interlacing,
   the exact identity ∏(gap critical values) = disc/n^n, and a one-line
   Hadamard inequality on the Vandermonde matrix giving disc < n^n strictly.
2. **First explicit uniform bound** (`proof_uniform_bound.md`): for ANY monic
   f of degree n and any component U of E(f) containing m zeros, any two
   zeros in U are joined inside U by a path of length
   ≤ √(mn) + 4πe·n **< 35.2 n**. Combined with EHP's qualitative theorem:
   every monic f with roots in the open unit disk has a pair of roots joined
   by a path of length < 35.2 n. Ingredients proved in full: the critical
   point count crit(f, U) = m−1 via Riemann map + finite Blaschke product;
   connectivity and single-Jordan-curve structure of the top sublevel set;
   monotone ray-preimage transport curves; and a **new sharp integral
   inequality** ∫_{V_s} |f′/f| dA ≤ 2π√(mn)·s^{1/n} (equality at f = z^n),
   via Cauchy–Schwarz + Pólya's area inequality. Citing T. Tao's 2025
   resolution of Erdős #114 (lemniscate length 2n + O(1)) would
   *conditionally* improve 35.2n to 2n + O(1); the headline keeps Borwein's
   unconditional 8πe·n.

## Verification

`./verify.sh` (deterministic, fixed seed; runs `sanity_checks.py` under
`uv run --with numpy --with scipy`; ~1 min) re-checks the numerical
certificates behind both proofs:

- **A1** — the critical-value product identity leg in **exact rational
  arithmetic**; **A2** — the companion identity in floats (max rel. err
  2.4e-10);
- **B** — 720 random + adversarial clustered collinear trials: min-gap
  max|f| < 1 and the quantitative bound hold to machine precision (worst
  max|f| = 0.9988, matching the known tightness of z² − a²);
- **C** — Hadamard margin disc < n^n at near-extremal points, n = 2..30;
- **D** — connectivity of {|f| < s} ∩ U above c_max on random / symmetric /
  degenerate examples (always exactly one subcomponent);
- **E** — grid quadrature of the integral inequality (max ratio 0.999,
  attained by the predicted extremal z⁶).

**Status: ALL CHECKS PASSED** (re-run in this repo, 2026-08-04; single mode —
the script has no heavy mode).

## Trusted base / caveats

- The theorems are **prose proofs** (not formalized); the numerical
  certificates above sanity-check the identities and the analytic lemmas but
  are not the proof. Classical inputs cited on trust: Hadamard's determinant
  inequality (Horn & Johnson); the Riemann mapping theorem; Fatou (proper
  self-maps of the disk = finite Blaschke products; Garnett, *Bounded
  Analytic Functions*, Ch. I); Pólya's 1928 area inequality
  Area({|f| ≤ t}) ≤ πt^{2/n}; P. Borwein's lemniscate length bound 8πe·n
  (Proc. Amer. Math. Soc. 123 (1995) 797–799); Jordan curve theorem; coarea
  formula; Rudin RCA 13.11.
- The 2n + O(1) remark is **conditional**: the exact constant in Tao's #114
  lemniscate theorem was not re-verified (flagged FIXME in
  `proof_uniform_bound.md`); the unconditional headline uses Borwein 1995.
- The integral inequality here is independent of (and for m ≪ n weaker than)
  the bound ∫_U |f′/f| dA ≤ 2πm stated by Terence Tao in the problem's forum
  thread; this work does **not** rely on that forum lemma.
- erdosproblems.com and its forum returned HTTP 403 at write-up time
  (2026-08-03), so the live page could not be re-checked against the recon
  snapshot; the original EHP 1958 p.139 remark context was not re-read.
- Novelty basis: both of Pendyala's 2026 preprints (arXiv:2606.24875,
  arXiv:2606.19178) were fetched and checked 2026-08-03 — neither treats the
  collinear/real-rooted case or any uniform length bound.

## Credit

- Problem: P. Erdős, F. Herzog, G. Piranian, *Metric properties of
  polynomials*, J. Analyse Math. 6 (1958), 125–148; curated by T. F. Bloom,
  erdosproblems.com/1041.
- Prior degree ≤ 4 resolution: **Venkata Siddharth Pendyala**, *A Degree-Four
  Lemniscate Path Theorem*, arXiv:2606.24875 (2026); see also his
  arXiv:2606.19178 (name as it appears on arXiv).
- Lemniscate length bound: **P. Borwein**, *The arc length of the lemniscate
  |p(z)| = 1*, Proc. Amer. Math. Soc. 123 (1995), 797–799.
- Forum context (integral bound ∫|f′/f| ≤ 2πm; autopsy of failed March-2026
  tree strategies): **Terence Tao**, erdosproblems.com forum thread #1041.
