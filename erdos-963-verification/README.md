# Erdős #963 — refereeing KoishiChan's forum proof of f(n) ≥ (1−o(1))log₂ n, plus an effectivized bound

**Problem** (Erdős; erdosproblems.com/963). Let f(n) be the largest k such that
every set of n reals contains a **dissociated** subset (all 2^k subset sums
distinct) of size k. Erdős asked whether f(n) ≥ ⌊log₂ n⌋.

**This directory is an independent verification + effectivization, not a
discovery.** The asymptotic theorem f(n) ≥ (1−o(1))log₂ n and its method belong
to forum user **KoishiChan** (proof posted 00:21, 05 Dec 2025, in the
erdosproblems.com/963 discussion thread). Our contribution is the line-by-line
referee report, the repairs, the explicit constants, and the upper-bound
companion note.

## What this work establishes

1. **Referee verdict: the forum proof is CORRECT** (`referee_report.md`, line by
   line). Every load-bearing step checks out: the Dirichlet-character
   second-moment identity, the reduction of difference-p progression sums to
   M(χ), the Montgomery–Vaughan 1979 fourth-moment input, the mod-p splicing,
   the ≤(q−1)/k transport, the r⁻¹ pullback, and the recursion. The one
   substantive error — an off-by-one found in-thread by **Quanyu Tang** (09:00,
   05 Dec 2025) — is repaired by KoishiChan's own in-thread fix (16:52, 05 Dec
   2025), which we verify quantitatively. Three minor presentational gaps
   (positivity reduction stated too strongly; implicit monotonicity of f;
   implicit largeness of the auxiliary prime q) are identified and repaired.
2. **Primary-source check of the key citation**: H. L. Montgomery and
   R. C. Vaughan, *Mean values of character sums*, Can. J. Math. 31 (1979),
   no. 3, 476–487 (doi:10.4153/CJM-1979-053-2), Theorem 1 states
   Σ_{χ≠χ₀} M(χ)^{2k} ≪_k φ(q)·q^k for any real k > 0 — no log factors, no
   primality assumption on q; with k = 2 this is exactly the ≪ q³ bound the
   post uses. (The post's spelling "Vaughen" is a typo.)
3. **New — effectivized theorem** (`proof_main.md`, the formal write-up
   Thomas Bloom requested in-thread on 23 Jan 2026):
   f(n) ≥ log₂ n − 2(log₂ max(log₂ n, 2))² − D for all n ≥ 4, with D
   effectively computable from the Montgomery–Vaughan implied constant
   (D = 362 if that constant is ≤ 1).
4. **New — constant improvement**: the parameters as posted give asymptotic
   error coefficient 1/(2log₂(12/11)) ≈ 3.983; taking p = 2^m (Terence Tao's
   in-thread suggestion, 05 Dec 2025) plus a union bound over only the m+1
   residue classes actually consumed improves this to
   1/(2log₂(4/3)) + o(1) ≈ 1.2047.
5. **New — upper-bound reduction** (`proof_upper_reduction.md`): the interval
   witness value d({1..n}) is by definition the Erdős #1 (distinct subset
   sums) extremal function, and an exact additivity lemma
   d(A₁ ∪ M·A₂) = d(A₁) + d(A₂) shows separated multi-scale constructions can
   never beat the single interval — so improving the #963 upper bound via
   subsets of [n] *is* the Erdős #1 conjecture.

The floor conjecture f(n) ≥ ⌊log₂ n⌋ for **all** n remains open (the error
term here has the wrong sign at every finite scale). See
[`../erdos-963-small-n/`](../erdos-963-small-n/) for the exact small-n table.

## Verification

`./verify.sh` (pure-stdlib Python 3, deterministic, seeded; < 1 s) re-checks
every machine-checkable claim behind the write-up:

- `fourier` — exact verification of the character-orthogonality/second-moment
  identity against brute-force enumeration over all dilations at q = 61, 101;
- `apbound` — the |S_B(χ)| ≤ 2M(χ) bound for difference-p progressions,
  per character;
- `splice` / `transport` — exhaustive signed-sum verification of the splicing
  and transport lemmas on random instances;
- `unroll` / `thresholds` — the recursion bookkeeping Σ m_j ≥ g − 2(log₂ g)² − g*
  validated to g = 10⁶, and the claimed numeric thresholds (g* = 361 for
  C_MV ≤ 1; W-inequality threshold g ≥ 204) recomputed.

**Status: ALL CHECKS PASSED** (re-run in this repo, 2026-08-04; single mode —
the script has no heavy mode).

## Trusted base / caveats

- The sole external analytic input is **Montgomery–Vaughan 1979, Theorem 1**,
  taken on trust from the published paper (verified against the paper itself
  during the attack; the PDF is *not* redistributed here — see the DOI above).
  Its implied constant C_MV is effective in principle but not extracted; D in
  the effectivized theorem is numeric only under the assumption C_MV ≤ 1.
- The refereed object is a **forum post**, cached during the attack from the
  Internet Archive snapshot of 2026-07-09
  (web.archive.org/web/20260709213826/https://www.erdosproblems.com/forum/thread/963;
  the live page returned HTTP 403). The capture is *not* redistributed here
  (copyright); the URLs above are the citation. `verify.sh` does not depend
  on it.
- Status context (as of 2026-08-03): erdosproblems.com/963 still reads OPEN on
  the latest verifiable snapshot; Thomas Bloom said in-thread he would mark it
  solved pending a formal write-up; no write-up or arXiv preprint was found.
  This document is, to our knowledge, the first complete formal write-up.
- Mathematical proofs (`proof_main.md`, `proof_upper_reduction.md`,
  `referee_report.md`) are prose proofs, human/agent-checked, **not**
  formalized; the machine checks cover the identities, lemma instances, and
  numeric bookkeeping listed above.

## Credit

- Asymptotic theorem f(n) ≥ (1−o(1))log₂ n and proof method: **KoishiChan**
  (erdosproblems.com forum, 05 Dec 2025; username as it appears in the thread).
- Off-by-one correction: **Quanyu Tang** (in-thread, 05 Dec 2025).
- p = 2^m optimization suggestion: **TerenceTao** (in-thread, 05 Dec 2025).
- Write-up request and screening: **Thomas Bloom** (in-thread, 23 Jan 2026);
  problem curated by T. F. Bloom, erdosproblems.com/963.
- Analytic input: **H. L. Montgomery and R. C. Vaughan**, *Mean values of
  character sums*, Can. J. Math. 31 (1979) 476–487, Theorem 1.
- Context on the Erdős #1 side: Q. Dubroff, J. Fox, M. W. Xu,
  arXiv:2006.12988.
