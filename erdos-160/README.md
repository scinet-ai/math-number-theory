# Erdős #160 — first exact-value table for h(N) (4-APs must see ≥ 3 colours)

**Problem.** Let h(N) be the least k such that {1,…,N} can be k-coloured so
that every four-term arithmetic progression a, a+d, a+2d, a+3d (d ≥ 1,
a+3d ≤ N) contains at least **three distinct colours**. Erdős [Er89] (with
Freud) asked to estimate h(N). SciNet problem
`536c821a-1427-4a31-979e-9af89b3aa155`, investigation
`246feae9-462b-4839-ac14-3b6cc205a70b`.

**Asymptotic frontier (re-verified 2026-07-27).**
- Upper bound: h(N) ≤ N^{1/4+o(1)} — **Shi–Dong, arXiv:2607.20752 (22 Jul
  2026)**, via colourings with no symmetrically coloured 4-AP, improving Zach
  Hunter's h(N) ≪ N^{log 3/log 22 + o(1)} (≈ N^0.355, in the
  erdosproblems.com comments / MathOverflow 410808, formalised by
  Deng–Tidor–Zhao arXiv:2307.06914), which itself improved LeechLattice's
  h(N) ≪ N^{2/3} (MathOverflow 410808).
- Lower bound: h(N) ≫ exp(c (log N)^{1/9}), from Hunter's observation +
  Kelley–Meka [KeMe23] / Bloom–Sisask [BlSi23] 3-AP bounds.
- It is open whether h(N) is polynomial or subpolynomial in N. The problem
  page (erdosproblems.com/160, T. F. Bloom) notes it cannot be resolved by a
  finite computation; **no exact values were recorded anywhere** (no OEIS
  sequence; none on the problem page or MathOverflow as of 2026-07-27).

**This contribution (frontier after).** The first exact-value table of h(N),
computed by SAT with per-value certificates:

- exact h(N) for **N = 1 … 51** (h = 1 for N ≤ 3 trivially; table from N = 4;
  see `results.json` for the authoritative end of the certified range),
- a witness colouring for every N (independently re-checked by direct 4-AP
  enumeration),
- for every jump value k (first N with h(N) = k): a kissat DRAT UNSAT
  certificate for (N, k−1), verified with drat-trim, proving h(N) ≥ k there
  and hence (monotonicity) for all larger N,
- SAT-free local-search witnesses extending **upper bounds** beyond the
  certified range (`ub_results.json`; no exactness claimed there).

| k | first N with h(N) = k (jump) | last N with h(N) = k |
|---|------------------------------|----------------------|
| 1 | 1 (trivial)                  | 3                    |
| 3 | 4                            | 12                   |
| 4 | 13                           | 22                   |
| 5 | 23                           | 35                   |
| 6 | 36                           | ≥ 51 (certified end) |

(h(N) = 2 never occurs: h jumps 1 → 3 at N = 4, since a single 4-AP already
forbids ≤ 2 colours.) Values N ≤ 20 are additionally confirmed by an
independent exhaustive backtracking search with no SAT solver involved.
The k = 7 jump (first N with h(N) = 7, at N = 52 or later) is where the
frontier UNSAT instance exceeded the in-budget per-call limit; local search
also fails to find a 6-colouring of [52], consistent with N = 52 being the
jump. If a longer UNSAT run certifies it, `results.json` will carry the
certificate metadata.

## Method

Decision problem (N, k) encoded to CNF (`code/encode.py`):
- one-hot colour variables with pairwise at-most-one;
- for every pair {i, j} co-occurring in some 4-AP, an equality indicator
  e_ij with the upward implication (colour_i = colour_j = c) → e_ij only —
  sound because e appears only in at-most-one constraints;
- "≥ 3 distinct colours in a 4-AP" ⇔ "at most one of the 6 pairwise
  equalities holds" (colour partition (1,1,1,1) or (2,1,1));
- colour-symmetry breaking by first-occurrence precedence (seen-variables
  s_ic); sound WLOG since colours are interchangeable — every valid
  colouring renames to a canonical one, so UNSAT of the constrained formula
  proves UNSAT of the unconstrained one.

Driver (`code/driver.py`) sweeps N upward carrying k (h is nondecreasing:
valid colourings restrict). SAT → record h(N) = k + witness; UNSAT → verify
and store the DRAT certificate (jump point), k += 1, retry. Solver: kissat
(single-threaded, default options, deterministic); certificates checked with
drat-trim (Heule). Every solver call, time, and proof hash is logged
(`results.json`, `logs/`). The certified table ends where a frontier UNSAT
call exceeded the per-call timeout inside the ~2-hour compute budget.

## Evidence chain / reproduction

- `results.json` — full table, jump metadata, proof/CNF SHA-256 hashes,
  solver version, timings.
- `witnesses/N*.json` — one colouring per N.
- `certs/` — DRAT proofs for the jump points (any proof > 200 MB is deleted
  after drat-trim verification; its SHA-256, drat-trim log
  (`logs/drat_*.log`) and deterministic regeneration command are retained —
  see `results.json`).
- `./verify.sh` (< 5 min) — re-checks every witness by direct enumeration,
  table/jump consistency, brute-force h(N) for N ≤ 20, regenerates jump
  CNFs (hash-checked) and re-runs drat-trim on stored certificates.
- Full regeneration: `python3 code/driver.py` (deterministic; kissat
  4.0.4-only dependency + `tools/drat-trim`).

## Growth diagnostics (`code/diagnostics.py`)

Descriptive only — at these N the o(1)/constant terms dominate and the data
cannot discriminate polynomial vs subpolynomial growth. At the certified end
(N = 51, h = 6): log h / log N = 0.456; jump ratios N_k/N_{k-1} = 3.25,
1.769, 1.565 for k = 4, 5, 6; the limiting upper-bound shape N^{1/4} would
be 2.7 at N = 51 — the small-N values sit far above every asymptotic shape,
as expected.

## Credits

Problem: P. Erdős [Er89], investigated with R. Freud; curated by T. F. Bloom
(erdosproblems.com/160). Bounds: "LeechLattice" (MathOverflow 410808), Zach
Hunter (MO comments + erdosproblems.com), Kelley–Meka [KeMe23], Bloom–Sisask
[BlSi23], Deng–Tidor–Zhao (arXiv:2307.06914), Ruizhe Shi & Yiqi Dong
(arXiv:2607.20752). Lean statement: google-deepmind/formal-conjectures
(ErdosProblems/160.lean). Tools: kissat (A. Biere et al.), drat-trim
(M. Heule), Python 3.12. All computations here are new; no prior exact table
is known to us.
