# Erdős #273 — covering systems with moduli of the form $p-1$

**Question (Erdős #273, [erdosproblems.com/273](https://www.erdosproblems.com/273), OPEN).**
Does there exist a *covering system* — a finite set of congruences
$x \equiv a_i \pmod{m_i}$ with **distinct** moduli $m_i>1$ covering every integer —
in which **every modulus has the form $p-1$ for a prime $p\ge 5$**?
The admissible moduli are
$$\{p-1 : p \text{ prime}, p\ge5\} = \{4,6,10,12,16,18,22,28,30,36,40,42,46,52,\dots\}.$$

This directory attacks the two finite, computational faces of the problem:
**(a) witness search** (find a covering) and **(b) bounded non-existence** (prove
no covering uses only admissible moduli $\le M$, for explicit $M$).

## Result (this work)

**No covering system of Erdős-#273 type exists using only admissible moduli $\le 276$.**
(Equivalently, using only admissible moduli $< 280$ — there is no admissible
modulus strictly between 276 and 280.) This is **search-free**: it follows from a
per-prime *local-density removal lemma* that reduces the admissible set to a
"core" whose reciprocal sum is $<1$, so the core — and hence the full admissible
set $\le 276$ — cannot cover $\mathbb{Z}$.

This strictly improves the naïve reciprocal-sum bound. The full admissible set's
reciprocal sum $\sum 1/m$ already exceeds $1$ at $M=70$, so the naïve
"$\sum 1/m \ge 1$ is necessary" argument proves non-existence only for $M\le 68$.
The reduction pushes the certified non-existence bound to $M=276$ — a $\sim4\times$
extension — with no search.

At $M=280$ the reduced core's reciprocal sum first crosses $1$
(it becomes $\{4,6,10,12,16,18,28,30,36,40,42,60,70,72,96,100,108,112,126,150,162,180,192,196,210,240,250,256,270,280\}$,
$\sum 1/m \approx 1.0079$, $\operatorname{lcm}=127{,}008{,}000$), so the reduction
is no longer conclusive there and an exact search over $\mathbb{Z}/\mathrm{lcm}$ is
required. **No witness was found within the searched region; the question remains
open for $M\ge 280$.**

See `results_table.md` for the full sweep.

## The local-density removal lemma (why the bound moves)

Every admissible modulus is even. More is true: rare prime factors are useless.

> **Lemma.** Let $S$ be a set of moduli and $q$ a prime. If
> $\sum_{m\in S,\; q\mid m} q^{-v_q(m)} < 1$
> (where $v_q$ is the $q$-adic valuation), then **every** modulus in $S$ divisible
> by $q$ is redundant: a covering with moduli in $S$ exists **iff** one exists with
> those moduli deleted.

*Proof sketch.* Let $v=\max_{m\in S} v_q(m)$ and $L'=\operatorname{lcm}(S)/q^{v}$.
The classes whose moduli are coprime to $q$ cover a set that is invariant under
$x\mapsto x+L'$; its complement $U$ is therefore a union of full $+L'$-orbits, each
of which meets every residue mod $q^{v}$ exactly once ($q^{v}$ points). A class
$a\bmod m$ with $q^{f}\,\|\,m$ meets any such orbit in at most $q^{v-f}$ of its
$q^{v}$ points. Hence the $q$-divisible classes together cover at most
$q^{v}\sum_{q\mid m} q^{-v_q(m)} < q^{v}$ points of any orbit in $U$ — not all of
it. So $U=\varnothing$: the $q$-coprime classes already cover $\mathbb{Z}$, and all
$q$-divisible moduli are redundant. $\square$

Applied iteratively to a fixpoint (removing one prime's multiples can make another
prime's weight drop below $1$), this yields the **core**, which is equivalent to
the full admissible set for the covering question. For admissible moduli $\le 276$
the surviving primes never accumulate enough weight, and the core's reciprocal sum
stays $<1$ — impossible to cover.

The lemma is **validated empirically** (`test_sanity.py`, check [4]): on hundreds
of random modulus sets, coverability of the full set equals coverability of the
reduced core, decided independently by a SAT solver.

## Files

| file | purpose |
|---|---|
| `admissible.py` | admissible-moduli generator; factorization; `reduce_local_density` (the lemma) |
| `cover_sat.py` | covering **verifier** `covers()`; two exact engines — Cadical **SAT** and a numpy **backtracking** search |
| `frontier_search.py` | in-place-undo backtracking search over $\mathbb{Z}/\mathrm{lcm}(\text{core})$ for a given bound $M$ (witness or UNSAT) |
| `run_results.py` | master reduction sweep → `results_table.md` |
| `test_sanity.py` | sanity + lemma-validation suite (must pass before any UNSAT is trusted) |
| `results_table.md` | the exhaustion table |
| `verify.sh` | re-runs a fast verification slice + the known-system sanity check |

## Reproduce

```bash
bash verify.sh            # fast slice (~1-2 min): sanity, lemma validation, sweep, boundary UNSAT
uv run --with sympy --with numpy python3 run_results.py 1000        # full reduction sweep
uv run --with sympy --with numpy python3 frontier_search.py 280 300 # attempt the M=280 exact search
```

Engines: Python 3.12, `sympy` (factorization), `numpy` (bitset search),
`python-sat` (Cadical). All computations are deterministic and rerunnable.

## What a follow-up should try

- **Push past $M=280$** with a proper SAT/CP solver on $\mathbb{Z}/127008000$
  (naïve Python clause-generation does not scale; use a native DIMACS pipeline,
  incremental CP-SAT, or the recursive 2-adic tree structure). The core sum sits
  just above $1$ (≈1.008), so any covering there is nearly an exact partition —
  strong reason to expect UNSAT, but it must be verified.
- **A sharper reduction.** The per-prime lemma is a *first-order* local-density
  test. A combined multi-prime / per-prime-power necessary condition (e.g. the
  2-adic projection must itself cover $\mathbb{Z}/2^{v_2}$) may certify
  non-existence for larger $M$ without an exhaustive search.

## Credit / provenance

Problem: Erdős #273, [erdosproblems.com/273](https://www.erdosproblems.com/273);
Erdős–Graham, *Old and new problems and results in combinatorial number theory*
(1980). The minimum-modulus problem (Erdős #2) was resolved by Hough (2015),
simplified by Balister–Bollobás–Morris–Sahasrabudhe–Tiba; #273 restricts moduli to
the thin set $\{p-1\}$ and remains open. This directory contributes verified
bounded non-existence, not a resolution.
