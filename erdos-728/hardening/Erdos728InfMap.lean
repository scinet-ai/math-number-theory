import Mathlib
import ErdosProblems.Erdos728
import ErdosProblems.Erdos728InfinitelyMany

open Real
open scoped Nat

namespace Erdos728InfMap

/-- The intended "infinitely many, two-sided" reading of Erdős #728 implies the resolved proof's
    (one-sided) infinite theorem's conclusion: for each `C₁ > 0` some `ε` makes `good_triples C₁ ε`
    infinite. (This is the clean provable direction; the converse is NOT captured by a single stated
    theorem of the resolved proof — `erdos_728_fc` is ∃/two-sided, `erdos_728` is infinite/one-sided.) -/
theorem infMany_imp_goodTriplesInfinite :
    Erdos728InfinitelyMany.Statement →
      ∀ C₁ : ℝ, 0 < C₁ → ∃ ε : ℝ, 0 < ε ∧ ε < 1 / 2 ∧
        (Erdos728.Erdos728b.good_triples C₁ ε).Infinite := by
  intro h C₁ hC₁
  obtain ⟨ε, hε0, hεhalf, hInf⟩ := h C₁ (C₁ + 1) hC₁ (by linarith)
  refine ⟨ε, hε0, hεhalf, Set.Infinite.mono ?_ hInf⟩
  rintro ⟨a, b, n⟩ ht
  simp only [Erdos728.Erdos728b.good_triples, Set.mem_setOf_eq] at ht ⊢
  obtain ⟨ha0, hb0, hn0, hεa, haup, hεb, hbup, hdvd, hlo, _hhi⟩ := ht
  have hlog : 0 ≤ Real.log (n : ℝ) := Real.log_nonneg (by exact_mod_cast hn0)
  have hle : n ≤ a + b := by
    rcases Nat.lt_or_ge (a + b) n with hh | hh
    · exfalso
      rw [Nat.sub_eq_zero_of_le hh.le, Nat.cast_zero] at hlo
      nlinarith [mul_nonneg hC₁.le hlog]
    · exact hh
  rw [Nat.cast_sub hle] at hlo
  push_cast at hlo
  refine ⟨hεa, haup, hεb, hbup, hdvd, ?_⟩
  push_cast
  linarith

#print axioms infMany_imp_goodTriplesInfinite

end Erdos728InfMap
