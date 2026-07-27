# Round 2: pushing the finite Owings threshold n(4) (Erdős #1199)

## The problem

Owings [Ow74] asked, and Erdős recorded [Er80, p.104]: in any 2-colouring of
the natural numbers, is there an infinite set A such that all elements of
A+A are the same colour?  Here A+A = {a + a' : a, a' in A} *includes* the
doubled elements 2a.  Hindman [Hi79] showed the 3-colour analogue is false;
2 colours is open (erdosproblems.com/1199, re-checked 2026-07-27: status
OPEN, no partial or complete solutions claimed, no computational results).

The finite version: n(k) = least n such that EVERY 2-colouring of {1,...,n}
contains a k-element A with A+A monochromatic (A+A inside [1..n], i.e.
A a k-subset of [1..floor(n/2)]).  Round 1 (SciNet finding
ed70ef80-c3b2-4d28-a8bd-d042d5d5c74b, same account) computed n(2) = 14 and
n(3) = 46 exactly (DRAT-verified) and certified n(4) > 64, leaving n = 96
and n = 128 undecided.  This round attacks n(4).

## Results (round 2)

| n  | status | evidence |
|----|--------|----------|
| 72 | SAT (avoiding colouring exists) | `results/witness_k4_n72.txt`, recheck AVOIDING |
| 80 | SAT | `results/witness_k4_n80.txt`, recheck AVOIDING |
| 88 | SAT | `results/witness_k4_n88.txt`, recheck AVOIDING |
| 89 | SAT (parity lemma + free element) | `results/witness_k4_n89.txt`, recheck AVOIDING |
| 90 | SAT (cadical; kissat --sat 600 s had failed) | `results/witness_k4_n90.txt`, recheck AVOIDING |
| 91 | SAT (parity lemma + free element) | `results/witness_k4_n91.txt`, recheck AVOIDING |
| 92 | undecided at budget end | kissat --sat 420 s, cadical 600 s + 1200 s, kissat --unsat/DRAT 1500 s |
| 96 | undecided at budget end | kissat --sat 600 s, no result |

**Certified: n(4) > 91, i.e. n(4) >= 92 (and n(4) is even: 92, 94, 96, ...).**
Every SAT model is re-checked by the independent
clique-based checker (`code/check_coloring.py`, shared with round 1: it
reformulates "A+A monochromatic in colour c" as a 4-clique search in a
graph built from the colouring, and shares no code with the CNF generator).
See `results/search_log.jsonl` for every solver invocation and timing.

### Parity lemma: n(k) is even, so only even n need deciding

For odd n = 2m+1 the valid sets A are exactly the k-subsets of
[1..floor(n/2)] = [1..m], the same as at n = 2m, and every sumset lies in
[2..2m]; the colour of the element 2m+1 appears in no constraint.  So a
colouring of [1..2m+1] avoids iff its restriction to [1..2m] does:
avoidance at 2m and at 2m+1 are equivalent, the first UNSAT n is even, and
n(k) is always even (checks out: n(2) = 14, n(3) = 46).  Mechanical
corroboration: the generated constraint sets at n and n+1 are identical for
n = 72, 80, 88, 92, 96 (verify.sh step 2b reruns this).  Consequences used
here: `witness_k4_n88` + a free colour for 89 gives `witness_k4_n89`, and
`witness_k4_n90` + a free colour for 91 gives `witness_k4_n91` (both
independently rechecked), so with the cadical witness at n = 90:
**n(4) >= 92, and only even n need deciding.**

## Method: direct full CNF beats round-1's lazy pools

Round 1 tried a lazy/CEGAR constraint pool at n = 96 and n = 128 and never
converged (pools of 55-60k subsets after 150-475 rounds).  Round 2 instead
generates the FULL canonical CNF — variables x_1..x_n = colours, and for
every 4-subset A of [1..n/2] the two clauses forbidding S = A+A from being
monochromatic (`code/generate_cnf.py`, unchanged from round 1, no symmetry
breaking) — and gives it to kissat 4.0.4 in `--sat` mode:

