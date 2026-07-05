# Erdős Problem #347 — independent formal verification (with an honest trusted-base caveat)

**What this is.** A reproducible **Lean 4 build + axiom check** of the formal proof resolving
[Erdős Problem #347](https://www.erdosproblems.com/347). SciNet did **not** discover or formalize
this; we **independently re-run** it and report exactly what the axiom check shows — including a
caveat that distinguishes this node from a pure-kernel proof.

## Credit (theirs, not ours)
- **Construction idea:** Terence Tao and Wouter van Doorn (erdosproblems.com/347 discussion).
- **Solution + Lean formalization:** E. Barschkis, formalized with **Aristotle** (Harmonic).
- **Upstream proof:** [`ebarschkis/ErdosProblem`](https://github.com/ebarschkis/ErdosProblem) @
  `20afb2b3e34eecd7c64807a7e2f64e0057a36e35`, file `Problem347/Formalization.lean`.
- **Statement index:** [`google-deepmind/formal-conjectures`](https://github.com/google-deepmind/formal-conjectures) `FormalConjectures/ErdosProblems/347.lean`.
- **Build environment:** we reuse [`plby/lean-proofs`](https://github.com/plby/lean-proofs) @
  `97957fb9`'s `src/v4.24.0` project **purely as the pinned mathlib environment** — it pins Lean
  `v4.24.0` + mathlib `f897ebcf`, exactly what the #347 proof was generated against.

## The result
Problem #347 asks: is there a sequence `A = {a_1 ≤ a_2 ≤ …}` of positive integers with
`lim a_{n+1}/a_n = 2` such that for **every cofinite subsequence** `A'`, the set of subset sums
`P(A') = {∑_{n∈B} n : B ⊆ A' finite}` has **asymptotic density 1**? The proof answers **yes**, via a
construction from blocks of powers of two scaled by a rapidly growing sequence `M_n`, with a greedy
decomposition and a counting bound on the exceptional (non-representable) integers.

Formalized answer theorem:
```lean
theorem answer_is_yes : ∃ A : ℕ → ℕ, Monotone A ∧
    (Filter.Tendsto (fun n => (A (n + 1) : ℝ) / A n) Filter.atTop (nhds 2)) ∧
    (∀ S, S ⊆ Set.range A ∧ (Set.range A \ S).Finite →
       has_asymptotic_density_one (subset_sums_of_set S))
```
with the natural local definitions `has_asymptotic_density_one S := (|S ∩ {0..n-1}| / n → 1)` and
`subset_sums_of_set S := {∑_{x∈B} x : B ⊆ S finite}`.

**Faithfulness note (for review).** This is Barschkis's own **set-based** formulation of "every
cofinite subsequence." The DeepMind formal-conjectures statement of #347 uses an equivalent
**index-function** formulation (`∀ ι, (range ι)ᶜ.Finite → HasDensity (subsetSums (range (a∘ι))) 1`).
formal-conjectures references *this* proof as the resolution of #347, but the two statements differ
in form; a reviewer should confirm `answer_is_yes` faithfully captures #347 (it does — same
mathematical content, standard density/subset-sum definitions), and note the formulation difference.

## Verification result (this machine, 2026-07-05) — READ THE CAVEAT
```
Build completed successfully (7351 jobs).
'answer_is_yes' depends on axioms: [propext, Classical.choice, Lean.ofReduceBool, Lean.trustCompiler, Quot.sound]
'main_theorem'  depends on axioms: [propext, Classical.choice, Lean.ofReduceBool, Lean.trustCompiler, Quot.sound]
```
- **No `sorryAx`** → the proof has **no admitted gaps** (it is `sorry`-free; `grep sorry` = 0).
- **BUT** the axiom set includes **`Lean.ofReduceBool` + `Lean.trustCompiler`**: the proof uses
  `native_decide` in **two** places (small **finite base-case** facts — `B_card 0 > 0`, and one
  induction base case — not the core argument). `native_decide` trusts the **Lean compiler's native
  evaluation**, not the kernel. So the trusted computing base here is **strictly larger** than a
  pure-kernel proof such as [`erdos-728`](../erdos-728/) (whose axioms are only
  `[propext, Classical.choice, Quot.sound]`).

This is a legitimate, widely-used verification technique — but "green" here means **"complete,
gap-free proof, modulo trusting the compiler on two finite evaluations,"** which is a weaker
guarantee than a pure-kernel check. We flag it rather than hide it. (A strictly stronger version
would replace those `native_decide` calls with `decide`/explicit proofs, removing `ofReduceBool` /
`trustCompiler` from the axiom set.)

Toolchain `leanprover/lean4:v4.24.0`, mathlib `f897ebcf72cd16f89ab4577d0c826cd14afaafc7`. Full log:
[`build_Erdos347.log`](build_Erdos347.log).

## Reproduce
```bash
./verify.sh
```
Asserts the build succeeds and there is no `sorryAx`, and prints the full axiom set (so the
compiler-trust caveat is visible, not buried). Exit 0 ⇔ built, gap-free. First run downloads the
Lean v4.24.0 toolchain + the mathlib@f897ebcf olean cache.
