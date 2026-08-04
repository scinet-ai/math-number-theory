# Novelty status — corrected against the primary source (EHT91)

This note supersedes the "Novelty and priority" section of
`proofs/proof_t6_t7.md` and claims 4–5 of `finding_draft_t6t7.json`, which
were written while EHT91 was inaccessible ("paywalled, could not be read").
The paper has since been obtained and read in full (2026-08-04):

> P. Erdős, A. Hajnal, Zs. Tuza, *Local constraints ensuring small
> representing sets*, J. Combin. Theory Ser. A **58** (1991) 78–84,
> doi:10.1016/0097-3165(91)90074-Q
> (sciencedirect.com/science/article/pii/009731659190074Q).

In the paper's notation, the problem's t(r) is t₀(3r−3, r).

## What EHT91 actually states

- **Theorem 3 (p. 80), verbatim**: "THEOREM 3. *For r ≥ 3,*
  (3r−3, 1) →_r ⌈r/5⌉." — a **ceiling**, unrestricted in r.
- **Lower bound (p. 80), verbatim**: "For t₀(3r−3, r) a somewhat weaker
  lower bound of ⌊(3/16)r + 7/8⌋ can be obtained from a construction given
  in Section 3." — a **floor**.
- **The construction (p. 84 concluding remark)**: x = ⌊(3/16)r − 1/8⌋,
  q = 2x+1, k = 3x+1; H(r, k, q) has every subsystem on ≤ 3r−3 elements
  coverable by one element and τ = x+1.

## Consequences for this directory's claims

1. **t(6) = 2 and t(7) = 2 follow from EHT91's own results.** At r = 6, 7
   the floor lower bound is ⌊18/16 + 14/16⌋ = ⌊35/16⌋ = 2 and Theorem 3's
   ceiling upper bound is ⌈6/5⌉ = ⌈7/5⌉ = 2 — so the sandwich closes.
   **These values are nowhere recorded in the paper** (it never evaluates
   the small cases, and no later source located records them), but they are
   a one-line consequence of its two displayed results. The correct claim
   for this directory is therefore: **first explicit recording of
   t(6) = t(7) = 2, with independent proofs by a genuinely new route**
   (the exhaustive MEIF/rigidity classification — EHT91's Theorem 3 proof
   is a different, non-classification argument via its Theorem 6 machinery)
   **and full machine certificates** — NOT "first exact values" in the
   discovery sense, and NOT a refutation of anything in EHT91.
2. **The "internal inconsistency of the sandwich for r < 70" claim is TRUE
   ONLY of the erdosproblems.com background's paraphrase**, which drops the
   floor and ceiling (3r/16 + 7/8 ≤ t ≤ r/5; at r = 7 it would read
   2.1875 ≤ t(7) ≤ 1.4). The **actual** EHT91 statements are mutually
   consistent for **all** r ≥ 3: ⌊(3/16)r + 7/8⌋ ≤ ⌈r/5⌉ everywhere,
   including r < 70. Reframe: this is an **ERRATUM against the problem
   page's background text**, not a caveat about the paper; the write-up's
   speculation that EHT91's statements "must carry unstated
   asymptotic/range caveats" is **withdrawn**. t(7) = 2 does not contradict
   EHT91 in any form: ⌊(3/16)·7 + 7/8⌋ = 2 ≤ 2 = ⌈7/5⌉. The erratum is
   two-sided: besides the floorless/ceilingless rendering, the page's
   3r/16-type lower bound also **understates** EHT91's actual lower-bound
   strength — the paper's Theorem 6(II) yields matching lower bounds
   ⌈r/5⌉ for all r ≤ 20 (see §4).
3. **One EHT91-internal wrinkle worth recording** (p. 84): the concluding
   display asserts "(3r−3, 1) ↛_r ⌊(3/16)r + 7/8⌋", but the construction it
   invokes has τ(F) = x + 1 with x = ⌊(3/16)r − 1/8⌋, which witnesses only
   (3r−3, 1) ↛_r x — i.e. t₀(3r−3, r) ≥ x + 1 = ⌊(3/16)r + 7/8⌋, one less
   than the display's ↛ asserts. The display is off by one against the
   paper's own construction; p. 80's phrasing ("lower bound of
   ⌊(3/16)r + 7/8⌋") is the intended, consistent claim and is what this
   repo attributes to EHT91.
4. **Landscape (corrected 2026-08-04, superseding an earlier version of this
   note that called t(11) the first open value)**: EHT91's closed-form floor
   ⌊(3/16)r + 7/8⌋ is a *lossy* corollary of its own Theorem 6(II). Reading
   Theorem 6(II) directly — p(r,t,m) = ⌈m/t⌉(r−m−t) + 2r−m; e.g.
   p(11,2) = 31 at m = 3 gives (30,1) ↛₁₁ 2, hence t(11) ≥ 3 —
   **EHT91's own theorems determine t(r) = ⌈r/5⌉ for ALL 3 ≤ r ≤ 20**
   (so in particular t(8) = t(9) = t(10) = 2 and t(11) = t(12) = 3). The
   first value EHT91 genuinely leaves open is **t(21) ∈ {4, 5}**. No exact
   value below r = 21 is new to this workspace; priority for all r ≤ 20
   values belongs to EHT91, and our proofs are independent verification
   with new machinery. Full extraction + independent elementary proofs for
   r ≤ 12: [`../erdos-616-landscape/`](../erdos-616-landscape/).

## Corrected credit line

- t(r) ≤ ⌈r/5⌉ (r ≥ 3) and t(r) ≥ ⌊(3/16)r + 7/8⌋: **Erdős–Hajnal–Tuza
  1991** (Theorem 3; Section 3 construction). The numerical coincidence
  t(6) = t(7) = 2 is implicit in their paper.
- Explicit recording of t(6) = t(7) = 2, the MEIF deficit/rigidity
  classification (span = mr − D, D ≥ m(m−2), survivor window 3 < m < r−1
  with excess (m−3)(r−1−m)), the two-case τ ≤ 2 arguments, and all machine
  certificates: this work.
- The 4-edge gadget lower-bound witness traces to the (overall refuted)
  jkabrg transcript; re-derived independently.
