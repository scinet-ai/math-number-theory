# Erdős #616 — the r ≤ 20 landscape t(r) = ⌈r/5⌉ extracted from EHT91, independent elementary proofs for r ≤ 12, and the first open value t(21) ∈ {4,5}

**Problem** (Erdős–Hajnal–Tuza; erdosproblems.com/616). For an r-uniform set
system in which every subsystem on at most 3r−3 vertices has transversal
number τ ≤ 1, write t(r) for the best-possible global bound on τ
(= t₀(3r−3, r) in EHT91).

**Priority framing — read first.** This directory is a **landscape
extraction + erratum + independent verification**, not a discovery of new
exact values. Reading EHT91's Theorem 6(II) directly — the reduction
p(r,t,m) = ⌈m/t⌉(r−m−t) + 2r−m with its H(r,k,q) construction, e.g.
p(11,2) = 31 at m = 3 gives (30,1) ↛₁₁ 2, hence t(11) ≥ 3 — rather than the
paper's lossy closed-form corollary ⌊(3/16)r + 7/8⌋ (p. 84), **EHT91's own
theorems determine t(r) = ⌈r/5⌉ for ALL 3 ≤ r ≤ 20** (in particular
t(8) = t(9) = t(10) = 2, t(11) = t(12) = 3). The paper never tabulates this.
**Priority for every r ≤ 20 value belongs to EHT91**; the first value their
results leave open is **t(21) ∈ {4, 5}** (the full undetermined set below 60
is {21, 26, 31, 36, 37, 41, 42, …}).

## What this work contributes

Complete write-up in `proof_t8_t11.md`:

1. **Erratum (two-sided) against the problem page's background**: the
   displayed sandwich 3r/16 + 7/8 ≤ t ≤ r/5 (i) drops the floor/ceiling,
   creating a spurious inconsistency for r < 70 and pinning no value beyond
   r ≤ 5, and (ii) **understates the paper's lower bound** — the closed form
   loses up to one unit of τ versus the construction it summarizes (e.g. at
   r = 16 the floor gives only t(16) ≥ 3, while H(16,10,7) itself gives
   t(16) ≥ 4 = t(16)).
2. **A new, self-contained elementary proof of t(r) = 2 for 6 ≤ r ≤ 10**
   (Fatness Lemma for minimal empty-intersection families + a
   minimal-MEIF-size chain argument), methodologically disjoint from
   EHT91's Theorem 6(I) proof, with exhaustive machine certificates over
   the full survivor landscape (589 / 46,668 / 8,271,972 MEIF type-vectors
   at r = 8/9/10; zero escape the lemma).
3. **Self-contained elementary proofs of t(11) = 3 and t(12) = 3** (upper
   bounds by a sharpened fatness argument; lower bounds = EHT91's witness
   H(r,7,5), given a short self-contained correctness proof and full
   machine certification — at H(11,7,5) the local property is *tight*:
   minimum bad-subfamily span 31 against threshold 31).
4. **Rigorous extraction of the r ≤ 20 landscape and the t(21) frontier**:
   the exact validity threshold r₀(t) = 5t + 1 + ⌊(t−1)/3⌋ for the EHT91
   construction; machine verification of all witnesses H(r,7,5)
   (r = 11..15, τ = 3) and H(r,10,7) (r = 16..20, τ = 4); and a proof that
   the **entire H(r,k,q) family fails at r = 21** for τ ≥ 5 (razor-thin:
   p(21,4) = 61 = (3·21−3) + 1), so t(21) needs a genuinely new
   construction or a better upper bound.
5. **Structure theory at the jump r = 11**: exactly 10 labeled MEIF
   type-vectors at (r,m) = (11,4) are "3-fat"; every τ ≥ 3 example at
   r = 11 must contain 4-edge MEIFs, all 3-fat; H(11,7,5) realizes exactly
   this structure — the template for attacking t(21).

Companion dirs: [`../erdos-616-small-r/`](../erdos-616-small-r/)
(t(3)=t(4)=t(5)=1, monotonicity),
[`../erdos-616-t6-t7/`](../erdos-616-t6-t7/) (t(6)=t(7)=2 via rigidity).

## Verification

`./verify.sh` (pure stdlib Python 3; ~5 min for steps 1–5, plus a
randomized falsification step 6 of ~30–60 min; `--quick` reduces step 6):

1. `classify_fatness.py` — exhaustive survivor type-vector classification +
   Fatness Lemma at r = 8, 9, 10, with the r = 11 negative control (the
   3-fat detector fires there, so its silence at r ≤ 10 has failure-power);
2. `independent_check.py` — covering-exhaustion double-check + a second,
   code-disjoint r = 8 enumeration;
3. `gadget_check_r8.py` — r = 8 lower-bound witnesses by literal bitmask
   sweeps + planted-bug negative control;
4. `witness_t11.py` — H(r,7,5) for r = 11..15 (τ = 3 exact) and H(r,10,7)
   for r = 16..20 (τ = 4 exact), local property certified, plus negative
   controls (H(10,7,5) and H(15,10,7) correctly violate L(r));
5. `eht_landscape.py` — the Theorem-3 reduction inequality and the pinned
   r ≤ 20 landscape; exhaustion of the H(r,k,q) family at r = 21;
6. `search_tau3.py` — randomized τ ≥ 3 falsification search at r = 8.

**Status (2026-08-04): steps 1–5 PASSED in this repo** (classification
counts 589/46,668/8,271,972 reproduced; all witnesses certified; landscape
extraction confirmed; "H(r,k,q) exhausted at r=21" confirmed). Step 6 (the
long randomized search, supporting evidence only) ran to the end of its
trial list in this repo with every completed trial at τ = 2 — including all
planted-m6 controls — and no counterexample; the workspace's original run's
24 planted-control trials also passed (`search_run.log` snapshot). All
proof-bearing checks are steps 1–5.

## Trusted base / caveats (disclosed)

- **Upper bounds for 13 ≤ r ≤ 20 cite EHT91 Theorem 3** ((3r−3,1) →_r
  ⌈r/5⌉) rather than being re-proved here; the independent elementary upper
  bounds cover r ≤ 12 only.
- **r = 10 materialization is a deterministic sample**: the classification
  identity is checked at the count level on **all** 8,271,972 survivor
  type-vectors, but explicit set-family materialization + set-level
  re-verification covers all survivors at r = 8, 9 and a deterministic
  sample of **8,275** survivors (plus all extremal/3-fat candidates) at
  r = 10.
- The staged `search_run.log` is a **snapshot**: a reduced *unplanted*
  falsification supplement may still be appending to the log in the source
  workspace at staging time (its results are supporting evidence only; the
  proofs do not depend on the randomized search).
- The EHT91 PDF is **not** redistributed (the proof's `../sources/` pointers
  refer to the attack workspace); cite doi:10.1016/0097-3165(91)90074-Q.
  No verification code reads the PDF.

## Credit

- **All exact values t(r) for r ≤ 20 are implicit in**: **Paul Erdős,
  András Hajnal, and Zsolt Tuza**, *Local Constraints Ensuring Small
  Representing Sets*, J. Combin. Theory Ser. A 58 (1991) 78–84 — Theorem 3
  (upper bounds), Theorem 6(II) + Section 3 H(r,k,q) construction (lower
  bounds). Curated by T. F. Bloom, erdosproblems.com/616.
- The landscape extraction, the Fatness-Lemma method (r ≤ 12), the r₀(t)
  threshold, the r = 21 frontier analysis, and all machine certificates:
  this work.