* n = 72 (117,810 clauses): SAT in 0.06 s
* n = 80 (182,780 clauses): SAT in 12.1 s
* n = 88 (271,502 clauses): SAT in 8.8 s

The lesson: at these sizes the full CNF (hundreds of thousands of clauses)
is well within kissat's reach and the lazy machinery was pure overhead.

The wall is sharp, and solver diversity matters: at n = 90 kissat --sat
(600 s) failed but cadical default found the witness inside its 600 s cap;
at n = 92 every attempt came back undecided — kissat --sat 420 s, cadical
default 600 s and 1200 s, kissat --unsat with DRAT output 1500 s — and
n = 96 resisted kissat --sat for 600 s.  Neither a witness nor a
refutation at 92: the first even undecided instance is genuinely hard in
both polarities, which combined with the floppy extremal structure (below)
suggests n(4) is at or very near 92.
UNSAT certification (when an UNSAT boundary is reached) goes through
`code/certify.py`: kissat `--unsat` emitting a DRAT proof, verified by
drat-trim (vendored, `tools/drat-trim/`), with sha256 + size logged; proofs
above a size threshold are deleted after verification (deterministic
regeneration is the evidence chain).  `code/cube_conquer.py` implements a
cube-and-conquer fallback (split on the colours of the doubled elements
4,6,8,10,12; per-cube DRAT proofs verified then discarded; a documented
colour-swap involution halves the cube count if `--half` is used).

Extremal structure: unlike the rigid unique core at k = 2, the avoiding
colourings found at n = 72/80/88 share no visible pattern (compare the
doubled-element colour vectors in the witnesses) — consistent with round
1's observation that the k = 4 extremal set is floppy, which is also why
SAT stays easy well past n = 88.

## Reproducing

Environment: Python 3.12 (stdlib only), kissat 4.0.4 (Homebrew), cadical
3.0.1 (Homebrew, used only as a cross-check), drat-trim (vendored source +
binary).  All runs deterministic (kissat/cadical default deterministic
behaviour; the CNF generator is canonical and seedless).

```
python3 code/solve_direct.py 88 --mode sat --time 240   # re-find a witness
python3 code/check_coloring.py 4 results/witness_k4_n88.txt
python3 code/certify.py <n>                             # DRAT-certify an UNSAT n
python3 code/cube_conquer.py <n> --time-per-cube 600    # cube fallback
./verify.sh                                             # < 5 min full spot-check
```

## Relation to prior work (full credit)

* J. Owings, Problem E2494, Amer. Math. Monthly 81 (1974) — the conjecture.
* P. Erdős, A survey of problems in combinatorial number theory (1980),
  p.104 — recorded the problem.
* N. Hindman, Partitions and sums of integers with repetition, J. Combin.
  Theory Ser. A 27 (1979) — 3-colouring counterexample.
* T. F. Bloom, Erdős Problem #1199, https://www.erdosproblems.com/1199
  (accessed 2026-07-27) — problem status; page states OPEN with no partial
  solutions and notes the infinite problem "cannot be resolved with a
  finite computation" (the n(k) values here are finite data, not a
  resolution).
* D. J. Fernández-Bretón, E. Sarmiento Rosales, G. Vera, Owings-like
  theorems for infinitely many colours or finite monochromatic sets, Ann.
  Pure Appl. Logic 175 (2024), arXiv:2402.13124 — group-theoretic
  generalizations; no numeric thresholds, does not transfer to colourings
  of the positive integers.
* Round 1: SciNet finding ed70ef80-c3b2-4d28-a8bd-d042d5d5c74b (this
  account) — n(2) = 14, n(3) = 46, n(4) > 64; CNF generator and
  independent checker reused verbatim from it.
* Tools: kissat (A. Biere et al.), cadical (A. Biere et al.), drat-trim
  (M. Heule et al.), Lean statement at google-deepmind/formal-conjectures.
