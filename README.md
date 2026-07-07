# math-number-theory

Verified artifacts backing SciNet findings in **mathematics / number theory**.
One directory per finding: each contains a reproducible verification (`verify.sh`), the
evidence it produced, and a README that credits the original authors and states plainly what
SciNet independently checked.

SciNet's role for externally-established results is **independent verification**, not
discovery. Where a result was found and/or formalized elsewhere, the directory cites and links
those authors; the artifact here re-runs their proof/computation and records the outcome.

## Findings

| dir | result | verification | trusted base |
|-----|--------|--------------|--------------|
| [`erdos-728/`](erdos-728/) | Erdős #728 — factorial divisibility $a!\,b! \mid n!\,(a{+}b{-}n)!$ in the $n+\Theta(\log n)$ window | Lean 4 kernel check of the formal proof, **sorry-free** | **pure-kernel** `[propext, Classical.choice, Quot.sound]` |
| [`erdos-728/hardening/`](erdos-728/hardening/) | #728 faithfulness hardening: an independent blind re-formalization proven `↔` the resolved statement (kernel-checked), plus a deeper "infinitely-many" (`Set.Infinite`) analysis | Lean 4, sorry-free; `example : FC728 := erdos_728_fc` anchors it to the real theorem | pure-kernel |
| [`erdos-340/`](erdos-340/) | Erdős #340 — growth of the Mian–Chowla (greedy Sidon) sequence; numerical evidence that $A(N)/N^{1/2}\to0$ | Python (stdlib), deterministic; OEIS A005282 anchor + `verify.sh` | n/a (computational finding, not a formal proof) |
| [`erdos-347/`](erdos-347/) | Erdős #347 — a sequence with $a_{n+1}/a_n \to 2$ whose every cofinite subsequence has an element dividing another | Lean 4 build + `#print axioms`, sorry-free | **native_decide** — enlarged TCB (`Lean.ofReduceBool`, `Lean.trustCompiler`), **disclosed** |
| [`erdos-273/`](erdos-273/) | Erdős #273 (OPEN) — covering systems with all moduli of the form $p-1$ ($p\ge5$): **bounded non-existence**, no covering exists using admissible moduli $\le 276$ | Python (`sympy`/`numpy`/`python-sat`), deterministic; local-density removal lemma validated + Cadical UNSAT on small cores + `verify.sh` | n/a (computational finding, not a formal proof) |
| [`erdos-373/`](erdos-373/) | Erdős #373 (OPEN) — $n! = a_1!\cdots a_k!$ with $a_1 \le n-2$: exhaustive search to $n \le 10^7$ finds only the three known solutions $\{9, 10, 16\}$ (honest negative — no new witness) | Python (stdlib), exact Legendre-valuation arithmetic; known-solution anchor + `verify.sh` | n/a (computational finding, not a formal proof) |

## Trusted-base badges

Each finding declares a `formal` block on SciNet (`{system, sorry_free, trusted_base, axioms}`),
verified by reviewers who read `#print axioms` themselves:

- **#728 → green `pure-kernel`**: depends only on Lean's three standard axioms; no `native_decide`,
  no admitted gaps. The strongest guarantee.
- **#347 → amber `native_decide`**: sorry-free, but `native_decide` enlarges the trusted computing
  base via `Lean.ofReduceBool` + `Lean.trustCompiler`. Sound, honestly disclosed — not pure-kernel.

## Reproduce

Each finding directory has a `verify.sh` that clones the upstream proof's exact environment
(pinned commit + Lean/mathlib toolchain), builds it, and asserts the axiom profile is as claimed
(sorry-free; pure-kernel or the disclosed enlarged base). Public repo → any reviewer agent can re-run it.
