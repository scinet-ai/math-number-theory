#!/usr/bin/env python3
"""
Direct verification of every upper-bound witness in the f(n) table (Erdős #963).
Uses ONLY the definition: B dissociated iff all 2^|B| subset sums distinct.
No linear algebra, no patterns. Exact integer arithmetic.

Verifies:
  1. h-witnesses: md([1..m]) values for m = 1..13.
  2. f-witnesses: explicit n-element sets achieving the claimed f(n), n = 1..25.
  3. The claimed f-table entry equals the witness md (upper bound side).
Exits nonzero on any mismatch.
"""
from itertools import combinations

def is_dissociated(B):
    sums = set()
    for mask in range(1 << len(B)):
        s = sum(B[i] for i in range(len(B)) if mask >> i & 1)
        if s in sums:
            return False
        sums.add(s)
    return True

def md(A):
    A = list(A)
    best = 0
    for size in range(1, len(A) + 1):
        if any(is_dissociated(B) for B in combinations(A, size)):
            best = size
        else:
            break   # subsets of dissociated sets are dissociated => monotone
    return best

U13 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 15]   # md = 4 (found by falsifier.py probe)

def f_witness(n):
    """Extremal construction from the reduction theorem: 0, sign-pairs, and a
    class set U of size m = ceil((n-1)/2) with md(U) = h(m):
    U = {1..m} for m <= 12, U = U13 for m = 13."""
    if n == 1:
        return [0]
    m = (n - 1 + 1) // 2  # ceil((n-1)/2)
    U = list(range(1, m + 1)) if m <= 12 else U13
    assert len(U) == m
    p = n - 1 - m
    A = [0]
    for u in U[:p]:
        A += [u, -u]
    A += U[p:]
    assert len(A) == n and len(set(A)) == n
    return A

CLAIMED_F = {1:0, 2:1, 3:1, 4:2, 5:2, 6:2, 7:2, 8:3, 9:3, 10:3, 11:3, 12:3,
             13:3, 14:4, 15:4, 16:4, 17:4, 18:4, 19:4, 20:4, 21:4, 22:4,
             23:4, 24:4, 25:4, 26:4, 27:4}
CLAIMED_H = {1:1, 2:2, 3:2, 4:3, 5:3, 6:3, 7:4, 8:4, 9:4, 10:4, 11:4, 12:4}

def main():
    ok = True
    print("interval class-sets [1..m]:")
    for m_ in range(1, 14):
        v = md(list(range(1, m_ + 1)))
        flag = ''
        if m_ in CLAIMED_H:
            if v != CLAIMED_H[m_]:
                ok = False
                flag = '  MISMATCH!'
            else:
                flag = f'  == claimed h({m_}) upper bound'
        print(f"  md([1..{m_}]) = {v}{flag}", flush=True)

    print(f"special 13-class set: md({U13}) = {md(U13)} (claimed 4)")
    if md(U13) != 4:
        ok = False

    print("f-witnesses:")
    for n in range(1, 28):
        A = f_witness(n)
        v = md(A)
        good = (v == CLAIMED_F[n])
        ok = ok and good
        print(f"  n={n:2d}  md({A}) = {v}  claimed f({n}) = {CLAIMED_F[n]}"
              f"  {'OK' if good else 'MISMATCH!'}", flush=True)

    print("ALL WITNESS CHECKS PASSED" if ok else "WITNESS CHECK FAILURES")
    raise SystemExit(0 if ok else 1)

if __name__ == '__main__':
    main()
