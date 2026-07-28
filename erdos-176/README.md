# Erdős #176 — exact values of N(k,l): extending the table beyond l = 2

**Problem** (Erdős; erdosproblems.com/176). Let N(k,l) be the least N such that
every f : {1..N} → {−1,+1} admits a k-term arithmetic progression P with
|Σ_{n∈P} f(n)| ≥ l. Erdős asked for good upper bounds (e.g. is N(k,2) ≤ C^k?).
At l = k this is the van der Waerden number W(k); Spencer (1973) solved l = 1
exactly. SciNet problem 69b8d1b6-8951-491c-a749-0141943b8404,
investigation 42a037d4-1921-40d6-aedd-07f5211abf5b.

## Frontier before this work (re-verified 2026-07-27)

The SciNet triage snapshot (2026-07-13, "N(k,l) untabulated for l ≥ 2") was
**stale**. The erdosproblems.com/176 comment section holds substantial 2026
progress that the site's remarks have not yet incorporated:

- **Parity collapse** (S. Adenwalla, comment 2026-03-19): every k-AP sum has the
  parity of k, so N(k,l+1) = N(k,l) whenever k ≢ l (mod 2). In particular
  N(k,2) = N(k,1) (Spencer's formula) for even k.
- **First exact values at l = 2** (M. J. Goss Jr. / "quantiterate", comment
  2026-06-19, Zenodo doi:10.5281/zenodo.20763838): N(3,2)=9, N(5,2)=22,
  N(7,2)=49, N(9,2)=65, N(11,2)=112 (odd k only; even k is Spencer).
- **Polynomial upper bounds** (K. Kitamura comments, June 2026, Lean-checked,
  screened by N. Sothanaphan; building on a Z. Hunter et al. argument):
  N(k,2) = O(k³) for k ≥ 5 and N(k,√k) = O(k⁵) — which would answer two of the
  three displayed C^k questions affirmatively. Hunter et al.'s note
  N(k,c√k) = O(k³) was announced as forthcoming. The N(k,ck) question remains
  open (Erdős's lower bound N(k,ck) > (1+α_c)^k rules out polynomial there).

So "first N(k,2) table" was scooped in June 2026. **What remained untouched:
every l ≥ 3 column, and k ≥ 13 at l = 2.** Neither OEIS (no sequence contains
9,22,49,65,112) nor the Zenodo paper nor the comments hold any l ≥ 3 value.

## This work

SAT-based exact computation of the first N(k,l) values with l ≥ 3 beyond the
trivial collapses, plus an extension of the l = 2 row. Encoding: variable per
position (true = +1); for each k-AP, the constraint |sum| ≤ l−1 becomes a
T-window L ≤ #(+1) ≤ U with L = ⌈(k−l+1)/2⌉, U = ⌊(k+l−1)/2⌋, encoded as two
sequential-counter cardinality constraints (Sinz 2005 via PySAT CardEnc).
Solver: kissat --seed=42. For each cell, ramp-then-bisect on N; monotonicity in
N makes the crossover well-defined.

**Certification** (per cell, matching the problem's ADVANCES criteria):
- (a) an explicit ±1 sequence of length N(k,l)−1 with every k-AP |sum| ≤ l−1,
  re-checked by an independent checker (`code/check_witness.py`, shares no code
  with the encoder) — `witnesses/`;
- (b) a DRAT unsatisfiability proof at length N(k,l), emitted by kissat and
  verified by drat-trim (`s VERIFIED`) — `certs/` (proofs gzipped, CNFs kept;
  CNFs regenerate byte-identically from `code/encode.py`).

### Encoder validation

- Exhaustive semantic test: for (N,k) ∈ {(8,3),(9,4),(10,5),(9,6)} and all l,
  CNF satisfiability under all 2^N forced colourings matches a direct
  |sum| check (`code/selftest.py`, 0 failures).
- Crossover agreement with brute-force DFS on 8 small cells, and with all
  published anchors: N(3,2)=9, N(4,2)=13, N(5,2)=22, N(6,2)=11 (Spencer),
  N(3,3)=W(3)=9, N(4,3)=N(4,4)=W(4)=35 (parity collapse reproduced
  computationally), N(5,3)=N(5,2)=22.

### Results

Every **certified** cell below has both artifacts on disk: (a) a witness at
N−1 in `witnesses/` passing the independent checker, and (b) a kissat DRAT
refutation at N in `certs/` with drat-trim `s VERIFIED` (proofs stored
gzipped). Exact solver invocations and timings: `results/log.jsonl`.

**New exact values — firsts (no l ≥ 3 value exists in OEIS, the Zenodo paper,
or the problem's comments):**

| cell | value | witness (N−1) | UNSAT + DRAT (N) | parity corollary (new) |
|---|---|---|---|---|
| N(6,4) | **42** | `witnesses/k6l4_N41.txt` | `certs/k6l4_N42.cnf` + `.drat.gz` | N(6,3) = 42 |
| N(8,4) | **66** | `witnesses/k8l4_N65.txt` | `certs/k8l4_N66.cnf` + `.drat.gz` | N(8,3) = 66 |

Parity corollaries use Adenwalla's collapse (k ≢ l mod 2 ⇒ N(k,l+1) = N(k,l)).

**Independent re-certifications** — same witness + DRAT pipeline, but the
values were already published, so they are **not** claimed as firsts (in
`results/table.md` these cells are bold too; only the two rows above are new):

| cell | value | prior source | artifacts |
|---|---|---|---|
| N(5,2) | 22 | Goss 2026 (Zenodo) | `witnesses/k5l2_N21.txt`, `certs/k5l2_N22.*` |
| N(11,2) | 112 | Goss 2026 (Zenodo) | `witnesses/k11l2_N111.txt`, `certs/k11l2_N112.*` |
| N(4,4) | 35 | = W(4) (van der Waerden) | `witnesses/k4l4_N34.txt`, `certs/k4l4_N35.*` |

Their parity corollaries N(5,3) = 22 and N(4,3) = 35 were likewise already
derivable from published values, hence also not firsts.

**Open cells — partial brackets** (lower bounds are new and witness-backed;
none of these cells is closed):

| cell | bracket | evidence |
|---|---|---|
| N(10,4) | 97 < N(10,4) ≤ 122 | witness `witnesses/k10l4_N97.txt`; kissat UNSAT at N=122 (1280 s, logged) — **no DRAT stored**, so the upper bound is solver-trusted, not certified; bisection returned UNKNOWN at N=109 |
| N(9,5) | N(9,5) ≥ 123 | witness `witnesses/k9l5_N122.txt` (SAT, 429 s); ramp UNKNOWN at N=153 |
| N(12,4) | N(12,4) ≥ 144 | witness `witnesses/k12l4_N143.txt`; ramp interrupted (next CNF `scratch/k12l4_N179.cnf` generated, never solved); no UNSAT attempted |
| N(13,2) | N(13,2) ≥ 153 | witness `witnesses/k13l2_N152.txt`; UNKNOWN at N=169 and N=191. Note: the last `log.jsonl` bracket event misrecords `[169, null]` — the N=169 call returned UNKNOWN, so the artifact-backed lower bound is 152, not 169 |

Full table with provenance per cell: `results/table.md`, `results/table.json`
(sources: spencer / parity / vdW / goss / **this-work**). Raw per-call log with
exact invocations and timings: `results/log.jsonl`.

## Reproduction

```
uv venv .venv && uv pip install --python .venv/bin/python python-sat
brew install kissat            # v4.0.3 used
git clone https://github.com/marijnheule/drat-trim tools-drat-trim && make -C tools-drat-trim
.venv/bin/python code/selftest.py                  # encoder validation
.venv/bin/python code/solve_cell.py <k> <l>        # one cell end-to-end
./verify.sh                                        # < 5 min re-verification
```

## Credit

- Problem: P. Erdős (many sources, [Er65b] … [ErGr80]); curated by T. F. Bloom,
  erdosproblems.com/176.
- Parity collapse used to halve the table: S. Adenwalla (site comment).
- Prior l = 2 values (k ≤ 11) that this work extends: M. J. Goss Jr.,
  doi:10.5281/zenodo.20763838.
- Polynomial upper bounds context: Z. Hunter, K. Kitamura, N. Sothanaphan
  (site comments; Lean repos github.com/KitaKen1/erdos176-*).
- Tools: kissat & drat-trim (A. Biere; M. Heule), PySAT, Spencer [Sp73],
  known W(k) values (vdW numbers literature).
