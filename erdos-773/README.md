# Erdős #773 — certified extension of the exact table of S(N)

**Problem** (Erdős 1980 [Er80, p.109]; Alon–Erdős 1985 [AlEr85];
erdosproblems.com/773): let S(N) be the size of the largest Sidon (B_2)
subset of the first N perfect squares {1², 2², …, N²}. How large is S(N) —
in particular is S(N) = N^{1−o(1)}?

**This computation** extends the table of exact values of S(N)
(OEIS A390813) beyond its published frontier, with machine-checkable
certificates, plus certified witness lower bounds at larger N and an
exponent-trend report.

## Frontier before → after

- Before (2026-07-27): A390813 lists a(1)–a(68); a(43)–a(68) added by
  Christian Sievers, 2025-11-27. Best published bounds:
  N^{2/3} ≪ S(N) (Lefmann–Thiele 1995) and
  S(N) ≤ N·exp(−c·log N/log log N) (Croot–Mao–Yip 2026, announced on the
  problem page 2026-04-17; cf. arXiv:2606.17487).
- After (honest statement):
  * The published exact frontier n = 68 was **not extended**: frontier
    UNSAT instances (level 60 of our self-certified chain; level 69 of an
    OEIS-anchored track) resisted ~25–30 min of core time each
    (`logs/frontier_attempts.md`).
  * **Independently certified** exact table S(1..59) — every value matches
    A390813, every witness re-verified in exact integer arithmetic, and
    all 30 optimality (UNSAT) steps carry kissat DRAT proofs checked by
    drat-trim (31 certificates incl. a complete 2-cube family at level 55;
    2.45 GB of proofs, 3315 s total checking; `results/certs.jsonl`).
    A390813 itself ships no proof artifacts, so this is the first
    machine-checkable certificate chain for the table's first 59 values.
  * **New certified lower bounds** (explicit witnesses, re-verified
    exactly; `results/lb.jsonl`, `results/lb_prior_verified.json`):
    S(100) ≥ 42, S(150) ≥ 54, S(200) ≥ 65, S(300) ≥ 80.
    No values at these N appear in A390813 or the literature.
  * Exponent trend (`results/fit.json`): log S(N)/log N ≈ 0.83 at N=25,
    0.826 at N=59 (exact); lower-bound exponents 0.812 @100 → 0.768 @300;
    local LSQ slope of log S vs log N over N ∈ [29,59] ≈ 0.70. Consistent
    both with S(N) = N^{1-o(1)} and with the Croot–Mao–Yip ceiling
    N^{1-c/log log N}; this scale cannot discriminate.

## Method

Incremental chain. S(N) ∈ {S(N−1), S(N−1)+1}, and S(N) = S(N−1)+1 iff
some square-Sidon subset of size S(N−1)+1 contains N² (else it would live
in the first N−1 squares). So each level is ONE decision problem:

    exists A ⊆ {1..N} (roots), |A| ≥ S(N−1)+1, N ∈ A,
    no two distinct pairs {i,j} ≠ {k,l} (repeats allowed) with
    i²+j² = k²+l² both inside A?

- Collision clauses: all pairs-of-pairs of equal square sums (includes the
  2b² = a²+c² doubles). Generated exactly (`code/sidon_common.py`).
- Cardinality: Sinz sequential counter (`code/cnf.py`); the totalizer
  encoding and cadical were benchmarked slower by the earlier run
  (`prior-attempt/RESULTS.md`).
- Engines: CP-SAT (ortools) for levels ≤ 45 (`code/chain.py`), then kissat
  (`code/chain2.py`), then — the step that made the frontier reachable —
  **profile-strengthened instances** (`code/chain3.py`, `code/cnf.py:
  build_cnf_profile`): a bidirectional sequential counter over x_1..x_N
  with unit upper bounds  Σ_{i≤m} x_i ≤ S(m)  for every m < N, each bound
  being a previously certified chain value (valid since a square-Sidon set
  restricted to {1..m} is square-Sidon in the first m squares). This cut
  UNSAT times ~3–4× over plain kissat (logged: N=45: 124.6 s CP-SAT →
  5.1 s kissat → 1.6 s profile-strengthened; N=53: 76.5 s → 18.9 s) and
  was validated by re-deciding levels 38–53 with identical outcomes
  (16/16, `logs/validate_profile.log`) before use.
