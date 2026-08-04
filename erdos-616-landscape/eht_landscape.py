#!/usr/bin/env python3
r"""The exact-value landscape of Erdős #616 derivable from EHT91's published
theorems, computed rigorously from their stated formulas.

From the paper (sources/EHT91.pdf; page references to JCTA 58 (1991) 78-84):

  * Theorem 3 (p.80):  (3r-3, 1) ->_r ceil(r/5)  for all r >= 3,
    i.e. t(r) <= ceil(r/5).  In the paper this is the special case
    t = ceil(r/5) of Theorem 6(I) via the check p(r, ceil(r/5)) <= 3r-3,
    where  p(r,t,m) = ceil(m/t)(r-m-t) + 2r - m,  p(r,t) = max_{1<=m<=r-1}.
    We verify that check here for all 3 <= r <= 60.

  * Lower bounds via the Section-3 construction H(r,k,q) with k = 3t+1,
    q = 2t+1 (tau = t+1): L(r) holds iff r >= r0(t) := 5t+1+floor((t-1)/3)
    (proved self-containedly in proof_t8_t11.md via the exact minimum span
    of empty-intersection subfamilies; also = EHT91 Theorem 6(II)'s bound
    p(r,t) - floor(t(t-1)/(m+2t-1)) - 1 >= 3r-3 with m = t+1).  We verify
    the two routes agree for all relevant t.

  * Also: the whole H(r,k,q) family fails at the undetermined values: for
    r = 21 and tau >= 5 (i.e. k-q >= 4) NO admissible (k,q) gives L(21).
    Exact criterion (complement form, proved in proof_t8_t11.md): writing
    d = k-q (complements are d-sets), an empty-intersection subfamily of m
    edges with |common part of complements| = i exists iff the m complements
    can cover [k] around a common i-set: i + m(d-i) >= k, 0 <= i <= d-1,
    m >= 2 (m distinct d-sets sharing an i-set: also need d > i, and
    m <= C(k-i, d-i) for realizability); its full span is k - i + m(r-q).
    L(r) holds iff all feasible (m,i) give span > 3r-3.  We minimize
    exactly over (m,i) for every q and report.

Output: the pinned values t(r) = ceil(r/5) for 3 <= r <= 20, and the list
of r <= 60 where EHT91's stated results leave t(r) undetermined
(first: r = 21, t(21) in {4,5}).
"""
from math import ceil, floor

