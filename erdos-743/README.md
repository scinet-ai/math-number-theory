# Erdős problem #743 — tree packing conjecture, exhaustively verified for n = 10

**Result: for every one of the 45,376,056 families of trees (T_2, ..., T_10) with
|T_k| = k, the complete graph K_10 decomposes into an edge-disjoint union of the
T_k. Combined with the calibration sweeps below (n ≤ 9 re-verified from scratch),
the Gyárfás–Lehel tree packing conjecture holds for all n ≤ 10.**

This extends the exhaustive-verification record for this conjecture, which had
stood at n ≤ 9 since Fishburn (1983).

## The problem

The tree packing conjecture (Gyárfás, 1970s; recorded by Erdős, and listed as
open at [erdosproblems.com/743](https://www.erdosproblems.com/743)): given any
trees T_2, ..., T_n where T_k has exactly k vertices, K_n can always be written
as the edge-disjoint union of the T_k. The edge counts match exactly
(sum of (k-1) for k = 2..n equals C(n,2)), so any packing is a decomposition.
A single non-packing family for one specific n would disprove the conjecture.

Frontier before this work (per erdosproblems.com/743, re-checked 2026-07-27):

- Gyárfás and Lehel (1978): true when all but at most 2 trees are stars, and
  when every tree is a star or a path.
- **Fishburn (1983): exhaustive verification for all n ≤ 9** — the record this
  work extends.
- Bollobás (1983): the smallest floor(n/sqrt(2)) trees always pack greedily.
- Joos, Kim, Kühn, Osthus (2019): true for trees of bounded maximum degree.
- Allen, Böttcher, Clemens, Hladký, Piguet, Taraz (2021): true when all trees
  have maximum degree at most c·n/log n.
- Janzer and Montgomery (2024): the largest c·n trees can always be packed.
- A 2024 preprint (Chalise, Clark, Gnang, arXiv:2410.13840) claims a full
  proof; as of 2026-07-27 it is unpublished, and erdosproblems.com/743 still
  lists the conjecture as open with zero claimed proofs. This work does not
  rely on it in any way.

Frontier after this work: **exhaustive verification through n = 10**
(45,376,056 families, every one packed, with machine-checkable witnesses).

## Why the family count is 45,376,056

The number of unlabeled trees on k vertices for k = 2..10 is
1, 1, 2, 3, 6, 11, 23, 47, 106 ([OEIS A000055](https://oeis.org/A000055)).
A family chooses one tree of each size, so there are
1·1·2·3·6·11·23·47·106 = 45,376,056 families. (For n = 9 the same product
stops at 47 and gives 428,076 — the size of Fishburn's sweep.)

## Method

1. **Tree enumeration with a completeness certificate** (`generate_trees.py`).
   Trees come from networkx's `nonisomorphic_trees` (WROM algorithm). Two
   independent checks certify the lists: (a) the count for every k equals the
   OEIS A000055 value; (b) an independently implemented AHU canonical form
   (rooted at tree centers) is pairwise distinct across each list. Distinct
   canonical forms + correct total count = the list is exactly one
   representative per isomorphism class.

2. **Exact symmetry reduction** (`packer.c`). T_n has n vertices, so any
   embedded copy of it is a spanning tree of K_n. Any isomorphism between two
   spanning copies is a bijection of all n vertices, i.e. an automorphism of
   K_n carrying one copy to the other — so Aut(K_n) = S_n acts transitively on
   the copies of T_n, and WLOG T_n is embedded by the identity map. A family
   packs K_n iff T_{n-1}, ..., T_2 pack K_n minus this canonical copy. This is
   exact (no lost cases) and removes a factor of up to n!/|Aut(T_n)| work.

3. **Sweep** (`packer.c`, one process per "chunk" = one choice of T_10).
   Families are enumerated in lexicographic index order. Fast path: greedy
   first-fit — place trees in decreasing size, taking the first embedding in a
   fixed deterministic order, sharing work across families with a common
   prefix of large trees. If greedy dies, an independent complete backtracking
   search over all embeddings of T_9, ..., T_2 (largest first, deterministic
   order, node cap 10^9) re-solves that family from scratch.

4. **Stragglers** (`resolve_hard.py`). The 27 families (of 45.4M) that hit the
   node cap were each solved by OR-Tools CP-SAT with an exact model (one
   injective vertex map per tree + exactly-one covering constraints per edge).
   All 27 are SAT; their packing witnesses are stored and validated. CP-SAT's
   answers are not trusted: only its *witnesses* are used, and each is checked
   independently (below).

5. **Independent witness validation** (`check_witnesses.py`, networkx — a
   fully separate code path from the C solver). A witness assigns every edge
   of K_10 a tree size; the checker verifies the labels partition all 45 edges
   and that each size class is a tree isomorphic to the family's chosen T_k.

## Soundness argument (what you must trust, and what you need not)

The claim "every family packs" is a purely *positive* claim: a packing was
constructed for every single family (greedy, backtracking, or CP-SAT). So the
completeness of the searches, the node cap, and CP-SAT's solver logic are all
irrelevant to soundness — they only affected speed. What soundness rests on:

- the family enumeration covers everything: certified by the A000055 counts +
  AHU distinctness, and by every chunk's family counter equaling the expected
  product (checked in-program; `complete yes` in every chunk file);
- the symmetry reduction (three-line proof above);
- witness validity: constructed embeddings are edge-disjoint by construction
  in the C solver, and independently re-validated on 31,796 sampled witnesses,
  all 27 CP-SAT witnesses, and a full-chunk archive (below) — zero failures.

## Results

| sweep | families | greedy | backtracking | CP-SAT | non-packing |
|---|---|---|---|---|---|
| n = 8 (smoke) | 9,108 | 9,072 | 36 | 0 | **0** |
| n = 9 (= Fishburn 1983) | 428,076 | 421,520 | 6,556 | 0 | **0** |
| **n = 10 (new)** | **45,376,056** | 43,792,160 | 1,583,869 | 27 | **0** |

- Full n = 10 sweep: 106 chunks, ~4 minutes wall clock on 4 worker processes
  (Apple Silicon, arm64-darwin, clang -O2); CP-SAT stragglers: under 5 minutes.
- Greedy first-fit alone settles 96.5% of families; a plain backtracking
  search settles all but 27 of the rest; no family required more than CP-SAT.
- Determinism: no randomness anywhere in the C sweep; re-running any chunk
  reproduces its result file byte-for-byte, including a running FNV-1a hash
  over all 45,376,056 witness label strings.

## Files

- `generate_trees.py` — tree lists + completeness certificates (`trees/`).
- `packer.c` — the sweep. Build: `clang -O2 -o packer packer.c`.
  Run one chunk: `./packer n top_index trees out_dir sample_stride node_cap`.
- `run_sweep.sh` — full sweep, resumable (skips finished chunks).
  Invocation used: `./run_sweep.sh 10 4 50000 1000000000` (and `9`, `8`).
- `resolve_hard.py` — CP-SAT for node-cap stragglers.
  Invocation used: `uv run --with ortools python resolve_hard.py 10 results/n10 trees 600`.
- `check_witnesses.py` — independent witness validator (networkx).
- `results/n10/chunk_III.txt` — per-chunk: expected vs actual family count,
  per-outcome counts, witness hash, and every family that needed more than
  greedy (with its resolution).
- `results/n10/sample_III.txt` — full witnesses: every 50,000th family plus
  every family that needed backtracking. Witness format: family index, result
  code, tree indices (sizes 9..2; the T_10 index is the chunk number), then 45
  hex digits — digit at position e is the size of the tree using edge e of
  K_10 (edges in lexicographic order (0,1),(0,2),...,(8,9); 10 prints as `a`).
- `results/n10/hard/` — the 27 CP-SAT witnesses (same format).
- `results/n10/full_witnesses/` — complete witness archive for chunk 042 (all
  428,076 families, regenerated with `sample_stride 1`; its witness hash
  matches the banked chunk 042 exactly). Any chunk's complete witness archive
  regenerates deterministically the same way in seconds.
- `results/n9/`, `results/n8/` — the calibration sweeps.
- `verify.sh` — spot verification in ~1 minute: regenerates the tree lists
  (byte-identical), rebuilds the solver, re-runs n=10 chunks 003 and 042 and
  an n=9 chunk (byte-identical including hashes), re-validates witness slices
  and all 27 straggler witnesses, and reconciles totals. Exits nonzero on any
  mismatch.

## Environment

macOS 26.5.1 (arm64, Apple Silicon), Apple clang 21.0.0, Python 3.12.13 via
uv, networkx 3.6.1, OR-Tools 9.15.6755. At most 4 concurrent processes; the C
sweep is exact integer/bitmask arithmetic throughout (no floating point).

## Credit

The conjecture is due to A. Gyárfás; the n ≤ 9 record this extends is
P. C. Fishburn, "Packing graphs with odd and even trees", *Journal of Graph
Theory* 7 (1983) 369–383. Problem catalogued by Thomas Bloom at
[erdosproblems.com/743](https://www.erdosproblems.com/743) (with the partial
results of Gyárfás–Lehel 1978, Bollobás 1983, Joos–Kim–Kühn–Osthus 2019,
Allen–Böttcher–Clemens–Hladký–Piguet–Taraz 2021, Janzer–Montgomery 2024 cited
there). Tree counts: [OEIS A000055](https://oeis.org/A000055). Tooling:
networkx (tree generation and independent validation), Google OR-Tools CP-SAT
(straggler resolution).
