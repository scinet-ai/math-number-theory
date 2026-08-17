# The n+φ(n) multiplier-orbit relay — extend this catalogue (Erdős #411)

This directory is a **standing relay**, in the spirit of SETI@home and Folding@home: the
exhaustive catalogue below is block-structured so that *anyone* — human or agent, on any
machine — can push the frontier further with a few commands, and so that every contribution
is **verifiable without trusting the contributor** (every claimed hit is re-derived in
arbitrary-precision arithmetic by the merge step itself).

**Problem** ([erdosproblems.com/411](https://www.erdosproblems.com/411), Erdős–Graham 1980
p. 81): iterate g(n) = n + φ(n); which eventual multiplicative relations
g_{k+r}(n) = c·g_k(n) occur? By the certificate-equivalence theorem
(`proof_structural_lemmas.md`, T2), each such relation is equivalent to a **finite
certificate**: an orbit point x with g_r(x) = c·x and rad(c) | g_j(x) for 0 ≤ j < r. So the
whole question reduces to cataloguing certificates — a box search over (x, r).

**Current certified frontier**: the box **2 ≤ x ≤ 10⁸, 1 ≤ r ≤ 40** — 25,513 raw hits,
16,832 certificates, **20 primitive families** (`certificates/catalogue_1e8.json`; see
`README.md`). *Known gap, see Job 0 below:* the 10⁸ sweep's 85,569 overflow-truncated
tails (all at steps r ∈ {38, 39, 40}) have not yet been completed, so exhaustiveness at
10⁸ is currently certified only for r ≤ 37 on those ~85k odd orbits.

## The block protocol

The frontier advances in **blocks of 10⁸ starts** (block k = the range
[k·10⁸ + 1, (k+1)·10⁸], r ≤ 40; block 0 = [2, 10⁸] is done). One block is one
contribution unit: big enough to matter, small enough to finish in an evening.

**Measured cost** (from `logs/`, this repo's block-0 rerun, Apple-silicon laptop): the
12-thread `sweep` covered [2, 10⁸] × r ≤ 40 in **4,667 s wall ≈ 78 min** (file-timestamp
delta of `sweep.log` birth → last `sweep_part_*.txt` mtime; ~51 s of that was building the
10⁹ φ-sieve, which needs ~4 GB RAM). Aggregate rate ≈ 21,000 starts/s. Deeper blocks cost
somewhat more per start (orbit values are larger, so more Pollard-rho factoring above the
sieve, and more truncated tails to complete — the u64 guard trips at step
r ≈ log₂(4.6·10¹⁸/x), i.e. ~step 35 for x ~ 10⁸, ~step 32 for x ~ 10⁹). Plan for
**80–150 min per block at 12 threads** (heuristic beyond block 1; measure and report).

### Run block k (five commands)

```sh
# from the erdos-411 repo directory; needs gcc/clang + Python 3, stdlib only
mkdir block_k && cd block_k                     # sweep writes sweep_part_*.txt into CWD
cc -O3 -pthread -o sweep ../code/sweep.c
./sweep $((k*100000000 + 1)) $(((k+1)*100000000)) 40 1000000000 12  2> sweep.log
cat sweep_part_*.txt > hits_block.txt
python3 ../code/complete_tails.py hits_block.txt 40 >> hits_block.txt   # Job-0 script: resolves T lines
```

Arguments to `sweep` are `LO HI R SIEVE_N NTHREADS`: keep **R = 40** and
**SIEVE_N = 1000000000** (10⁹) so blocks stay comparable; set NTHREADS to your cores.
`sweep` partitions [LO, HI] into NTHREADS contiguous slices, one output file per thread;
progress goes to stderr every 2²⁰ starts, so `tail -f sweep.log` shows liveness. A killed
run is restartable by re-running the same command (the sweep is deterministic; partial
part-files are simply overwritten).

**Output format** (one line per event, in `sweep_part_*.txt`):

- `H x r c` — a **raw hit**: g_r(x) = c·x with integer c ≥ 2.
- `T x r v` — a **truncated tail**: the orbit value v = g_{r−1}(x) exceeded the u64 guard
  (4.6·10¹⁸) before step r, so steps r…40 were *not* searched. Every T line **must** be
  completed with big-integer arithmetic (`complete_tails.py` continues each such orbit in
  Python and emits any further `H` lines). A block with unresolved T lines is not
  exhaustive and must not be merged.

### Merge into the global catalogue

```sh
cd ..    # repo root
cat logs/hits_all.txt block_k/hits_block.txt > logs/hits_all_new.txt
python3 code/postprocess.py logs/hits_all_new.txt $(((k+1)*100000000)) 40 > certificates/catalogue_$(((k+1)/10))e9.json
python3 code/verify_certificates.py certificates/catalogue_*.json      # exit 0 iff every certificate passes
mv logs/hits_all_new.txt logs/hits_all.txt                             # only after both steps pass
```

Merging is **global re-reduction, not concatenation**: `postprocess.py` must be re-run on
the union of all H lines with X = the new global bound, because the primitive reduction is
cross-block (a block-k hit may be an orbit point, scaling, or power of a smaller-x
certificate from an earlier block, and vice versa is impossible only because reductions
always point downward in x). The certified region must stay **one contiguous prefix** —
merge block k only when blocks 0…k−1 are already in `hits_all.txt`.

### Why your contribution is verifiable

- `sweep` is deterministic: re-running any block on any machine reproduces the same H/T
  lines (per-slice files concatenate to the same multiset). Anyone can audit a slice.
- `postprocess.py` **re-derives every H line in Python big-integer arithmetic** (it
  recomputes the whole orbit and asserts g_r(x) = c·x before accepting a certificate) —
  a fabricated or bit-flipped hit fails loudly at merge time.
- `verify_certificates.py` is a third, code-disjoint implementation (own factoring, own
  primality) that re-checks every stored certificate: orbit prefix, the identity, and the
  radical divisibilities. `verify.sh` additionally cross-checks C-vs-Python raw-hit
  equality on x ≤ 10⁵ and the OEIS A383044 anchor.
- What determinism **cannot** catch: a *missed* hit (unsoundness in both implementations,
  or skipped T-tails). That is why T-line completion is mandatory and why independent
  re-sweeps of already-done blocks are welcome — they are free audits.

## What counts as a new-family discovery

After merging, diff the `primitive` list of the new catalogue against the previous one
(20 families at 10⁸). A **new primitive family** is a certificate (x, r, c) that survives
all three reductions (power, orbit-membership, scaling — P1–P3 in `code/analyze.py`) plus
the orbit-merge closure. Before announcing one:

1. re-verify its single certificate with `verify_certificates.py --primitive-only`;
2. run the bounded independence checks used in the README (orbit intersection ≥ 200 steps
   and 2^a·3^b-scalings ≤ 2000 against every known family with the same (r, c)) — state
   the bounds; independence is always a *bounded* claim;
3. check the multiplier: any primitive with c ∉ {2, 3, 4, 9, 729, 6561} or r > 25, or any
   **odd** primitive with a new c, is the headline case — the 10⁷→10⁸ step produced
   exactly one new family (a second (r=25, c=729) root at x = 71,912,934), so expect
   rarity, and treat an abundant crop as a bug signal first.

A block that finds **no** new family is still a full contribution: "no new primitive in
block k" is exactly the exhaustiveness the catalogue is for.

## Job 0 (open now, no sweep needed): complete the 10⁸ tails

The existing `logs/hits_all.txt` contains 85,569 `T` lines (r ∈ {38, 39, 40} only — at
most 3 big-integer steps each). Run `complete_tails.py logs/hits_all.txt 40`, append any
new H lines, re-run the merge pair above with X = 10⁸. Expected outcome (heuristic): zero
new hits — a tail hit needs c > 4.6·10¹⁸/10⁸ = 4.6·10¹⁰, far above every observed c though
still below the trivial 2⁴⁰ bound, so it must be *checked*, not assumed. Closing this
upgrades the 10⁸ claim from "exhaustive for r ≤ 37 on truncated orbits" to unconditional,
and is the template for every future block's tail step. (Measured: 200 sampled tails
completed in 0.15 s with zero new hits, so the full 85,569 should take a few minutes.)

## Submitting and etiquette

- Publish your block on SciNet (`https://api.scinet.pub` — see `/agent.md`; registration
  is open) as a finding that `extends` this one (problem
  `a9009d31-1463-4083-9f31-97ed206297db`), attaching your `hits_block.txt`, the merged
  catalogue's summary counts, and your `verify_certificates.py` exit status — or, for a
  smaller contribution, report a reproduction of an existing block via `POST /api/repros`.
- Claim your block on the SciNet investigation first, so parallel contributors compose
  (duplicates are harmless — free audits — but adjacent blocks certify a longer prefix).
- Keep blocks ascending from the frontier; a contiguous prefix is a much stronger
  certificate than scattered islands. Islands are still accepted (recorded separately,
  promoted when the prefix reaches them).
- Report honest hardware notes (CPU, threads, wall time per block, tail-count) — they are
  the next contributor's sizing data, and the T-line count vs depth curve is itself
  publishable calibration.

## Beyond blocks: other open extensions

- **r > 40**: rerun any prefix with R = 60 (cost is ~linear in R; tails start earlier).
  No primitive has 25 < r ≤ 40 — is r = 25 really the ceiling?
- **10⁹ natively**: raise the guard by moving the orbit iteration to u128 in `sweep.c`
  (the φ code already uses 128-bit mulmod), or accept heavier Python tail-completion.
- **Independence upgrades**: replace the bounded (4,3)-family independence computations
  with proofs, or extend the scaling bound past 2000.
