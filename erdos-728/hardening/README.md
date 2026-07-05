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

## Reproduce
```bash
./verify_faithful.sh
```
Clones the resolved proof's environment (`plby/lean-proofs@97957fb9`, Lean v4.32.0-rc1 + mathlib
v4.32.0-rc1), drops in `Erdos728Independent.lean` + `Erdos728Faithful.lean`,
builds `Erdos728Faithful`, and asserts `faithful` is pure-kernel and `sorry`-free. (Build success
also confirms the `example : FC728 := erdos_728_fc` anchoring type-checked.)
