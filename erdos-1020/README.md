# Erdős #1020 — exact values of f(n;r,k) in the open middle window

**Problem.** Let f(n;r,k) be the maximum number of edges of an r-uniform
hypergraph on n vertices containing no k pairwise disjoint edges. The Erdős
matching conjecture (Erdős 1965; erdosproblems.com/1020) states

    f(n;r,k) = max( C(rk-1, r),  C(n,r) - C(n-k+1, r) )

realized by the clique on rk-1 vertices and by the family of all r-sets
meeting a fixed (k-1)-set ("cover family").

**SciNet:** problem d2ada81a-f94e-4ea5-a3dd-8b58a2a23712, investigation
aec4527d-0276-45b3-82ab-98aa3f965d75.

## Frontier before this work (re-verified 2026-07-27)

Beyond the ranges listed on erdosproblems.com/1020 (fetched 2026-07-27; page
last edited 2025-12-28) and in the SciNet problem background, the sharpest
results relevant to small parameters are:

- Frankl (JCTA 120 (2013) 1068–1072): the conjecture holds for all
  n ≥ (2s+1)r − s, where s = k−1 is the matching number. **This result is
  missing from the erdosproblems.com page**; it cuts the plausible r=4, k=3
  window from "13 ≤ n ≲ 69" down to 13 ≤ n ≤ 17.
- Frankl–Kupavskii (JCTB 157 (2022) 366–400): n ≥ (5/3 + o(1))rs, but only
  for s beyond an unspecified large s₀ — no effect at small s.
- Frankl–Lu–Ma–Wu (arXiv:2602.19230, Feb 2026): r=4, n ≥ 5s, but requires
  n ≥ n₀ = 10^(10^7) — no effect at realistic n. Their introduction confirms
  no s-specific or computational small-n results exist.
- arXiv:2605.26060 (May 2026): r=4 via finite-board reduction, but only for
  matching number s ≥ 6961.
- The claimed full proof arXiv:2602.01471 (Feb 2026) was withdrawn in June
  2026 (author-acknowledged error). The conjecture is open.
- Small-n side: trivial for n < rk; Kleitman 1968 for n = rk; Frankl (Israel
  J. Math 2017) for rk ≤ n ≤ k(r + 1/(2r^(2r+1))) — nothing new below the
  Frankl-2013 threshold for our parameters. Kolupaev–Kupavskii 2023 needs
  k > 101r³.
- arXiv:2607.07392 (Jul 2026): spectral-radius analogue of the conjecture
  for sufficiently large n — does not determine edge-count values f(n;r,k)
  at any finite n (re-checked 2026-07-27, after the initial survey).
- OEIS: no sequence records these values (searched 2026-07-27).

**Open windows attacked here** (each strictly between the solved small-n
and large-n regimes; every cell of every window is now certified):

| family | open window | Frankl-2013 threshold | status |
|---|---|---|---|
| r=4, k=3 (s=2) | 13 ≤ n ≤ 17 | n ≥ 18 | COMPLETE (5 cells) |
| r=5, k=3 (s=2) | 16 ≤ n ≤ 22 | n ≥ 23 | COMPLETE (7 cells) |
| r=4, k=4 (s=3) | 17 ≤ n ≤ 24 | n ≥ 25 | COMPLETE (8 cells) |
| r=4, k=5 (s=4) | 21 ≤ n ≤ 31 | n ≥ 32 | COMPLETE (11 cells) |
| r=6, k=3 (s=2) | 19 ≤ n ≤ 27 | n ≥ 28 | COMPLETE (9 cells) |

## Method (exact, certified)

