# Erdős #616 — t(6) = 2 and t(7) = 2, via rigidity of minimal empty-intersection families

**Problem** (Erdős–Hajnal–Tuza; erdosproblems.com/616). For an r-uniform set
system in which every subsystem on at most 3r−3 vertices has transversal
number τ ≤ 1, write t(r) for the best-possible global bound on τ
(= t₀(3r−3, r) in EHT91). EHT91 proved ⌊(3/16)r + 7/8⌋ ≤ t(r) ≤ ⌈r/5⌉.

**Novelty framing (corrected against the primary source — see
[`NOVELTY.md`](NOVELTY.md)):** at r = 6, 7 EHT91's floor and ceiling both
equal 2, so **t(6) = t(7) = 2 already follows from EHT91's own results** —
though the paper never evaluates the small cases and no source records these
values. This directory's contribution is the **first explicit recording**,
plus **independent proofs by a genuinely new route** (an exhaustive
MEIF/rigidity classification; EHT91's Theorem 3 proof is a different
argument) **with full machine certificates** — not a discovery-in-the-strong-
sense, and not a refutation of anything in EHT91.

## What this work establishes

Complete elementary proofs in `proofs/proof_t6_t7.md`:

1. **Theorem 1 — t(6) = 2** (finite or infinite systems). Engine (Lemma 3,
   of independent interest): a minimal empty-intersection family (MEIF) of m
   r-sets spans mr − D vertices with deficit D ≥ m(m−2); its span exceeds
   the window 3r−3 iff 3 < m < r−1, and then by at most (m−3)(r−1−m). At
   r = 6 the only survivor is m = 4 with span exactly 16 and **zero slack**:
   the MEIF is forced to be the rigid 4-edge gadget, two of whose edges meet
   in exactly 2 vertices; the 3-wise intersection property forced by the
   window pinches every edge onto that 2-set, so τ ≤ 2. Lower bound: the
   verified 16-vertex gadget.
2. **Theorem 2 — t(7) = 2**. Survivors at r = 7 are (m, span) ∈
   {(4,19), (4,20), (5,19), (5,20)}, rigid up to at most one extra
   doubly-covered vertex; a two-case analysis (m = 4: same pinch; m = 5:
   4-wise intersecting forces every edge to contain ≥ 4 of the 5
   distinguished vertices) gives τ ≤ 2. Two lower-bound witnesses on 20
   vertices.
3. **Erratum against the problem page** (see `NOVELTY.md` §2): the
   erdosproblems.com background paraphrases EHT91's sandwich without
   floor/ceiling (3r/16 + 7/8 ≤ t ≤ r/5), which is self-contradictory for
   every r < 70. The actual EHT91 statements are consistent for all r ≥ 3;
   nothing here contradicts the paper in any form.
4. **Landscape via EHT91** (corrected 2026-08-04): reading EHT91's Theorem
   6(II) directly (rather than its lossy ⌊(3/16)r + 7/8⌋ closed form),
   EHT91's own theorems determine **t(r) = ⌈r/5⌉ for ALL 3 ≤ r ≤ 20** — in
   particular t(8) = t(9) = t(10) = 2 and t(11) = t(12) = 3. The first
   value EHT91 leaves open is **t(21) ∈ {4, 5}**. Full extraction,
   independent elementary proofs for r ≤ 12, and the t(21) frontier
   analysis: [`../erdos-616-landscape/`](../erdos-616-landscape/). The
   rigidity mechanism used here visibly breaks at r = 8 (excess reaches
   4) — which is exactly the gap that sank the retracted Jan 2026 AI claim
   t(r) = 2 for all r ≥ 6.

Companion small-r pack (t(3) = t(4) = t(5) = 1, t(r) ≥ 2 for r ≥ 6,
monotonicity): [`../erdos-616-small-r/`](../erdos-616-small-r/).

## Verification

`./verify.sh` (pure stdlib Python 3; ~30–40 min, dominated by the
falsification searches):

1. `code/classify_minimal.py` — exhaustive enumeration of all MEIF
   type-vectors from the axioms alone (r = 6, 7, all m ≤ r+2), materializing
   every survivor as an explicit family and re-verifying uniformity,
   minimality, empty intersection, span, and every intersection property the
   theorems consume (unique survivor at r = 6; exactly 7 surviving labeled
   type-vectors at m = 4 and 11 at m = 5 for r = 7);
2. `code/gadget_check.py` — both lower-bound gadgets against the literal
   definition (all 58,650 subsets at r = 6; all 988,095 at r = 7); τ = 2
   exactly; plus the Theorem-1 key step verified exhaustively over all
   74,613 one-edge extensions of the gadget on 22 vertices (all 489
   L(6)-compatible extensions meet E₁ ∩ E₂);
3. `code/random_maximal_search.py` — randomized greedy-maximal falsification
   (gadget-planted, unplanted; exact DFS local-property checking): no L(r)
   family with τ ≥ 3;
4. `code/planted_m5_search_r7.py` — Case-B-flavored falsification at r = 7;
5. `code/checker_crossval.py` — the DFS checker cross-validated against a
   literal-definition oracle on 400 families.

**Status (2026-08-04): legs 1–2 PASSED in this repo** (exhaustive
classification; both literal-definition gadget checks; the 74,613-extension
key-step check). Legs 3–4 (the long randomized falsification searches,
supporting evidence only — the proofs do not depend on them) are **still
running at publication time** after an earlier session kill and restart;
no counterexample has been reported in any completed portion, including the
24 planted-control trials (all three structurally relevant regimes) and the
9-trial m=5-planted r=7 search, which completed earlier and passed. Leg 5
(checker cross-validation vs a literal-definition oracle, 400 families) was
run independently by the adversarial referee during the attack wave:
400/400 agreement, on a separate implementation and seed. Re-run everything
from scratch with `./verify.sh` (legs 3–4 take multiple hours).

## Trusted base / caveats

- Elementary self-contained prose proofs + machine certificates; EHT91 is
  context/credit, not a proof dependency. The falsification searches are
  supporting evidence with failure-power, not part of the proofs.
- The "Novelty and priority" section inside `proofs/proof_t6_t7.md` and
  claims 4–5 of `finding_draft_t6t7.json` were **updated 2026-08-04 after
  EHT91 was obtained** (erratum + priority resolution); [`NOVELTY.md`](NOVELTY.md)
  carries the verbatim EHT91 quotes and the full landscape correction
  (t(r) = ⌈r/5⌉ for 3 ≤ r ≤ 20 implicit in EHT91; first open value t(21)).
- The EHT91 PDF is **not** redistributed here; cite
  doi:10.1016/0097-3165(91)90074-Q.

## Credit

- Problem and both bounds: **Paul Erdős, András Hajnal, and Zsolt Tuza**,
  *Local Constraints Ensuring Small Representing Sets*, J. Combin. Theory
  Ser. A 58 (1991) 78–84 (Theorem 3; Section 3 H(r,k,q) construction; the
  values t(6) = t(7) = 2 are implicit in these). Curated by T. F. Bloom,
  erdosproblems.com/616.
- The 4-edge gadget witness traces to the ChatGPT 5.2 Pro transcript posted
  by forum user **jkabrg** (18 Jan 2026; its headline claim was refuted
  in-thread by **TerenceTao**); re-derived independently here.
