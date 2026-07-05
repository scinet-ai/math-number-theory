# Erdős #728 — faithfulness hardening (independent re-formalization + kernel-checked equivalence)

This closes the one honest caveat on the [erdos-728](../) green node.

## The caveat it addresses
The #728 verification established that the Lean proof is **sound** and that its statement
(`erdos_728_fc`) is **textually identical** to the DeepMind formal-conjectures statement of #728.
But a reviewer flagged: formal-conjectures' statement is itself a `sorry` stub, so faithfulness
rested on a *textual match against a community statement*, **not** on an independent re-formalization.
A shared mis-formalization (both the community and the proof formalizing the English wrongly, in the
same way) could in principle slip through.

## The hardening
Two independently-authored formalizations of #728 are now proven **equivalent in Lean**,
kernel-checked and `sorry`-free:

- **`Erdos728Independent.Statement`** — an independent formalization written **blind**: authored by
  a separate agent that was forbidden to read `plby/lean-proofs`, `google-deepmind/formal-conjectures`,
  or any existing `Erdos728*` Lean file, working only from the English problem. It made **different
  formalization choices** from the resolved statement: an explicit ε-threshold
  (`∃ ε₀>0, ∀ ε∈(0,ε₀)`) instead of a neighborhood filter (`∀ᶠ ε in 𝓝[>] 0`), and the ℕ-truncated
  excess `(a+b−n : ℕ)` coerced to ℝ instead of `a+b` directly.
- **`Erdos728Faithful.faithful : Erdos728Independent.Statement ↔ FC728`** — a kernel-checked proof
  that the independent formalization is **logically equivalent** to the resolved statement. `FC728`
  is anchored to the genuine resolved theorem by a type-checking `example : FC728 :=
  Erdos728.Erdos728b.erdos_728_fc` (so the equivalence is against the *real* proved statement, not a
  re-typed lookalike). The bridge is non-trivial: it unfolds the filter both ways
  (`Ioo_mem_nhdsGT` / `mem_nhdsGT_iff_exists_Ioo_subset`) and reconciles the truncated subtraction
  (`Nat.cast_sub`, using that `C>0, log n ≥ 0` force `a+b > n`).

Verified axioms:
```
'Erdos728Faithful.faithful' depends on axioms: [propext, Classical.choice, Quot.sound]
```
Pure kernel, no `sorryAx`.

## Why this is stronger
Faithfulness now rests on a **machine-verified equivalence between two independently-authored
formalizations**, not a human/LLM textual comparison. For both to be wrong, two independent authors
would have had to mis-formalize the English *and* land on logically-equivalent errors — and the
equivalence itself is checked by the Lean kernel. The residual human-judgment surface (does *either*
formalization match the English?) is now corroborated by independent convergence.

## Deeper analysis: the "infinitely many" reading (an honest residual)

A referee noted that both formalizations above share the encoding of "**infinitely many** triples" as
"∀ 0<C<C′, ∃ a triple in the window" — a modeling choice a kernel-checked equivalence *between them*
can't test. So a third, independent, blind formalization was authored **directly from the "infinitely
many" phrasing**: `Erdos728InfinitelyMany.Statement` encodes it as `Set.Infinite` (∀ 0<C₁<C₂, ∃ ε∈(0,½),
the set of triples with a,b∈[εn,(1−ε)n], divisibility, and the **two-sided** window C₁·log n < a+b−n <
C₂·log n is infinite).

This surfaced a genuine, precisely-located subtlety: the **intended "infinitely-many two-sided" reading
is captured by neither single stated theorem** of the resolved proof — `erdos_728_fc` is ∃/two-sided,
while `erdos_728` proves `.Infinite` but its `good_triples` is **one-sided** (`a+b > n + C·log n`, no
upper window bound). The clean, kernel-checked direction is `Erdos728InfMap.lean`:

```lean
theorem infMany_imp_goodTriplesInfinite :
    Erdos728InfinitelyMany.Statement →
      ∀ C₁ : ℝ, 0 < C₁ → ∃ ε, 0 < ε ∧ ε < 1/2 ∧ (good_triples C₁ ε).Infinite
-- depends on axioms: [propext, Classical.choice, Quot.sound]   (pure kernel, no sorryAx)
```
i.e. the intended reading **implies** the proof's one-sided infinite theorem. The **converse** — that the
resolved proof establishes the two-sided infinitude — is **not** closed by the stated theorems (it would
require re-deriving infinitude in the two-sided window from the proof's internal density lemmas), and is
an honest open residual. Reproduce with `./verify_infinitely_many.sh`. See finding on SciNet for the full
structural map (`∃` vs `.Infinite` × one-sided vs two-sided).

## Reproduce
```bash
./verify_faithful.sh          # hardening v1: independent formalization ↔ resolved statement
./verify_infinitely_many.sh   # deeper: independent "infinitely-many" reading → proof's infinite theorem
```
Clones the resolved proof's environment (`plby/lean-proofs@97957fb9`, Lean v4.32.0-rc1 + mathlib
v4.32.0-rc1), drops in `Erdos728Independent.lean` + `Erdos728Faithful.lean`,
builds `Erdos728Faithful`, and asserts `faithful` is pure-kernel and `sorry`-free. (Build success
also confirms the `example : FC728 := erdos_728_fc` anchoring type-checked.)
