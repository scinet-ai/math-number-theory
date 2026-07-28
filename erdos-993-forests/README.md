# Erdős #993, round 2: the forest case — first exhaustive verification (all forests on ≤ 30 vertices) plus a closure theorem for every forest with components ≤ 30

**Problem.** Alavi, Malde, Schwenk, and Erdős (1987) conjectured that the
independent-set counting sequence `i_0, i_1, i_2, ...` of every **tree or
forest** is unimodal ([Erdős Problem #993](https://www.erdosproblems.com/993),
status: open/falsifiable). Round 1 of this project (SciNet finding
`b1eaa502-a0b8-4181-a285-2e7fa9cee15d`, workspace `../erdos-993/`) exhausted
the **tree** half through order 30: all 23,522,619,475 trees on ≤ 30 vertices
are unimodal, and exactly **149** of them fail log-concavity (2 of order 26 —
the known Kadrawi–Levit–Yosef–Mizrachi pair — plus 19 of order 28, 7 of order
29, 121 of order 30).

This round attacks the **forest** half. A forest's independence polynomial is
the product of its components' polynomials, and unimodality is **not**
preserved by products in general, so the tree result does not imply the forest
result. Before this computation the literature contained **no exhaustive
forest verification bound at all** (frontier check 2026-07-27: erdosproblems.com
records none; Reynolds' Zenodo record is trees ≤ 29 only; the only forest-side
work is W. Blair's 2026-06-05 comment on the erdosproblems.com forum — 253,695
*targeted* products built from a non-exhaustive parametric family of
non-log-concave trees).

## Results

**1. Direct exhaustive verification (assumption-free).** Every one of the
**52,068,524,664 forests on at most 30 vertices** has a unimodal
independent-set sequence. (23,522,619,475 are the round-1 trees; the
28,545,905,189 disconnected forests are new here, covered by 28,169,623,738
product checks after polynomial dedup.) This is the first exhaustive forest
bound; it matches the order-30 tree record, and no counterexample to
Erdős #993 exists on ≤ 30 vertices. Since a *disconnected* forest on 31
vertices has all components ≤ 30, the disconnected case of order 31 is also
covered by result 2 below.

**2. Closure theorem (conditional only on two classical theorems).**
*Every forest all of whose tree components have at most 30 vertices — of
arbitrarily many vertices — has a unimodal independent-set sequence. Hence
any counterexample to Erdős #993 must contain a tree component on ≥ 31
vertices.* The two classical ingredients:

- **[Hoggar 1974]** the product of log-concave positive-coefficient
  polynomials is log-concave;
- **[Keilson–Gerber 1971]** a nonnegative sequence with interval support is
  *strongly unimodal* (its convolution with every unimodal sequence is
  unimodal) **iff** it is log-concave.

Write a forest `F = L ⊔ M` where `L` collects the log-concave components and
`M` the non-log-concave ones. `poly(L)` is LC (Hoggar), so if `poly(M)` is
unimodal, `poly(F)` is unimodal (Keilson–Gerber). With components ≤ 30, the
components of `M` come from the 149; so the forest case reduces to: *is every
finite multiset product of the 149 unimodal?* Moreover a minimal non-unimodal
multiset `M` must have **every** proper nonempty sub-multiset non-log-concave
(split `M = A ⊔ B`; both sides unimodal by minimality; either side LC would
make `poly(M)` unimodal by K–G). This makes the risk set hereditary and the
search a closure computation (`lane_a_closure.py`, exact big-int arithmetic):

- level 2: all `C(150,2) = 11,175` pair products — **all unimodal**; exactly
  **97** are non-log-concave (`H_2`, total order 56–60,
  `results/lane_a_H2_members.txt`);
- level 3: all `10,823` extensions of `H_2` — **all unimodal**; the candidates
  in which every pair is non-LC number 111, and **every one of them is
  log-concave**, so `H_3 = ∅` and the closure **terminates**: no minimal
  non-unimodal multiset of any size exists.

The same argument shows Blair's product lanes (non-LC seed × paths, powers of
a single seed with LC cofactors, etc.) could never have contained a
counterexample — only multisets with ≥ 2 non-LC components are at risk, and
(for components ≤ 30) levels 2–3 close them all off.

