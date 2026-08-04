# Novelty status — corrected against the primary source (EHT91)

This note supersedes the priority discussion in `proof_small_r.md` §6 and in
`finding_draft.json` (claim 5), which were written while EHT91 was
inaccessible ("paywalled, could not be read"). The paper has since been
obtained and read in full (2026-08-04):

> P. Erdős, A. Hajnal, Zs. Tuza, *Local constraints ensuring small
> representing sets*, J. Combin. Theory Ser. A **58** (1991) 78–84,
> doi:10.1016/0097-3165(91)90074-Q
> (sciencedirect.com/science/article/pii/009731659190074Q).

In the paper's notation, the problem's t(r) is t₀(3r−3, r): the smallest t
for which (3r−3, 1) →_r t.

## What EHT91 actually states

- **Theorem 3 (p. 80), verbatim**: "THEOREM 3. *For r ≥ 3,*
  (3r−3, 1) →_r ⌈r/5⌉." — a **ceiling**, unrestricted in r. Immediately
  below: "For t₀(3r−3, r) a somewhat weaker lower bound of ⌊(3/16)r + 7/8⌋
  can be obtained from a construction given in Section 3."
- **Lower-bound construction (p. 84 concluding remark)**: put
  x = ⌊(3/16)r − 1/8⌋, q = 2x+1, k = 3x+1; the set system H(r, k, q) of
  Section 3 has every subsystem on ≤ 3r−3 elements coverable by one element,
  "However, τ(F) = x + 1."

## Consequences for this directory's claims

1. **t(3) = t(4) = t(5) = 1 is IMPLICIT in EHT91**: Theorem 3 gives
   t(r) ≤ ⌈r/5⌉ = 1 for r ≤ 5 (and t ≥ 1 is trivial). The paper never states
   the small cases explicitly — it evaluates no small values anywhere — but
   they follow at once from its Theorem 3. **Theorem A here is therefore an
   independent, self-contained proof of a result implicit in EHT91, not a
   discovery.** Our contribution: the explicit statement, elementary proofs
   independent of EHT91's Section 4 machinery, the exact-threshold framing
   (r = 6 is where the window argument breaks), the monotonicity theorem,
   and the machine certificates.
2. **The "displayed bounds cannot be literally valid at small r" observation
   is an ERRATUM against the erdosproblems.com background, not against the
   paper.** The problem page paraphrases the sandwich floorlessly/ceilinglessly
   as 3r/16 + 7/8 ≤ t(r) ≤ r/5, which is indeed self-contradictory for
   r < 70 (e.g. at r = 5 it reads 1.8125 ≤ t ≤ 1). The **actual** EHT91
   statements — lower bound ⌊(3/16)r + 7/8⌋ (floor), upper bound ⌈r/5⌉
   (ceiling) — are mutually consistent for **all** r ≥ 3. The speculation in
   the write-up that the original statements "must carry unstated
   asymptotic/range caveats" is **withdrawn**: they carry floors and
   ceilings, nothing more. The erratum is two-sided: the page's 3r/16-type
   lower bound also **understates** the paper — EHT91's Theorem 6(II), read
   directly rather than through the lossy floor corollary, yields matching
   lower bounds ⌈r/5⌉ for all r ≤ 20, so **EHT91's own theorems determine
   t(r) = ⌈r/5⌉ for all 3 ≤ r ≤ 20**, with the first genuinely open value
   t(21) ∈ {4, 5} (extraction + independent proofs:
   [`../erdos-616-landscape/`](../erdos-616-landscape/)).
3. **One EHT91-internal wrinkle worth recording** (p. 84): the concluding
   display claims "(3r−3, 1) ↛_r ⌊(3/16)r + 7/8⌋", but its own construction
   has τ(F) = x + 1 with x = ⌊(3/16)r − 1/8⌋, which witnesses
   (3r−3, 1) ↛_r x, i.e. exactly t₀(3r−3, r) ≥ x + 1 = ⌊(3/16)r + 7/8⌋ —
   one less than the display asserts. The p. 80 phrasing ("a somewhat weaker
   **lower bound of** ⌊(3/16)r + 7/8⌋") is the intended, consistent claim,
   and is what this repo attributes to EHT91.

## Corrected credit line

- t(r) ≤ ⌈r/5⌉ for all r ≥ 3 (hence t(3)=t(4)=t(5)=1 implicitly):
  **Erdős–Hajnal–Tuza 1991, Theorem 3**.
- Explicit statement of the small-r values, self-contained elementary proofs
  (window/span-counting), the r = 6 threshold framing, monotonicity
  t(r+1) ≥ t(r), and all machine certificates: this work.
- The span-counting route and the 4-edge gadget were first proposed in this
  problem's forum context in the (overall refuted) ChatGPT 5.2 Pro
  transcript posted by jkabrg (18 Jan 2026); re-derived independently here.
