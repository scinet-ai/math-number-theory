#!/usr/bin/env python3
"""
Independent re-implementation of the lower-bound refutation search for
Erdős #963 small-n certification.  Deliberately different from search963.py:

  * exact integer arithmetic (fraction-free row reduction, no mod-p, no Fraction)
  * iterative DFS with an explicit stack (no recursion)
  * subspace canonical key = exact Fraction-arithmetic RREF of the basis
    (rref_key below), independent of the mod-p RREF keys in search963.py
  * coverage computed from the support sets of the intersection
  * branching over candidate vectors in a different (reverse-lexicographic) order
  * optionally NO root symmetry reduction (--nosym): branch over every
    candidate vector of the first uncovered subset from the empty subspace.

Claim verified for mode 'h', dimension m, threshold k:
    NO subspace V of Q^m spanned by {-1,0,1}-vectors satisfies
      (a) V contains none of: e_i, e_i - e_j, e_i + e_j   (validity), and
      (b) every k-subset S of coordinates supports a nonzero ternary vector of V.
Equivalently: every set of m distinct nonzero reals, no two summing to zero,
has a dissociated subset of size k, i.e. h(m) >= k.
Mode 'f' drops the e_i and e_i + e_j constraints (arbitrary distinct reals):
f(n) >= k.
"""
import sys, time
from itertools import combinations, product
from math import gcd
from fractions import Fraction

def rref_key(basis):
    """Canonical key of the row space: exact reduced row echelon form over Q,
    computed with Fractions (independent of the mod-p engine in search963.py)."""
    mat = [[Fraction(x) for x in row] for row in basis]
    ncols = len(mat[0]) if mat else 0
    out = []
    r = 0
    for c in range(ncols):
        piv = None
        for i in range(r, len(mat)):
            if mat[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        mat[r], mat[piv] = mat[piv], mat[r]
        inv = mat[r][c]
        mat[r] = [x / inv for x in mat[r]]
        for i in range(len(mat)):
            if i != r and mat[i][c] != 0:
                ci = mat[i][c]
                mat[i] = [a - ci * b for a, b in zip(mat[i], mat[r])]
        r += 1
    return tuple(tuple(row) for row in mat[:r])

def row_reduce_int(rows):
    """Bring integer rows to a row-echelon form over Q using exact integer ops
    (cross-multiplication), primitive rows. Returns echelon list."""
    rows = [list(r) for r in rows if any(r)]
    ech = []
    for r in rows:
        r = reduce_by(ech, r)
        if any(r):
            g = 0
            for x in r:
                g = gcd(g, x)
            r = [x // g for x in r]
            ech.append(r)
            ech.sort(key=lambda row: next(i for i, x in enumerate(row) if x))
    return ech

def reduce_by(ech, v):
    v = list(v)
    for r in ech:
        p = next(i for i, x in enumerate(r) if x)
        if v[p]:
            a, b = r[p], v[p]
            v = [a * x - b * y for x, y in zip(v, r)]
            g = 0
            for x in v:
                g = gcd(g, x)
            if g:
                v = [x // g for x in v]
    return v

def in_span_int(ech, v):
    return not any(reduce_by(ech, v))

def run(mode, m, k, use_sym=True, verbose=True):
    t0 = time.time()
    all_tern = []
    for v in product((-1, 0, 1), repeat=m):
        supp = [i for i, x in enumerate(v) if x]
        if supp and v[supp[0]] == 1:
            all_tern.append(v)

    forb = []
    for i in range(m):
        if mode == 'h':
            forb.append(tuple(1 if j == i else 0 for j in range(m)))
    for i, j in combinations(range(m), 2):
        forb.append(tuple(1 if t == i else (-1 if t == j else 0) for t in range(m)))
        if mode == 'h':
            forb.append(tuple(1 if t == i else (1 if t == j else 0) for t in range(m)))
    forbset = set(forb)
    min_supp = 3 if mode == 'h' else 1

    subsets = list(combinations(range(m), k))
    cand = {}
    for S in subsets:
        cs = []
        for v in all_tern:
            supp = [i for i, x in enumerate(v) if x]
            if len(supp) < min_supp or not set(supp) <= set(S):
                continue
            if v in forbset:
                continue
            cs.append(v)
        cs.reverse()   # different branching order from search963.py
        cand[S] = cs

    seen = set()
    nodes = 0
    found = None

    def valid(basis):
        if len(basis) >= m:
            return False
        return not any(in_span_int(basis, f) for f in forb)

    # stack entries: (echelon basis, uncovered subsets of the parent)
    if use_sym:
        roots = []
        for s in range(max(1, min_supp), k + 1):
            v = tuple(1 if i < s else 0 for i in range(m))
            if v not in forbset:
                roots.append([list(v)])
    else:
        S0 = subsets[0]
        roots = [[list(w)] for w in cand[S0]]

    stack = [(row_reduce_int(r), subsets) for r in roots]
    stack = [(b, u) for (b, u) in stack if valid(b)]
    while stack:
        basis, uncovered = stack.pop()
        key = rref_key(basis)
        if key in seen:
            continue
        seen.add(key)
        nodes += 1
        if verbose and nodes % 20000 == 0:
            print(f"  ... nodes={nodes} elapsed={round(time.time()-t0,1)}s", flush=True)
        unc = [S for S in uncovered
               if not any(in_span_int(basis, v) for v in cand[S])]
        if not unc:
            found = basis
            break
        S = unc[0]
        for w in cand[S]:
            if in_span_int(basis, w):
                continue
            b2 = row_reduce_int(basis + [list(w)])
            if not valid(b2):
                continue
            stack.append((b2, unc))
    dt = round(time.time() - t0, 2)
    verdict = 'ADVERSARY FOUND' if found else 'REFUTED (lower bound proved)'
    print(f"[independent {mode}-mode m={m} k={k} sym={use_sym}] {verdict} "
          f"nodes={nodes} time={dt}s", flush=True)
    return found

if __name__ == '__main__':
    mode, m, k = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    use_sym = '--nosym' not in sys.argv
    r = run(mode, m, k, use_sym)
    sys.exit(2 if r else 0)
