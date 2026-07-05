# Erdős Problem #728 — independent formal verification

**What this is.** A reproducible **Lean 4 kernel check** of the formal proof resolving
[Erdős Problem #728](https://www.erdosproblems.com/728). SciNet did **not** discover or formalize
this result — we **independently verify** it: `verify.sh` fetches the upstream proof at a pinned
commit, builds it against the pinned mathlib, and confirms the answer theorems are **sorry-free**
(their only axioms are Lean/mathlib's standard `propext, Classical.choice, Quot.sound`).

## Credit (the discovery + formalization are theirs, not ours)

- **Informal proof:** Kevin Barreto & **ChatGPT-5.2** — *"Factorial Divisibility Beyond the
  Logarithmic Barrier."*
- **Lean formalization:** **Aristotle** (Harmonic), Kevin Barreto, and **Boris Alexeev**.
- **Upstream proof repo:** [`plby/lean-proofs`](https://github.com/plby/lean-proofs) @
  `97957fb9083d6b321843fbb3c1cbff82e076aa66`, file
  `src/latest/ErdosProblems/Erdos728.lean` (theorems `erdos_728`, `erdos_728_fc`).
- **Statement index:** [`google-deepmind/formal-conjectures`](https://github.com/google-deepmind/formal-conjectures)
  `FormalConjectures/ErdosProblems/728.lean`.
- **Discussion / write-up:** erdosproblems.com forum thread 728; arXiv:2601.07421.

## The result

Problem #728 (intended form). For any `0 < ε < 1/2` and `0 < C < C'`, are there integers
`a, b, n` with `a, b > ε·n`, `a!·b! ∣ n!·(a+b−n)!`, and `C·log n < a+b−n < C'·log n`? The proof
answers **yes** (infinitely many such triples), via the probabilistic method — Kummer's theorem
relating `v_p(C(2m,m))` to base-`p` carry counts, plus a Chernoff bound showing almost all `m`
have enough carries.

The formalized answer theorem (matches the formal-conjectures statement verbatim):

```lean
theorem erdos_728_fc :
    ∀ᶠ ε : ℝ in 𝓝[>] 0, ∀ C > (0 : ℝ), ∀ C' > C,
      ∃ a b n : ℕ,
        0 < n ∧ ε * n < a ∧ ε * n < b ∧
        a ! * b ! ∣ n ! * (a + b - n)! ∧
        a + b > n + C * log n ∧ a + b < n + C' * log n
```

**Faithfulness note (important for review).** erdosproblems.com currently displays a *simpler,
trivial* version of #728 (without the `a+b ∈ n + O(log n)` window). The formalization above
proves the **intended, non-trivial** version discussed in the forum thread — this is the correct
target, but a reviewer should confirm the formal statement matches the *intended* problem, not
the trivial website rendering. The kernel certifies the proof; a human/agent must certify that
the statement is the right one.

## Verification result (this machine, 2026-07-05)

```
Build completed successfully (8580 jobs).
'Erdos728.Erdos728b.erdos_728'    depends on axioms: [propext, Classical.choice, Quot.sound]
'Erdos728.Erdos728b.erdos_728_fc' depends on axioms: [propext, Classical.choice, Quot.sound]
```

No `sorryAx` → the proof has no gaps. Toolchain `leanprover/lean4:v4.32.0-rc1`, mathlib
`360da6fa66c1273b76b6b2d8c5666fd5ac2e3b56`. Full log: [`build_Erdos728.log`](build_Erdos728.log).

## Reproduce

```bash
./verify.sh
```

Installs `elan` if absent, clones the upstream proof at the pinned commit, runs `lake exe cache
get` (prebuilt mathlib oleans, ~5 GB) + `lake build ErdosProblems.Erdos728`, and asserts the
build succeeds and the answer theorems' axiom sets contain no `sorryAx`. Exit 0 ⇔ verified.
Expect ~5–15 min on a first run (cache download dominates); the proof compile itself is ~40 s.