- Certificates: every UNSAT level's DRAT proof is checked with drat-trim
  (`results/certs.jsonl`: cnf/proof SHA-256, sizes, check time). Proof
  files are deleted after successful verification — CNFs regenerate
  deterministically from `code/cnf.py`. UNSAT levels ≥ 54 are conditional
  lemmas (they assume the certified prefix profile), forming a standard
  inductive certificate chain; levels ≤ 53 are unconditional.
- Witnesses: every SAT step's model is re-verified in exact Python integer
  arithmetic before being recorded; the final witness for each N is in
  `results/chain.jsonl`.
- Lower bounds at large N (`code/lb_climb.py`): kissat --sat with rising
  size targets (method due to the earlier partial run, preserved in
  `prior-attempt/`), witnesses re-verified exactly.

## Reproduce / verify

- `./verify.sh` (< 5 min): chain consistency, exact re-verification of all
  witnesses, OEIS cross-check (n ≤ 68), fresh brute force (n ≤ 18), DRAT
  cert ledger completeness, spot re-solve + fresh DRAT check of three
  UNSAT levels, lower-bound witness checks.
- Full regeneration: `code/chain.py` → `code/chain2.py` / `code/chain3.py`
  (see file docstrings for exact invocations; all runs logged in `logs/`).

## Environment

macOS arm64 (Darwin 25.5.0), Python 3.11.15 (uv venv), ortools 9.15.6755,
kissat 4.0.4 (Homebrew), cadical 3.0.1 (benchmark only), drat-trim built
from marijnheule/drat-trim@master with clang -O2 (`code/drat-trim.c`).
Determinism: fixed seeds where applicable; all arithmetic exact.

## Credit

- Problem: Erdős [Er80]; Alon–Erdős [AlEr85]. Page: Thomas Bloom,
  erdosproblems.com/773 (accessed 2026-07-27).
- OEIS A390813: Giorgos Kalogeropoulos (author, 2025-11-20); a(43)–a(68)
  Christian Sievers (2025-11-27). This work extends their table.
- Upper bound N·exp(−c log N/log log N): Ernie Croot, Junzhe Mao, Kyle Yip
  (2026, announced on erdosproblems.com/773; cf. arXiv:2606.17487).
- Lower bound N^{2/3}: Lefmann–Thiele (1995).
- Solvers: kissat/cadical (Armin Biere et al.), drat-trim (Marijn Heule),
  OR-Tools CP-SAT (Google).
- Earlier partial attack run today (preserved in `prior-attempt/`):
  chain to N=41, S(68) witness, kissat --sat climb method and encoding
  benchmarks, lower-bound witnesses at N=100/150/200 (re-verified here).

## Files

- `results/chain.jsonl` — the certified chain (one record per N: value,
  step type, witness, wall, encoder stats).
- `results/certs.jsonl` — DRAT certificate ledger (sha256 of CNF + proof,
  sizes, drat-trim time, verified flag, encoding tag; proofs deleted after
  successful verification, CNFs regenerate deterministically).
- `results/lb.jsonl`, `results/lb_prior_verified.json` — lower-bound
  witnesses. `results/fit.json` — exponent trend.
- `logs/` — run logs incl. `frontier_attempts.md` (what did not resolve).
- `prior-attempt/` — preserved artifacts of the earlier partial run today
  (chain to N=41, benchmarks, kissat --sat climb method, lb witnesses),
  which this run builds on.
- `code/chain.py, chain2.py, chain3.py, cube.py, anchored.py` — engines;
  `code/cnf.py` — encoders; `code/verify.py` + `verify.sh` — verifier;
  `code/cert_*.py` — certificate plumbing; `code/lb_climb.py` — bounds.
