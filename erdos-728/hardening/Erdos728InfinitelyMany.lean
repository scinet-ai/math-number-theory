import Mathlib

open scoped Nat
open Real

namespace Erdos728InfinitelyMany

/-- Independent formalization of Erdős #728 in its "infinitely many triples" reading.

For every pair of reals `0 < C₁ < C₂` there are infinitely many triples of positive
integers `(a, b, n)` such that, for some fixed `ε ∈ (0, 1/2)`:
* (i)   `ε·n ≤ a ≤ (1−ε)·n` and `ε·n ≤ b ≤ (1−ε)·n`  (a, b a bounded-away fraction of n);
* (ii)  `a! · b! ∣ n! · (a + b − n)!`;
* (iii) `C₁·log n < a + b − n < C₂·log n`  (two-sided window, natural log).

Encoding notes:
* "infinitely many triples" is `{t : ℕ × ℕ × ℕ | …}.Infinite` (`Set.Infinite`);
* the fixed `ε` is `∃ ε`, chosen once for the whole infinite family;
* `a + b - n` is truncated `ℕ`-subtraction, cast to `ℝ` only afterwards, i.e.
  `((a + b - n : ℕ) : ℝ)`; the factorial `(a + b - n)!` likewise uses `ℕ`-subtraction. -/
def Statement : Prop :=
  ∀ C₁ C₂ : ℝ, 0 < C₁ → C₁ < C₂ →
    ∃ ε : ℝ, 0 < ε ∧ ε < 1 / 2 ∧
      { t : ℕ × ℕ × ℕ |
          let a := t.1; let b := t.2.1; let n := t.2.2;
          -- positive integers
          0 < a ∧ 0 < b ∧ 0 < n ∧
          -- (i) a and b are each a bounded-away (by ε) positive fraction of n
          ε * (n : ℝ) ≤ (a : ℝ) ∧ (a : ℝ) ≤ (1 - ε) * (n : ℝ) ∧
          ε * (n : ℝ) ≤ (b : ℝ) ∧ (b : ℝ) ≤ (1 - ε) * (n : ℝ) ∧
          -- (ii) a! · b!  divides  n! · (a + b − n)!
          a ! * b ! ∣ n ! * (a + b - n)! ∧
          -- (iii) two-sided window: C₁·log n < a + b − n < C₂·log n
          C₁ * Real.log (n : ℝ) < ((a + b - n : ℕ) : ℝ) ∧
          ((a + b - n : ℕ) : ℝ) < C₂ * Real.log (n : ℝ) }.Infinite

end Erdos728InfinitelyMany
