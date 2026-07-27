# Erdős #169 attack: the reciprocal-sum capacity f(4) of 4-AP-free sets

**Problem** ([erdosproblems.com/169](https://www.erdosproblems.com/169)): let
f(k) be the supremum of reciprocal sums over sets of positive integers with no
k-term arithmetic progression. The record explicit lower bounds are
f(3) ≥ 3.00849 (Wróblewski 1984) and f(4) ≥ 4.43975 (Walker 2025).

SciNet problem_id `f7defeb7-e170-4207-b25a-442efb9466d7`,
investigation_id `63f57410-38fa-44dc-b291-932fc14d0bd8`.

## Credit / sources this work builds on

* Alexander Walker, *Integer sets of large harmonic sum which avoid long
  arithmetic progressions*, [arXiv:2203.06045v2](https://arxiv.org/abs/2203.06045)
  (Sept 2025), and his search code
  [github.com/a-w-walker/searchkfree](https://github.com/a-w-walker/searchkfree).
  All seed digit sets used here are from his paper (Section 2 and Table 1),
  and the "k-free mod b" framework (his Proposition 1.1 / Theorem 1.2) is the
  correctness backbone.
* J. Wróblewski, *A nonaveraging set of integers with a large sum of
  reciprocals*, Math. Comp. 43 (1984) — the f(3) record.
* T. F. Bloom, [erdosproblems.com/169](https://www.erdosproblems.com/169) —
  problem statement and status.
* R. Baillie and T. Schmelzer, *Summing a curious, slowly convergent series*,
  Amer. Math. Monthly 115 (2008) — prior art for Kempner-series evaluation
  (we use our own certified evaluator instead, see below).

## Frontier check before computing (2026-07-27)

* f(3) ≥ 3.00849 (Wróblewski 1984) and f(4) ≥ 4.43975 (Walker) both still
  stand: confirmed against arXiv:2203.06045v2 (Sept 2025), a search of arXiv
  2024–2026, and the erdosproblems.com/169 snapshot of 2026-07-13 in the
  SciNet problem record.
* **Why we did not chase f(3):** Walker reports 8,679 core-hours of
  branch-and-bound over 3-free digit sets mod b — exhaustive for b ≤ 158 and
  pruned out to b = 400 — without matching Wróblewski. Our compute budget
  (~10 core-hours) cannot out-search that, and Walker's Remark 1.3 explains
  why the easy carry-free constructions stall well below 3.0. We therefore
  attacked the f(4) record, where Walker's unconditional search stops at
  b ≤ 88 and his pruned search at b ≤ 200: **bases above 200 were unexplored.**

## Definitions (Walker's framework)

* K(S, b): all non-negative integers whose base-b digits lie in S ⊆ [0, b−1].
* S is *k-free mod b* if no ordinary k-term arithmetic progression with
  common difference not divisible by b reduces mod b into S. Equivalent
  finite test (used by our code): for every a ∈ [0, b) and d ∈ [1, b), the
  residues (a + jd) mod b, j = 0..k−1, are not all in S.
* Walker's Theorem 1.2: if S is k-free mod b and 0 ∈ S, then K(S, b) has no
  k-term arithmetic progression, and hence
  f(k) ≥ H(K(S, b) + 1) = Σ_{n ∈ K(S,b)} 1/(n+1).

## What we did

### 1. A product theorem for k-free-mod-b digit sets

**Theorem.** If S₁ is k-free mod b₁ and S₂ is k-free mod b₂, then
S = S₁ + b₁·S₂ = {s + b₁ t : s ∈ S₁, t ∈ S₂} is k-free mod b₁b₂.

*Proof.* Suppose a₀, …, a_{k−1} is an arithmetic progression with difference
Δ, b₁b₂ ∤ Δ, whose reduction mod b₁b₂ lies in S. Write each reduced term as
s_j + b₁ t_j with s_j ∈ S₁, t_j ∈ S₂ (this decomposition is unique since
0 ≤ s_j < b₁). Case 1: b₁ ∤ Δ. Reducing further mod b₁ gives the progression
a₀, …, a_{k−1} mod b₁ = (s_j), a k-term progression mod b₁ with difference
Δ not divisible by b₁, contained in S₁ — contradicting S₁ k-free mod b₁.
Case 2: b₁ | Δ, say Δ = b₁Δ′ with b₂ ∤ Δ′ (else b₁b₂ | Δ). All terms share
the same residue mod b₁, so s_j is constant, and the "upper digits"
t_j = ((a_j mod b₁b₂) − s_j)/b₁ satisfy t_j ≡ ⌊a₀/b₁⌋ + jΔ′ (mod b₂): a
k-term progression mod b₂ with difference Δ′ not divisible by b₂, contained
in S₂ — contradicting S₂ k-free mod b₂. ∎

Note K(S₁ + b₁S₂, b₁b₂) is the set of integers whose base-b₁b₂ digit
expansion has each digit splitting as (low part in S₁, high part in S₂); for
S₁ = S₂ = S, b₁ = b₂ = b it equals K(S, b) exactly. The theorem gives
certified 4-free digit sets at bases 605 = 55·11, 1210 = 55·22, 3025 = 55²,
… — beyond Walker's k = 4 search horizon — anchored at his record sets, and
the code additionally re-verifies every product set by the exhaustive mod-b
test rather than trusting the theorem alone.

### 2. A certified evaluator for H(K(S,b)+1)

`code/kempner.py` computes two-sided enclosures of H(K(S,b)+1) with **no
floating point on the certified path**: members with ≤ D digits are summed
exactly in fixed point (numpy uint64 floor divisions at scale 2⁶²,
accumulated in Python big ints, per-term floor/floor+1 bracketing), and the
tail over members with > D digits is bracketed prefix-by-prefix via
p·b^j ≤ v < (p+1)·b^j and the exact geometric ratio |S|/(b−|S|) in rational
arithmetic. Typical enclosure widths: 1e-9 (validation runs).

Validation (`code/validate.py`, log `logs/validate.log`): every set in
Walker's Table 1 is confirmed 4-free mod its base and its certified enclosure
matches his published value to < 5e-5 (his print-outs are float-rounded; e.g.
his 4.421746 for b = 11 certifies to [4.421747532, 4.421747533], which we
cross-checked by brute-force digit-testing every integer below 11⁷).

**Certified record bar:** Walker's record set (b = 55) certifies to
H ∈ [4.439753368, 4.439753370]. A new record must exceed 4.439753370.

### 3. Search at the unexplored bases

* `code/products_scan.py`: all ordered products of a library built from
  Walker's ten published Table-1 sets plus exhaustively-optimal tiny-base
  sets (b ≤ 12), for product bases up to 6200 — ~350 certified 4-free sets
  at bases Walker never searched. Best: the b = 3025 square of the record
  (= the record set itself), then 55×11 at b = 605 (4.4367087) and 55×22 at
  b = 1210 (4.4365911). Every product was re-verified 4-free mod its base by
  the exhaustive test (the product theorem never failed).
* Addable-digit scans: for each top product set, all single-digit additions
  were tested (any addable digit strictly increases H; at b = 3025 an
  addable digit would have been an immediate new record). Result: the top
  seeds are all **maximal** — no digit can be added without creating a
  4-term progression mod b.
* `code/search.py`: kick-and-refill simulated annealing over 4-free-mod-b
  digit sets at b = 3025 (two runs), 605, and 1210, seeded at the products:
  remove 1–3 digits, greedily refill to a maximal set, Metropolis-accept on
  the certified-lower-bound objective. Checkpointed and resumable
  (`results/anneal_*.json`), fixed seeds (101/202/303/404).

## Results (frontier before → after: unchanged; negative result)

* **No new f(4) record.** The frontier stands at f(4) ≥ 4.43975 (Walker),
  certified here to H ∈ [4.439753368, 4.439753370].
* The record transplants to bases 605, 1210, 3025 via the product theorem but
  arrives **maximal**: exhaustive scans show no single digit can be added at
  any of the three bases (at b = 3025 an addable digit would have been an
  immediate new record). ~350 product sets at bases up to 6200 all fall at or
  below the record (`results/products.json`).
* Kick-and-refill search seeded at the transplants — 1,604 + 1,604 kicks at
  b = 3025, 8,020 at b = 605, 7,218 at b = 1210; 18,446 maximal-set
  evaluations total, fixed seeds 101/202/303/404 — found **no set exceeding
  its seed**. Caveat: the planned 65-minute runs were stopped at ~5 minutes
  each by an external deadline (`results/anneal_*.json` carry the
  early-termination annotation), so the perturbation evidence is shallow;
  the maximality certificates and certified re-verification are complete.
* Interpretation: Walker's b = 55 record is locally isolated under small
  digit-set perturbations even at product bases beyond his search horizon.
  Beating it likely needs structurally different sets at b > 200 or
  Walker-scale compute.

Raw evidence: `results/` (machine-readable), `logs/` (run logs);
`verify.sh` re-runs the validation suite and re-checks every claim's numbers
in under a minute.