1. **Shifted reduction (citation).** (i,j)-shifts preserve the edge count and
   never increase the matching number (Frankl, "The shifting technique in
   extremal set theory", 1987). Hence f(n;r,k) is attained by a *shifted*
   family — one that is down-closed in the coordinatewise domination order on
   sorted r-sets (B ≤ A iff b_t ≤ a_t for all t).

2. **Partition reduction (proved here, elementary).** For a down-closed
   family F: F contains k pairwise disjoint edges **iff** F contains k
   pairwise disjoint edges partitioning [rk]. *Proof.* Given disjoint
   A_1,…,A_k with union U, while some u ∈ U has u−1 ≥ 1 and u−1 ∉ U, replace
   u by u−1 inside its block: the blocks stay valid disjoint r-sets, stay in
   F by down-closure, and Σ U strictly decreases. At termination u−1 ∈ U for
   every u ∈ U with u > 1, and |U| = rk, so U = [rk]. ∎

3. **Integer program.** Binary x_A per r-subset A of [n]; maximize Σ x_A
   subject to (shift) x_A ≥ x_B whenever A is B with one element decremented,
   and (match) Σ_{B ∈ P} x_B ≤ k−1 for every partition P of [rk] into k
   r-blocks. By 1+2 the optimum equals f(n;r,k) exactly. The partition
   constraints are added in full when their number is ≤ 4·10⁵ (e.g. 5775 for
   r=4,k=3; 126126 for r=5,k=3), else generated lazily (separation on the
   incumbent, looped until a solve is optimal with zero violations; a cell is
   recorded `certified_optimal` only in that state).

3b. **Lazy separation, v2 (`code/emc_solve2.py`).** The v1 separation
   (lexicographic DFS, 200k violated partitions per round) stalls on
   r=4, k=5 (~2.55·10⁹ partitions of [20]): the cuts are near-duplicates
   sharing their first blocks, and enumeration-when-none-exist explodes.
   v2 fixes both: (i) 120k uniformly random partition constraints are
   injected up front (every partition constraint is valid a priori) —
   empirically this alone pins the relaxation optimum at the true value;
   (ii) per-round separation is a complete bitmask DFS with *support
   pruning* (a branch dies the moment some uncovered element of [rk] lies
   in no still-available block — pruning only provably-dead branches, so
   "no violated partition" conclusions stay exact) and min-support pivot
   branching, with shuffled adjacency for cut diversity; (iii) every round
   logs the proven relaxation optimum, a certified upper bound on f, so an
   interrupted run still yields a bound. Certification = CP-SAT OPTIMAL
   *and* the deterministic complete search finds no partition of [rk]
   inside the incumbent.

4. **Solvers.** Primary: OR-Tools CP-SAT 9.15.6755 (proven-optimal status,
   3 workers, seed 0). Independent cross-checks with HiGHS MIP
   (mip_rel_gap = mip_abs_gap = 0, model rebuilt from scratch):
   `code/emc_check_highs.py` (full partition set — all of r=4,k=3 at
   n=12..18, plus r=5,k=3 spot cells n=16,17) and `code/emc_check_highs2.py`
   (r=4,k=5 spot cells n=21,22, whose full partition set is too large:
   HiGHS proves the optimum of a relaxation built from an
   independently-seeded random partition sample; relaxation optimum == the
   directly-verified feasible family size pins f from both sides with a
   second solver; both cells AGREE). The analogous check for f(19;6,3) did
   not terminate within the compute budget (killed after ~17 CPU-min), so
   the r=6,k=3 upper bounds rest on CP-SAT proven optimality alone.
   Outputs in `results/highs_check_*.out`.

5. **Verification independent of the reduction.** `code/verify.py` re-checks
   every recorded family directly: validity, size, down-closure, and a proof
   that the raw edge list contains no k pairwise disjoint edges (no shifting
   assumption) — via an edge-by-edge-re-verified O(|F|) certificate when one
   applies (spanned vertices < rk, e.g. clique-type optima; or an explicit
   ≤(k−1)-vertex transversal, e.g. cover-type optima), else an exhaustive
   branch-and-prune search. This certifies the lower bound f ≥ |family|
   unconditionally; the matching upper bound rests on the two solver proofs
   of the exact model above.

## Results

See `results/results.jsonl` (one line per cell; `certified_optimal: true`
lines are claims — for a given (r,k,n) the LAST such line is the record) and
`results/sol_r*_k*_n*.json` (extremal families). Summary table in
`results/table.md`. **All 40 open cells across the five windows match the
conjectured value** — the conjecture survives exact computation everywhere
we could reach. In every open cell except one the cover family
C(n,r)−C(n−k+1,r) is optimal; the exception is **f(21;4,5) = 3876 =
C(19,4)**, where the clique on rk−1 = 19 vertices is still optimal one
vertex *above* the trivial range n ≤ rk — pinning the clique→cover
crossover for (r,k)=(4,5) between n=21 and n=22. The boundary cells n = rk
(Kleitman 1968) and n = (2s+1)r−s (Frankl 2013) reproduce the published
theorems, validating the pipeline.

Note: results.jsonl also retains four `certified_optimal: false` lines from
the v1 lexicographic separation's non-converging r=4,k=5 attempt (relaxation
upper bounds only, superseded by the certified v2 lines that follow them).

## Reproduce

    uv venv .venv --python 3.12 && uv pip install -p .venv/bin/python ortools highspy
    # v1 solver (small partition spaces, full/lazy-lex):
    .venv/bin/python code/emc_solve.py 4 3 12 13 14 15 16 17 18
    .venv/bin/python code/emc_solve.py 5 3 15 16 17 18 19 20 21 22 23
    .venv/bin/python code/emc_solve.py 4 4 16 17 18 19 20 21 22 23 24 25 --lazy
    # v2 solver (random-injection + pruned complete separation):
    .venv/bin/python code/emc_solve2.py 4 5 20 21 22 23 24 25 26 27 28 29 30 31
    .venv/bin/python code/emc_solve2.py 6 3 18 19 20 21 22 23 24 25 26 27
    # independent HiGHS cross-checks:
    .venv/bin/python code/emc_check_highs.py 4 3 12 13 14 15 16 17 18   # full model
    .venv/bin/python code/emc_check_highs.py 5 3 16 17                  # full model
    .venv/bin/python code/emc_check_highs2.py 4 5 21 22 --sample 120000 # sampled relaxation
    ./verify.sh          # ≤5 min spot-check, exit 0 iff all recorded cells verify

## Credit

Problem: P. Erdős (1965), curated by T. F. Bloom at erdosproblems.com/1020.
Key prior results relied on: Frankl 2013 (frontier delimitation), Frankl 1987
(shifting lemma; the WLOG at the heart of the model), Kleitman 1968 and
Frankl 2013 again (validation cells). Solvers: Google OR-Tools CP-SAT; HiGHS.