**3. By-product: the complete census of non-log-concave forests on ≤ 30
vertices** (`results/nonlc_products_recheck.txt`). By Hoggar, a non-LC forest
must contain a non-LC tree component, so on ≤ 30 vertices the disconnected
ones are exactly the non-LC products `T × q` with `T` one of the 28 non-LC
trees of order ≤ 29. The sweep found each such product; every one is unimodal,
and the census is proved complete by a from-scratch recomputation.

## Method (Lane B, the direct sweep)

Every disconnected forest `F` on ≤ 30 vertices factors as `F = T ⊔ q` where
`T` is a maximum component of some order `k ≤ 29` and `q` is a forest on
`m = 1..30−k` vertices with components of order ≤ k. So:

1. **q-sets** (`build_qsets.py`, exact Python): for each `k`, the set of
   *distinct* independence polynomials of forests on `m ≤ 30−k` vertices with
   components ≤ k, built by a multiset-knapsack DP over the 13,188 tree
   polynomials of order ≤ 15 (dumped from gentreeg by the round-1-validated
   plugin, each re-verified by an independent Python DP). Totals per (cap, m)
   are certified against an independent Euler-transform computation from
   A000055 and, where the cap is not binding, against OEIS A005195. 716,895
   distinct q-polynomials across k = 1..29.
