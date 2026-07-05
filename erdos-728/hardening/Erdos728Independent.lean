import Mathlib
open scoped Nat
open Real
namespace Erdos728Independent

/-- Independent formalization of Erdős #728 (intended non-trivial version).

For every sufficiently small `ε > 0` (i.e. there is a threshold `ε₀ > 0` below which the
following holds) and for all real `C, C'` with `0 < C < C'`, there exist positive integers
`a, b, n` such that
* (i)   `a > ε·n` and `b > ε·n`,
* (ii)  `a!·b!` divides `n!·(a+b−n)!`,
* (iii) `C·log n < a + b − n < C'·log n`  (natural logarithm).

Here `a + b - n` is natural-number (truncated) subtraction; condition (iii) forces
`a + b > n`, so it agrees with the honest integer excess. -/
def Statement : Prop :=
  ∃ ε₀ : ℝ, 0 < ε₀ ∧
    ∀ ε : ℝ, 0 < ε → ε < ε₀ →
      ∀ C C' : ℝ, 0 < C → C < C' →
        ∃ a b n : ℕ, 0 < a ∧ 0 < b ∧ 0 < n ∧
          -- (i) a, b each exceed ε·n
          ε * (n : ℝ) < (a : ℝ) ∧ ε * (n : ℝ) < (b : ℝ) ∧
          -- (ii) factorial divisibility
          a ! * b ! ∣ n ! * (a + b - n) ! ∧
          -- (iii) the excess a+b−n lies in the Θ(log n) window
          C * Real.log (n : ℝ) < ((a + b - n : ℕ) : ℝ) ∧
          ((a + b - n : ℕ) : ℝ) < C' * Real.log (n : ℝ)

end Erdos728Independent
