"""
Sanity + validation suite. MUST pass before any UNSAT result is trusted.

1. Verifier recognises the classic covering system {0/2,0/3,1/4,5/6,7/12}.
2. Verifier rejects a deliberately-incomplete system.
3. SAT engine and backtracking engine AGREE on many random small instances,
   and when SAT they return a genuine cover (checked by the verifier).
4. Reduction lemma (reduce_local_density) preserves coverability: on random
   small modulus sets, coverability of the FULL set == coverability of the CORE
   (both decided exhaustively). This validates the lemma the big claim rests on.
"""
import random
import numpy as np
from admissible import lcm, reduce_local_density
from cover_sat import covers, solve_sat, solve_backtrack


def test_verifier():
    classic = [(0, 2), (0, 3), (1, 4), (5, 6), (7, 12)]
    ok, bad = covers(classic)
    assert ok, f"classic system should cover, bad point {bad}"
    # drop the 7/12 class -> point 7 (and 7+12,...) uncovered
    incomplete = [(0, 2), (0, 3), (1, 4), (5, 6)]
    ok2, bad2 = covers(incomplete)
    assert not ok2 and bad2 == 7, f"expected uncovered at 7, got {ok2},{bad2}"
    print("[1,2] verifier: classic covers Z/12; incomplete fails at 7  OK")


def coverable_bruteforce(moduli):
    """Ground truth coverability via Cadical SAT over Z/lcm (fast, reliable)."""
    L = lcm(moduli)
    sat, model = solve_sat(moduli, L)
    if sat:
        ok, _ = covers(model, L)
        assert ok, "SAT returned a non-cover!"
    return sat


def test_engines_agree():
    rng = random.Random(20260706)
    small = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12]
    trials = 0
    for _ in range(120):
        k = rng.randint(2, 5)
        moduli = sorted(rng.sample(small, k))
        L = lcm(moduli)
        if L > 5000:
            continue
        s_sat, m_sat = solve_sat(moduli, L)
        s_bt, m_bt, _ = solve_backtrack(moduli, L)
        assert s_sat == s_bt, f"SAT/backtrack disagree on {moduli}: {s_sat} vs {s_bt}"
        if s_sat:
            assert covers(m_sat, L)[0] and covers(m_bt, L)[0]
        trials += 1
    print(f"[3] SAT vs backtracking agree on {trials} random instances  OK")


def test_lemma_preserves_coverability():
    """Core (after local-density removal) is coverable iff full set is."""
    rng = random.Random(1234567)
    pool = list(range(2, 25))
    trials = mismatches = removed_any = 0
    for _ in range(400):
        k = rng.randint(3, 8)
        moduli = sorted(set(rng.sample(pool, k)))
        Lf = lcm(moduli)
        if Lf > 20000:
            continue
        core, log = reduce_local_density(moduli)
        if not core:
            # empty core => lemma claims uncoverable; verify full is uncoverable
            full_cov = coverable_bruteforce(moduli)
            assert not full_cov, f"lemma emptied {moduli} but it IS coverable!"
            trials += 1
            if log:
                removed_any += 1
            continue
        full_cov = coverable_bruteforce(moduli)
        core_cov = coverable_bruteforce(core)
        if full_cov != core_cov:
            mismatches += 1
            print(f"  MISMATCH {moduli} full={full_cov} core={core}={core_cov}")
        trials += 1
        if log:
            removed_any += 1
    assert mismatches == 0, f"{mismatches} lemma mismatches!"
    print(f"[4] lemma preserves coverability on {trials} instances "
          f"({removed_any} had removals)  OK")


def test_lemma_on_admissible_slices():
    """Directly on admissible cores with small LCM: SAT confirms UNSAT and it
    matches the lemma-based prediction (core sum < 1 => uncoverable)."""
    from admissible import admissible_moduli
    for M in [100, 150, 200, 250]:
        S = admissible_moduli(M)
        core, _ = reduce_local_density(S)
        Lc = lcm(core) if core else 1
        if not core:
            print(f"  M={M}: core empty -> uncoverable (no search)")
            continue
        if Lc > 50_000:
            print(f"  M={M}: core lcm={Lc} too big for direct SAT here (skip)")
            continue
        sat, _ = solve_sat(core, Lc)
        csum = sum(1.0 / m for m in core)
        print(f"  M={M}: |core|={len(core)} lcm={Lc} sum1/m={csum:.4f} "
              f"-> SAT covering solver says {'SAT/witness!' if sat else 'UNSAT'}")
        assert not sat, f"unexpected witness for admissible core M={M}"
    print("[5] admissible cores M<=250: SAT engine confirms UNSAT  OK")


if __name__ == "__main__":
    test_verifier()
    test_engines_agree()
    test_lemma_preserves_coverability()
    test_lemma_on_admissible_slices()
    print("\nALL SANITY CHECKS PASSED")
