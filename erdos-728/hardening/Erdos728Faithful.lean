import Mathlib
import ErdosProblems.Erdos728
import ErdosProblems.Erdos728Independent
open Real
open scoped Nat Topology
namespace Erdos728Faithful

-- Transcribe the resolved statement as a def, and CONFIRM it is exactly erdos_728_fc's type:
def FC728 : Prop :=
  ∀ᶠ ε : ℝ in 𝓝[>] 0, ∀ C > (0 : ℝ), ∀ C' > C,
    ∃ a b n : ℕ, 0 < n ∧ ε * n < a ∧ ε * n < b ∧
      a ! * b ! ∣ n ! * (a + b - n)! ∧
      a + b > n + C * Real.log n ∧ a + b < n + C' * Real.log n

example : FC728 := Erdos728.Erdos728b.erdos_728_fc   -- anchors FC728 to the real theorem

theorem faithful : Erdos728Independent.Statement ↔ FC728 := by
  unfold FC728 Erdos728Independent.Statement
  constructor
  · -- Statement → FC728
    rintro ⟨ε₀, hε₀, H⟩
    refine Filter.eventually_of_mem (Ioo_mem_nhdsGT hε₀) ?_
    rintro ε ⟨hεpos, hεlt⟩ C hC C' hC'
    obtain ⟨a, b, n, ha, hb, hn, han, hbn, hdvd, hlo, hhi⟩ := H ε hεpos hεlt C C' hC hC'
    have hlog : 0 ≤ Real.log (n : ℝ) := Real.log_nonneg (by exact_mod_cast hn)
    -- the excess condition forces n ≤ a + b (else `a + b - n = 0` contradicts `C·log n < 0`)
    have hle : n ≤ a + b := by
      rcases Nat.lt_or_ge (a + b) n with h | h
      · exfalso
        rw [Nat.sub_eq_zero_of_le h.le, Nat.cast_zero] at hlo
        linarith [mul_nonneg hC.le hlog]
      · exact h
    rw [Nat.cast_sub hle] at hlo hhi
    push_cast at hlo hhi
    refine ⟨a, b, n, hn, han, hbn, hdvd, ?_, ?_⟩
    · linarith
    · linarith
  · -- FC728 → Statement
    intro hfc
    rw [Filter.eventually_iff] at hfc
    obtain ⟨ε₀, hε₀, hsub⟩ := mem_nhdsGT_iff_exists_Ioo_subset.1 hfc
    refine ⟨ε₀, hε₀, ?_⟩
    intro ε hεpos hεlt C C' hC hC'
    have hmem : ε ∈ Set.Ioo (0 : ℝ) ε₀ := ⟨hεpos, hεlt⟩
    have hp := hsub hmem
    simp only [Set.mem_setOf_eq] at hp
    obtain ⟨a, b, n, hn, han, hbn, hdvd, hlo, hhi⟩ := hp C hC C' hC'
    have hnR : (0 : ℝ) < (n : ℝ) := by exact_mod_cast hn
    -- positivity of a, b from `ε·n < a`, `ε·n < b`, `ε > 0`, `n > 0`
    have ha : 0 < a := by
      have : (0 : ℝ) < (a : ℝ) := lt_trans (mul_pos hεpos hnR) han
      exact_mod_cast this
    have hb : 0 < b := by
      have : (0 : ℝ) < (b : ℝ) := lt_trans (mul_pos hεpos hnR) hbn
      exact_mod_cast this
    have hlog : 0 ≤ Real.log (n : ℝ) := Real.log_nonneg (by exact_mod_cast hn)
    have hle : n ≤ a + b := by
      have h1 : (n : ℝ) < (a : ℝ) + (b : ℝ) := by linarith [mul_nonneg hC.le hlog]
      exact_mod_cast h1.le
    refine ⟨a, b, n, ha, hb, hn, han, hbn, hdvd, ?_, ?_⟩
    · rw [Nat.cast_sub hle]; push_cast; linarith
    · rw [Nat.cast_sub hle]; push_cast; linarith

#print axioms faithful
end Erdos728Faithful
