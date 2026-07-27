# First computed thresholds for the finite version of Owings' problem (Erdős #1199)

## The problem

Owings [Ow74] asked, and Erdős recorded [Er80, p.104]: is it true that in any
2-colouring of the natural numbers there is an infinite set A such that all
elements of A+A are the same colour?  Here A+A = {a + a' : a, a' in A}
*includes the doubled elements* 2a.  Hindman [Hi79] showed the analogue for
3 colours is false; two colours is open.  Listed as open at
https://www.erdosproblems.com/1199 (re-checked 2026-07-27: status OPEN, no
partial solutions claimed, no computational results in the comments).

If the conjecture is true, compactness gives finite thresholds

    n(k) = the least n such that EVERY 2-colouring of {1,...,n} contains a
           k-element set A with A+A monochromatic,

where A+A must lie inside {1,...,n} for its colours to be defined
(equivalently, A is a k-subset of {1,...,floor(n/2)}).  No values of n(k)
appear to have been published anywhere; the erdosproblems.com page, its
forum thread, OEIS, and the recent literature (see "Relation to prior work")
have no finite thresholds for this problem.  This directory computes them.

## Results

| k | n(k) | lower-bound witness | upper-bound certificate |
|---|------|--------------------|------------------------|
| 1 | 2    | trivial (see below) | trivial |
| 2 | **14**   | `results/witness_k2_n13.txt` | DRAT, verified (`certificates/k2/`) + exhaustive 2^14 enumeration |
| 3 | **46**   | `results/witness_k3_n45.txt` | DRAT, verified (`certificates/k3/`) |
| 4 | > 64 (exact value not reached in budget) | `results/witness_k4_n64.txt` | none yet — n = 96 and n = 128 were still undecided when the compute budget ended |

Every threshold means two facts, each with its own evidence:

* **n(k) <= N** ("every colouring is hit"): the CNF whose satisfying
  assignments are exactly the colourings of [1..N] avoiding monochromatic
  A+A is unsatisfiable.  kissat 4.0.4 emits a DRAT refutation which
  drat-trim verifies (`s VERIFIED`).  For k=2 this is additionally confirmed
  by SAT-free exhaustive enumeration of all 2^14 colourings
  (`code/exhaustive_check_n2.py`).
* **n(k) > N-1** (lower bound): an explicit avoiding colouring of [1..N-1],
  found as a SAT model and re-checked by an independent clique-based checker
  (`code/check_coloring.py`) that shares no code with the CNF generator.

n(1) = 2 is trivial: a valid 1-element A = {a} needs A+A = {2a} inside
[1..n], which is impossible for n = 1 and automatic for n = 2 (any colouring
makes the single element 2 monochromatic).

### Extremal structure

For k = 2 the avoiding colourings of [1..13] were enumerated exhaustively
(`results/extremal_k2_n13.txt`): there are exactly 16, and they are ONE
colouring up to colour swap and three irrelevant positions {1, 7, 13}
(1 and 13 occur in no valid sumset; every pair-constraint through 7 is
already broken elsewhere).  The core pattern, as the colour-1 class on
[2..12], is {3, 5, 6, 10, 12}: note it splits the doubled elements as
{6, 10, 12} vs {2, 4, 8} — colour(2a) equals 1 exactly for a in {3, 5, 6},
and the pairwise sums then dodge both classes.

Lower-bound witnesses for k = 3 and k = 4 are in `results/witness_k*.txt`
(one 0/1 line, position i = colour of integer i).

### Status of k = 4

n(4) > 64 is certified (SAT witness, independently re-checked).  The
instances n = 96 and n = 128 were still undecided — by both the full-CNF
run (2.5M clauses, 13+ CPU-minutes) and the lazy-constraint runs (pools of
55-60k active subsets after 150-450 refinement rounds) — when the compute
budget ended; see the `budget_stop` entry in `results/search_log.jsonl`.
The sharp hardness jump from k = 3 (0.05 s) to k = 4 (minutes-to-hours near
the boundary) is itself a data point: the lazy pools show tens of thousands
of active constraints, i.e. the extremal colourings at k = 4 are far less
rigid than the unique core found at k = 2.

## Encoding

