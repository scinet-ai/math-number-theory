/-
Let $\varepsilon$ be sufficiently small and $C, C' > 0$. Are there integers $a, b, n$ such that
$$a, b > \varepsilon n\quad a!\, b! \mid n!\, (a + b - n)!, $$
and
$$C \log n < a + b - n < C' \log n ?$$
Note that the website currently displays a simpler (trivial) version of this problem because
$a + b$ isn't assumed to be in the $n + O(\log n)$ regime.
-/
theorem erdos_728_fc :
    ∀ᶠ ε : ℝ in 𝓝[>] 0, ∀ C > (0 : ℝ), ∀ C' > C,
      ∃ a b n : ℕ,
        0 < n ∧
        ε * n < a ∧
        ε * n < b ∧
        a ! * b ! ∣ n ! * (a + b - n)! ∧
        a + b > n + C * log n ∧
        a + b < n + C' * log n := by