def p_rtm(r, t, m):
    return -(-m // t) * (r - m - t) + 2*r - m

def p_rt(r, t):
    return max(p_rtm(r, t, m) for m in range(1, r))

def thm3_check(rmax=60):
    """Verify p(r, ceil(r/5)) <= 3r-3 (the stated reduction of Thm 3 to
    Thm 6(I)) for 3 <= r <= rmax."""
    for r in range(3, rmax+1):
        t = -(-r // 5)
        assert p_rt(r, t) <= 3*r - 3, f"p({r},{t}) = {p_rt(r,t)} > {3*r-3}"
    print(f"Theorem 3 reduction verified: p(r, ceil(r/5)) <= 3r-3 for 3 <= r <= {rmax}")

def r0_construction(t):
    """Threshold from the exact span analysis of H(r, 3t+1, 2t+1)."""
    return 5*t + 1 + (t - 1) // 3

def r0_thm6II(r, t):
    """Does Theorem 6(II) as stated give (3r-3,1) -/-> t (hence t(r) >= t+1)?
    Requires m = argmax of p(r,t,.) with m == 1 (mod t) (paper: the argmax
    can be taken so), bound p(r,t) - floor(t(t-1)/(m+2t-1)) - 1 >= 3r-3."""
    best = max(range(1, r), key=lambda m: (p_rtm(r, t, m), -(m % t != 1)))
    # among argmaxes prefer one with m % t == 1 (paper's normalization)
    val = p_rt(r, t)
    cands = [m for m in range(1, r) if p_rtm(r, t, m) == val and m % t == 1 % t]
    if not cands:
        return False
    m = cands[0]
    return val - (t*(t-1)) // (m + 2*t - 1) - 1 >= 3*r - 3

def lower_bound(r):
    """Best t(r) >= L from the construction thresholds (t >= 1), plus the
    trivial t(r) >= 1."""
    best = 1
    t = 1
    while r0_construction(t) <= r:
        best = t + 1
        t += 1
    return best

def h_family_min_span(r, q, d):
    """Exact minimum span of an empty-intersection subfamily of H(r, q+d, q)
    (complement criterion; d = k-q, complements are d-subsets of [k]).
    Returns None if no empty-intersection subfamily exists."""
    k = q + d
    if not (q < k < 2*q and q < r):
        return None
    best = None
    mcap = (3*r) // (r - q) + 2   # beyond this m, m(r-q) alone exceeds 3r
    from math import comb
    for m in range(2, mcap + 1):
        for i in range(0, d):
            if i + m*(d - i) < k:
                continue           # cannot cover [k] around a common i-set
            if comb(k - i, d - i) < m:
                continue           # not enough distinct d-sets sharing an i-set
            span = k - i + m*(r - q)
            if best is None or span < best:
                best = span
    return best

def check_r21_family_fails():
    """For r=21, tau >= 5 needs d = k-q >= 4; verify NO admissible (q,d)
    gives L(21) (min span > 60)."""
    r = 21
    ok_none = True
    for d in range(4, 10):
        for q in range(d + 1, r):       # k=q+d < 2q  <=>  q > d
            s = h_family_min_span(r, q, d)
            if s is None:
                continue
            if s > 3*r - 3:
                print(f"  !! H(21,{q+d},{q}) would satisfy L(21) with tau={d+1}")
                ok_none = False
    assert ok_none
    print("H(r,k,q) family exhausted at r=21: no (k,q) with k-q >= 4 satisfies "
          "L(21) => the EHT construction cannot decide t(21). OK")
    # cross-check the criterion against the Y-level exhaustive checks of
    # witness_t11.py at the certified parameters:
    for (r_, q_, d_, expect) in ((11, 5, 2, 31), (16, 7, 3, 46),
                                 (10, 5, 2, 27), (15, 7, 3, 42)):
        s = h_family_min_span(r_, q_, d_)
        assert s == expect, (r_, q_, d_, s, expect)
    print("  (complement criterion reproduces the exhaustively-computed "
          "min spans 31/46/27/42 at (r,q,d) = (11,5,2),(16,7,3),(10,5,2),(15,7,3))")

def main():
    thm3_check()
    # thresholds: construction analysis vs Theorem 6(II) as stated
    for t in range(1, 9):
        r0 = r0_construction(t)
        assert r0_thm6II(r0, t), f"Thm 6(II) fails at its own threshold r={r0}, t={t}"
        assert not r0_thm6II(r0 - 1, t), f"Thm 6(II) fires below threshold, t={t}"
    print("Thresholds r0(t) = 5t+1+floor((t-1)/3) agree with Theorem 6(II) "
          "for t = 1..8:", [r0_construction(t) for t in range(1, 9)])
    print("\n r : lower <= t(r) <= upper   (EHT91-derivable)")
    open_rs = []
    for r in range(3, 61):
        lo, up = lower_bound(r), -(-r // 5)
        status = "PINNED" if lo == up else f"OPEN {{{lo}..{up}}}"
        if lo != up:
            open_rs.append(r)
        if r <= 26 or lo != up:
            print(f" {r:2d}: {lo} <= t <= {up}   {status}")
    assert all(lower_bound(r) == -(-r // 5) for r in range(3, 21)), \
        "some r <= 20 not pinned?!"
    assert open_rs[0] == 21
    print(f"\nPinned: t(r) = ceil(r/5) for all 3 <= r <= 20.")
    print(f"Undetermined by EHT91's stated results (r <= 60): {open_rs}")
    check_r21_family_fails()
    print("\nLANDSCAPE CHECKS PASSED")

if __name__ == "__main__":
    main()