2. **Sweep** (`forest_check_plugin.c` inside gentreeg's OUTPROC hook): stream
   every tree of order k = 1..29 (round-1 tree DP, verbatim), convolve its
   polynomial with every q-set entry in uint64 arithmetic (max coefficient
   `C(30,15) < 2^28`; guard at `2^41`), and test unimodality (+
   log-concavity as a by-product). 186 chunked tasks (gentreeg res/mod
   partitions; ≤ ~60 s each), 3 workers, resumable; every chunk banks an
   order-independent FNV hash.
3. **Certification** (`aggregate_forest_sweep.py`): per order, summed tree
   counts must equal A000055(k) exactly and product checks must equal
   `A000055(k) × |q-set(k)|`; the (T, q)↔(F, max-component-type) bijection is
   the coverage argument, tested explicitly at TOTAL=12.

## Correctness evidence

1. **End-to-end brute force** (`test_small_end_to_end.py`): all 2,948 forests
   on ≤ 12 vertices enumerated explicitly; brute-force `2^n` subset counts ==
   product of component polynomials for every one; counts match A005195(1..12);
   and a full TOTAL=12 mini-sweep through the *actual C binary* is reproduced
   bit-for-bit (counts + FNV hashes) by an independent Python implementation.
2. **Round-1 pedigree**: the tree DP inside the sweep is the round-1 code,
   which was brute-force cross-checked on all 436 trees of order ≤ 11 and
   reproduces the published order-26 record (2 non-LC trees) and OEIS A000055
   counts for every order ≤ 30.
3. **Independent recomputation of every exceptional object**: the 149 non-LC
   trees (Lane A re-derives their sequences from parent arrays and matches
   round 1 byte-for-byte) and every non-LC product found by the sweep
   (`recheck_nonlc_products.py`, big-int Python sharing no code with the C
   checker; census completeness proved by from-scratch recomputation).
4. **Counting certificates at every layer**: q-set totals == Euler transform
   == A005195 (where applicable); per-order streamed trees == A000055;
   checks == trees × |q-set|; all banked in `results/`.
5. **Determinism**: single-threaded per chunk, integer-only arithmetic,
   fixed enumeration order; chunk hashes are order-independent FNV sums, so
   any re-run of any chunk must reproduce its banked line exactly (verify.sh
   re-runs two).

## Reproducing

```bash
# build (nauty 2.8.9 source bundled at ../erdos-993/nauty.tar.gz, configured copy here)
cd nauty2_8_9 && ./configure && make gtools.o && cd ..
gcc -O3 -march=native -include forest_plugin_decl.h \
    -DOUTPROC=forest_check_tree -DSUMMARY=forest_summary \
    -DPLUGIN_INIT='{ forest_init(); }' \
    -o gentreeg_forest nauty2_8_9/gentreeg.c forest_check_plugin.c nauty2_8_9/gtools.o

python3 lane_a_closure.py          # structural closure (< 1 s)
python3 build_qsets.py             # q-sets + counting certificates (~3 s)
python3 test_small_end_to_end.py   # end-to-end validation at TOTAL=12 (~2 s)
for w in 0 1 2; do ./run_forest_worker.sh $w & done; wait   # ~50 min, 3 cores
python3 aggregate_forest_sweep.py  # certification + summary
python3 recheck_nonlc_products.py  # by-product census recheck

./verify.sh                        # ~3-4 min spot-verification of everything
```

## Frontier: before and after

| Statement | Before (2026-07-27) | After |
|---|---|---|
| trees, exhaustive | ≤ 29 published (Reynolds, Zenodo, 2026-03); ≤ 30 (round 1, SciNet) | unchanged (round 1) |
| forests, exhaustive | **none** | **all forests on ≤ 30 vertices** (52,068,524,664) |
| forests, structural | non-unimodal ⇒ some component non-LC (Hoggar; Blair forum comment); 253,695 targeted products checked | **every forest with all components ≤ 30 is unimodal** (closure via Keilson–Gerber; any counterexample needs a tree component ≥ 31) |

## Credits and sources

- Problem: Y. Alavi, P. J. Malde, A. J. Schwenk, P. Erdős, *The vertex
  independence sequence of a graph is not constrained*, Congr. Numer. 58
  (1987) 15–23. Catalogued by T. F. Bloom as
  [Erdős Problem #993](https://www.erdosproblems.com/993).
- S. G. Hoggar, *Chromatic polynomials and logarithmic concavity*, J. Combin.
  Theory Ser. B 16 (1974) 248–254,
  [doi:10.1016/0095-8956(74)90071-9](https://doi.org/10.1016/0095-8956(74)90071-9).
- J. Keilson, H. Gerber, *Some results for discrete unimodality*, J. Amer.
  Statist. Assoc. 66 (1971) 386–389 (strong unimodality ⇔ log-concavity).
- W. Blair, comment on erdosproblems.com/993 (2026-06-05) and repository
  [willblair0708/verified-combinatorics](https://github.com/willblair0708/verified-combinatorics/tree/main/erdos-993):
  the Hoggar reduction for forests and the first targeted forest-product
  search; the closure theorem here strictly subsumes that search surface for
  components ≤ 30.
- Non-log-concave trees: O. Kadrawi, V. E. Levit, R. Yosef, M. Mizrachi
  ([arXiv:2305.01784](https://arxiv.org/abs/2305.01784), the order-26 pair);
  D. Galvin ([arXiv:2502.10654](https://arxiv.org/abs/2502.10654), infinite
  families); Ramos–Sun ([arXiv:2510.18826](https://arxiv.org/abs/2510.18826),
  PatternBoost, orders 27–101).
- Previous tree record: B. Reynolds, Zenodo v3 (2026-03-18),
  [doi:10.5281/zenodo.19100781](https://doi.org/10.5281/zenodo.19100781),
  trees ≤ 29; round 1 of this project extended to 30 and banked the complete
  149-tree non-LC census this round's Lane A consumes.
- Tree enumeration: `gentreeg` from **nauty 2.8.9** (B. McKay, A. Piperno,
  gentreeg by G. Li & F. Ruskey's algorithm lineage),
  https://pallini.di.uniroma1.it/, via its documented OUTPROC plugin hook.
- Counts: OEIS [A000055](https://oeis.org/A000055) (trees),
  [A005195](https://oeis.org/A005195) (forests), b-files fetched 2026-07-27.

## Machine and runtime

Apple M4 Max (macOS), ≤ 3 concurrent worker processes (shared machine),
Apple clang -O3 -march=native, nauty 2.8.9, Python 3 big-int for everything
exact-critical. Lane A: < 1 s. q-sets: ~3 s. Sweep: 186 chunks, ~50 min wall
on 3 workers (see `results/forest_sweep_summary.txt` for CPU totals). Exact
integer arithmetic throughout; no floating point in any counted quantity.

## What this does NOT cover

Trees (and hence forests with a component) on ≥ 31 vertices. The conjecture
remains open; these results say a counterexample, if one exists, must contain
a tree component on at least 31 vertices, and for single trees order ≥ 31.
