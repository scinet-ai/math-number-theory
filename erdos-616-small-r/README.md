# Erdős #616 — small-r pack: t(3) = t(4) = t(5) = 1, t(r) ≥ 2 for r ≥ 6, monotonicity

**Problem** (Erdős–Hajnal–Tuza; erdosproblems.com/616). For an r-uniform set
system in which every subsystem on at most 3r−3 vertices has transversal
number τ ≤ 1, how large can the global τ be? Write t(r) for the best-possible
global bound (= t₀(3r−3, r) in EHT91's notation). EHT91 proved
⌊(3/16)r + 7/8⌋ ≤ t(r) ≤ ⌈r/5⌉.

**Novelty framing (corrected against the primary source — see
[`NOVELTY.md`](NOVELTY.md)):** t(3) = t(4) = t(5) = 1 is *implicit* in EHT91
(Theorem 3 gives t(r) ≤ ⌈r/5⌉ = 1 for r ≤ 5), though never stated there —
the paper evaluates no small cases. This directory's contribution is the
**explicit statement, independent self-contained proofs, and machine
certificates**, not a discovery.

## What this work establishes

All proofs complete and elementary, in `proof_small_r.md`:

1. **Theorem A**: t(3) = t(4) = t(5) = 1 — for r ≤ 5 the 3r−3-local
   condition forces a global common vertex. Engine: every inclusion-minimal
   empty-intersection family of m r-sets has 2 ≤ m ≤ r+1 and spans at most
   m(r−m+2) vertices; max_m m(r−m+2) = 3r−3 exactly for r = 3, 4, 5, so any
   witness to τ ≥ 2 sits inside a forbidden window.
2. **Theorem B**: t(r) ≥ 2 for every r ≥ 6, via an explicit 4-edge gadget
   E_i = ({a₁,a₂,a₃,a₄}∖{a_i}) ∪ B_i on 4r−8 vertices (three-wise
   intersecting, empty total intersection, span 4r−8 > 3r−3). This agrees
   with EHT91's own lower bound ⌊(3/16)r + 7/8⌋ = 2 at r = 6; its value here
   is the fully self-contained, certificate-checked construction.
3. **Theorem C (monotonicity)**: t(r+1) ≥ t(r) for all r ≥ 3, via a
   pendant-vertex extension preserving both the local property and τ
   exactly (no criticality hypothesis).
4. **Threshold framing**: r = 6 is exactly where the local condition stops
   forcing τ = 1, and m = 4 (span 16 > 15) is the unique arithmetic escape
   at r = 6.

Exact values beyond the τ = 1 range: see
[`../erdos-616-t6-t7/`](../erdos-616-t6-t7/) (t(6) = t(7) = 2).

## Verification

`./verify.sh` (stdlib Python 3 for the main script; scipy/numpy for the LP
cross-check, skipped with a warning if absent; ~seconds):

- `code/verify_616.py` — the arithmetic core of Theorem A; the gadget's
  local property verified both by the proved subfamily criterion (all
  6 ≤ r ≤ 40) and by raw-definition exhaustive enumeration over all 2¹⁶
  (r = 6) and 2²⁰ (r = 7) vertex subsets; τ = 2 exactly; pendant extension
  checks to uniformity 12; **negative controls** (the same gadget at r = 5
  is correctly flagged as violating the local condition, and a planted-bug
  test at 2²⁰ scale is caught — the checkers have failure-power).
- `code/verify_atoms_lp.py` — an LP over the atom (Venn-cell) formulation
  certifying the span bound m(r−m+2) is exactly right for all 3 ≤ r ≤ 12,
  2 ≤ m ≤ r+1, plus failure-power controls (dropping minimality raises the
  optimum to mr; a wrong formula does not match).

**Status: ALL VERIFICATIONS COMPLETE** (re-run in this repo, 2026-08-04;
single mode; the scipy LP leg was available and PASSED — nothing skipped).

## Trusted base / caveats

- Elementary self-contained prose proofs + machine certificates; no external
  theorem is used in the proofs themselves. EHT91 is context/credit, not a
  dependency.
- The erdosproblems.com/616 background paraphrases EHT91's sandwich without
  floor/ceiling (3r/16 + 7/8 ≤ t ≤ r/5), which is self-contradictory for
  r < 70; the actual EHT91 statements (floor lower bound, ceiling upper
  bound) are consistent for all r — and the page's lower bound also
  *understates* the paper: EHT91's Theorem 6(II) yields matching lower
  bounds, so its own theorems determine t(r) = ⌈r/5⌉ for all 3 ≤ r ≤ 20
  (first open: t(21) ∈ {4,5}; see
  [`../erdos-616-landscape/`](../erdos-616-landscape/)). Treat the older
  "the EHT bounds carry unstated caveats" language in `proof_small_r.md` §6
  / `finding_draft.json` as superseded by [`NOVELTY.md`](NOVELTY.md) — it
  is a two-sided erratum against the problem page's paraphrase, not against
  the paper.
- The EHT91 PDF is **not** redistributed here; cite
  doi:10.1016/0097-3165(91)90074-Q.

## Credit

- Problem and both bounds: **Paul Erdős, András Hajnal, and Zsolt Tuza**,
  *Local Constraints Ensuring Small Representing Sets*, J. Combin. Theory
  Ser. A 58 (1991) 78–84 (Theorem 3: (3r−3,1) →_r ⌈r/5⌉; p. 80/p. 84:
  lower bound ⌊(3/16)r + 7/8⌋ via the H(r,k,q) construction). Curated by
  T. F. Bloom, erdosproblems.com/616.
- The span-counting route and the 4-edge gadget first appeared in this
  problem's context in the ChatGPT 5.2 Pro transcript posted by forum user
  **jkabrg** (18 Jan 2026) — whose headline claim (t(r) = 2 for all r ≥ 6)
  was wrong and is not used; the fatal Step 4 was identified in-thread by
  **TerenceTao** and **Nat Sothanaphan** (usernames as they appear in the
  thread). The fragments used here are re-derived independently and proved
  in full.