Variables x_1..x_n, x_i = colour of i.  For each k-subset A of
{1,...,floor(n/2)}, with S = A+A (doubles included), two clauses forbid S
monochromatic: (OR_{s in S} x_s) and (OR_{s in S} not x_s).  No symmetry
breaking is used, so an UNSAT certificate covers ALL colourings directly.

* SAT model  =>  avoiding colouring  =>  n(k) > n.
* UNSAT      =>  every colouring contains a monochromatic A+A  =>  n(k) <= n.

Avoidance is monotone in n (restriction of an avoiding colouring is
avoiding), so the threshold is located by doubling + binary search
(`code/search_thresholds.py`).

For k = 4 the full CNF has 2*C(n/2, 4) clauses (~21M at n = 256), so
`code/cegar_search.py` solves lazily: solve a growing pool of discovered
constraints; a SAT model is checked against ALL constraints by the
independent checker (violations join the pool); UNSAT on a pool is already a
sound upper-bound proof, because the pool is a subset of the true constraint
set and each clause is a genuine constraint.

The witness checker reformulates "A+A monochromatic in colour c" as a
k-clique problem: vertices are {a <= n/2 : colour(2a) = c}, edges are pairs
with colour(a+b) = c.  This gives an exact exhaustive check that shares
nothing with the CNF pipeline.

## Reproducing

Environment: Python 3.12 (stdlib only), kissat 4.0.4 (Homebrew), drat-trim
(github.com/marijnheule/drat-trim, built with `cc -O2`, vendored under
`tools/drat-trim/`).  Everything is deterministic: the CNF generator is
seedless and canonical, kissat runs with default (deterministic) settings.

```
python3 code/search_thresholds.py 2      # rediscovers n(2) = 14
python3 code/search_thresholds.py 3      # rediscovers n(3) = 46
python3 code/cegar_search.py 4           # k = 4 (lazy constraints)
python3 code/certify_boundary.py 2 14    # regenerate + verify DRAT proof
python3 code/certify_boundary.py 3 46
python3 code/exhaustive_check_n2.py      # SAT-free confirmation of n(2)
python3 code/count_extremal.py 2 13      # all 16 extremal colourings
./verify.sh                              # < 5 min spot-check of everything
```

Raw run evidence: `results/search_log.jsonl` (every solver call: instance,
status, clause count, timing), `results/k4_run.log`, `results/k4_lazy_run.log`.

## Relation to prior work (full credit)

* J. Owings, *Problem E2494*, Amer. Math. Monthly 81 (1974) — the conjecture.
* P. Erdős, *A survey of problems in combinatorial number theory* (1980),
  p.104 — recorded the problem.
* N. Hindman, *Partitions and sums of integers with repetition*,
  J. Combin. Theory Ser. A 27 (1979) — the 3-colouring counterexample; also
  Hindman's finite-sums theorem for the doubles-free variant (Erdős #532).
* T. F. Bloom, Erdős Problem #1199, https://www.erdosproblems.com/1199
  (accessed 2026-07-27) — problem status and history.
* D. J. Fernández-Bretón, E. Sarmiento Rosales, G. Vera, *Owings-like
  theorems for infinitely many colours or finite monochromatic sets*, Ann.
  Pure Appl. Logic 175 (2024), arXiv:2402.13124 — proves that for every
  infinite group G and finite n, r, every r-colouring of G admits an
  n-element X with X+X monochromatic.  Note this does not automatically
  transfer to colourings of the *positive* integers (a colouring of N
  extended to Z can be hit only by an X whose sumset leaves N), and the
  paper gives no numeric thresholds; the values of n(k) here appear to be
  the first published.
* The statement is formalized in Lean at
  google-deepmind/formal-conjectures (ErdosProblems/1199.lean).
* Tools: kissat (A. Biere et al.), drat-trim (M. Heule et al.).

What these computations say about the infinite problem: nothing decisive
(the erdosproblems.com page correctly notes it "cannot be resolved with a
finite computation") — but the thresholds and extremal colourings are
exactly the finite data the problem page's open question about n(k) asks
for, and the extremal structure (rigid core, near-forced doubled elements)
is the raw material for guessing an infinite avoiding colouring or proving
none exists.
