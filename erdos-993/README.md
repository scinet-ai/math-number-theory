# Erdős #993: exhaustive unimodality verification for all trees on 30 vertices

**Problem.** Alavi, Malde, Schwenk, and Erdős (1987) conjectured that for every
tree (and forest) `T` the independent-set counting sequence
`i_0(T), i_1(T), i_2(T), ...` is unimodal — it never strictly dips and then
strictly rises. The conjecture is open; a single counterexample tree would
disprove it. Listed as [Erdős Problem #993](https://www.erdosproblems.com/993).

**What this computation does.** Streams every unlabeled tree on 30 vertices
(14,830,871,802 trees, OEIS [A000055](https://oeis.org/A000055)(30)) out of
nauty's `gentreeg` enumerator and, inside the same process via gentreeg's
`OUTPROC` plugin hook, computes each tree's independence polynomial exactly in
64-bit integer arithmetic by the standard two-state dynamic program over the
rooted tree, then tests the coefficient sequence for unimodality and (as a
by-product) log-concavity.

**Result.** Every tree on 30 vertices has a unimodal independent-set sequence.
No counterexample to Erdős #993 among trees exists on 30 or fewer vertices —
and this workspace makes that claim self-contained: every order 1..30 was
swept here (1–11 additionally cross-checked tree-by-tree against a brute
force), 23,522,619,475 trees in total, with every per-order count matching
OEIS A000055 exactly (`results/all_orders_summary.txt`). On 26 vertices the
code finds precisely the two known non-log-concave trees (both unimodal),
reproducing the published record.

**By-product: exhaustive non-log-concavity census.** The only trees on at
most 30 vertices whose independence sequence is not log-concave are:

| order | non-log-concave trees |
|---|---|
| ≤ 25 | 0 |
| 26 | 2 (the known pair) |
| 27 | 0 |
| 28 | 19 |
| 29 | 7 |
| 30 | 121 |

All 149 are saved with parent arrays and full sequences in `results/` and
independently re-verified in exact Python big-integer arithmetic
(`recheck_nonlogconcave.py`); all 149 are unimodal. Notable: the 7 trees on
29 vertices are the smallest non-log-concave trees of odd order — the
PatternBoost search of Ramos–Sun (arXiv:2510.18826) reports never having
found an odd-order example. The exhaustive counts at orders 27–30 (and the
odd-order existence at 29) appear to be new; the order-≤29 part of the sweep
overlaps Reynolds' unimodality verification, whose preprint we could not
fully access to confirm whether it also tracked log-concavity.

## Frontier: before and after

| Verification | Trees covered | Source |
|---|---|---|
| order ≤ 20 | — | Yosef–Mizrachi–Kadrawi (arXiv:2101.06744) |
| order ≤ 25 | — | Radcliffe (cited in arXiv:2502.10654) |
| order ≤ 26 | 279,793,450 at order 26 | Kadrawi–Levit–Yosef–Mizrachi (arXiv:2305.01784), found the only 2 non-log-concave trees of order ≤ 26 |
| order ≤ 29 | 8,691,747,673 total | **B. Reynolds**, "Mean bounds, structural reductions, and exhaustive verification for tree independence polynomial unimodality", Zenodo v3, 2026-03-18, DOI [10.5281/zenodo.19100781](https://doi.org/10.5281/zenodo.19100781) — the previous record |
| **order ≤ 30** | **+14,830,871,802 at order 30 (this work); orders 1–29 independently re-swept here as well (23,522,619,475 trees total)** | this repository |

Related context: log-concavity (a strengthening of unimodality) is known to
fail for trees — Kadrawi–Levit–Yosef–Mizrachi found the first two examples on
26 vertices, Galvin (arXiv:2502.10654) built infinite families, and Ramos–Sun
(arXiv:2510.18826) generated tens of thousands more on 27–101 vertices via
PatternBoost. Every known non-log-concave tree is still unimodal; this sweep
confirms that pattern exhaustively through order 30.

## Why the arithmetic is exact

Every coefficient counts independent sets of one size in a subtree on at most
30 vertices, so it is bounded by C(30,15) = 155,117,520 < 2^28. Convolution
accumulators are partial sums of such counts (same bound); the log-concavity
test multiplies two coefficients (< 2^56). Everything fits in `uint64_t` with
enormous margin; a runtime guard aborts if any coefficient exceeds 2^40.

## Correctness evidence

1. **Brute-force cross-check** (`brute_force_crosscheck.py`): an independent
   Python implementation enumerates all 2^n vertex subsets per tree and
   recounts by size. All 436 trees on ≤ 11 vertices match the DP output
   exactly, sequence by sequence (`results/crosscheck_n1_11.txt`).
2. **Reproduction of the published record**: the full order-26 sweep yields
   279,793,450 trees (= A000055(26)), 0 non-unimodal, and exactly 2
   non-log-concave trees — the trees `T_{3,4,4}` and `T*_{3,3,4}` of
   arXiv:2305.01784, with the tail dip 48² = 2304 < 2372·1
   (`results/order26_summary.txt`, `results/order26_exceptions.txt`).
3. **Coverage certificate**: gentreeg's `res/mod` splitting is a true
   partition (verified explicitly at order 20: 8 chunk counts and hashes sum
   to the full-run count and hash). The order-30 sweep runs 240 disjoint
   chunks; the summed tree count must equal A000055(30) = 14,830,871,802
   exactly, and does (`aggregate_order30.py`).
4. **Topological-order assertion**: the DP relies on gentreeg's documented
   invariant `par[j] < j`; the checker asserts it on every vertex of every
   tree and aborts on violation. The overflow guard is likewise always on.

## Reproducing

```bash
# build (nauty 2.8.9 source is bundled; see nauty.tar.gz)
cd nauty2_8_9 && ./configure && make gtools.o && cd ..
gcc -O3 -march=native -include plugin_decl.h \
    -DOUTPROC=check_tree -DSUMMARY=check_summary \
    -o gentreeg_independence nauty2_8_9/gentreeg.c independence_check_plugin.c \
    nauty2_8_9/gtools.o

# full order-30 sweep, 4 workers, checkpointed into logs/ (about 50 min on an M4 Max)
for w in 0 1 2 3; do ./run_order30_worker.sh $w 4 & done; wait
python3 aggregate_order30.py       # certifies count == A000055(30)

# quick spot-verification (a few minutes)
./verify.sh
```

`verify.sh` rebuilds from source, re-runs the brute-force cross-check, fully
reproduces the order-26 published record, re-runs one banked order-30 chunk
bit-for-bit, and re-aggregates the banked chunk logs.

## Credits and sources

- Problem: Y. Alavi, P. J. Malde, A. J. Schwenk, P. Erdős, *The vertex
  independence sequence of a graph is not constrained*, Congr. Numer. 58
  (1987) 15–23. Catalogued by T. F. Bloom as
  [Erdős Problem #993](https://www.erdosproblems.com/993).
- Previous verification record (order ≤ 29): B. Reynolds, Zenodo,
  DOI [10.5281/zenodo.19100781](https://doi.org/10.5281/zenodo.19100781)
  (v3, 2026-03-18), cited by Hibi–Kara–Vien (arXiv:2604.18824).
- Order-26 exhaustive computation and the two non-log-concave trees:
  O. Kadrawi, V. E. Levit, R. Yosef, M. Mizrachi (arXiv:2305.01784).
- Non-log-concave tree families: D. Galvin et al. (arXiv:2502.10654);
  Ramos–Sun PatternBoost search (arXiv:2510.18826).
- Tree enumeration: `gentreeg` from **nauty 2.8.9** by Brendan McKay and
  Adolfo Piperno (with gentreeg by Gang Li & Frank Ruskey's algorithm
  lineage), https://pallini.di.uniroma1.it/. The checker runs inside
  gentreeg's documented `OUTPROC` plugin hook.
- Tree counts: OEIS [A000055](https://oeis.org/A000055) (b-file).

## Headline numbers (order 30)

```
chunks:          240/240
trees checked:   14,830,871,802   (== OEIS A000055(30), exact)
non-unimodal:    0
non-log-concave: 121              (all still unimodal; all saved with sequences)
sequence hash:   c20d7f070e7da7d1
```

The 149 non-log-concave trees on ≤ 30 vertices all fail log-concavity at the
penultimate coefficient (e.g. the first found at order 30: tail
`..., 4101, 62, 1` with 62² = 3844 < 4101·1), the same failure mode as the
two known order-26 trees.

## What this does NOT cover

Forests. The conjecture is stated for trees and forests; a forest's
independence polynomial is the product of its components' polynomials, and
unimodality is not automatically preserved under products (log-concavity is,
but trees are not all log-concave). No exhaustive forest verification bound
appears in the literature either; extending this pipeline to forests
(multisets of trees) is the natural next step.

## Machine and runtime

Apple M4 Max (macOS), at most 4 concurrent worker processes, Apple clang
-O3 -march=native, nauty 2.8.9. Order-30 sweep: 12,847 CPU-seconds of
checking, 70 minutes wall for all 240 chunks (including one
checkpoint-resume). Orders 27–29 re-sweep: 6,605 CPU-seconds, 37 minutes wall. Orders 12–26: under 5 minutes single-core. Exact integer
arithmetic throughout; no floating point in any counted quantity.
