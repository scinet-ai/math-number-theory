#!/usr/bin/env python3
"""
Exact small-n values of f(n) for Erdős #963.

f(n) = largest k such that EVERY n-element set A of reals contains a dissociated
subset (all 2^|B| subset sums distinct) of size k.

Framework
---------
A set A = (a_1,...,a_d) of d distinct reals is modeled by its coincidence pattern
    N(A) = { eps in {-1,0,1}^d : sum eps_i a_i = 0 }.
B = {a_i : i in S} is dissociated  <=>  no nonzero eps in N(A) with supp(eps) ⊆ S.
N(A) = V ∩ {-1,0,1}^d for V = Q-span(N(A)); conversely every Q-subspace V spanned
by ternary vectors and avoiding the relevant "degeneracy" ternary vectors is
realized exactly by some integer point A in V-perp (generic point argument;
realization verified explicitly by the code, so nothing is taken on faith).

Two modes:
  mode 'f' (dimension n, direct):    forbidden in V: e_i - e_j (i<j)   [distinct entries]
  mode 'h' (dimension m, reduced):   forbidden: e_i, e_i - e_j, e_i + e_j
       [nonzero, distinct, no sign-pairs]  -- h(m) = min over such A of maxdiss(A),
       and THEOREM (proof_reduction.md): f(n) = h(ceil((n-1)/2)).

Certification of a lower bound h(m) >= k (resp. f(n) >= k):
  Show NO valid subspace V "covers" all k-subsets of coordinates, where S is
  covered iff V contains a nonzero ternary vector supported inside S.
  (maxdiss(V) <= k-1  <=>  every k-subset covered.)
  Exhaustive DFS over valid subspaces, directed by the first uncovered k-subset;
  completeness: if an adversary V* exists, every DFS node V ⊆ V* has its first
  uncovered S covered by some ternary w* in V* \ V with supp ⊆ S, and the DFS
  branches over all such w*, so it reaches a subspace of V* covering everything.
  Root symmetry: signed coordinate permutations preserve validity and coverage,
  so WLOG the first added vector is a canonical representative (all +1 entries,
  support an initial segment of the first k-subset); reps of support size 1,2
  included when the mode allows them.

Upper bounds: explicit integer witness sets, verified by direct subset-sum
enumeration (independent semantics, no linear algebra).
"""
from fractions import Fraction
from itertools import combinations, product
import argparse, json, random, sys, time

sys.setrecursionlimit(100000)

# ---------------------------------------------------------------- linear algebra
#
# Fast engine: arithmetic over GF(p), p = 2^31 - 1 (Mersenne prime M31).
# SOUNDNESS: every matrix handled here has <= 10 columns and rows that are
# ternary vectors; by Hadamard's inequality every minor determinant has
# absolute value <= 10^5 = 100000, so every numerator/denominator of any entry
# appearing in exact rational RREF / residuals (which are ratios of such
# minors, by Cramer) is a nonzero integer of absolute value < 4096 << p.
# A nonzero rational a/b with |a|,|b| < p is nonzero mod p, and reductions
# never divide by a multiple of p.  Hence membership tests, ranks, and RREF
# canonical forms over GF(p) coincide exactly with those over Q for all
# inputs arising in this program.  (Cross-checked against the exact
# Fraction engine SpanQ in verify_independent.py.)

P = (1 << 31) - 1

class Span:
    """Row space over GF(p) in RREF (exact for our inputs, see note above)."""
    __slots__ = ('rows', 'pivots')

    def __init__(self, rows=(), pivots=()):
        self.rows = tuple(rows)      # tuple of tuple[int mod P]
        self.pivots = tuple(pivots)

    def rank(self):
        return len(self.rows)

    def reduce(self, v):
        v = [x % P for x in v]
        for row, p in zip(self.rows, self.pivots):
            c = v[p]
            if c:
                v = [(a - c * b) % P for a, b in zip(v, row)]
        return v

    def contains(self, v):
        return not any(self.reduce(v))

    def extended(self, v):
        r = self.reduce(v)
        piv = next((j for j, x in enumerate(r) if x), None)
        if piv is None:
            return None
        inv = pow(r[piv], P - 2, P)
        r = tuple((x * inv) % P for x in r)
        rows, pivs = [], []
        for row, p in zip(self.rows, self.pivots):
            c = row[piv]
            if c:
                row = tuple((a - c * b) % P for a, b in zip(row, r))
            rows.append(row)
            pivs.append(p)
        idx = 0
        while idx < len(pivs) and pivs[idx] < piv:
            idx += 1
        rows.insert(idx, r)
        pivs.insert(idx, piv)
        return Span(rows, pivs)

    def key(self):
        return self.rows


class SpanQ:
    """Exact Q-subspace in RREF (used for witness realization + cross-checks)."""
    __slots__ = ('rows', 'pivots')

    def __init__(self, rows=(), pivots=()):
        self.rows = tuple(rows)      # tuple of tuple[Fraction]
        self.pivots = tuple(pivots)  # pivot column of each row, strictly increasing

    def rank(self):
        return len(self.rows)

    def reduce(self, v):
        v = [Fraction(x) for x in v]
        for row, p in zip(self.rows, self.pivots):
            c = v[p]
            if c:
                v = [a - c * b for a, b in zip(v, row)]
        return v

    def contains(self, v):
        return all(x == 0 for x in self.reduce(v))

    def extended(self, v):
        """Span of self + v, or None if v already in span."""
        r = self.reduce(v)
        piv = next((j for j, x in enumerate(r) if x != 0), None)
        if piv is None:
            return None
        inv = r[piv]
        r = tuple(x / inv for x in r)
        rows, pivs = [], []
        for row, p in zip(self.rows, self.pivots):
            c = row[piv]
            if c:
                row = tuple(a - c * b for a, b in zip(row, r))
            rows.append(row)
            pivs.append(p)
        idx = 0
        while idx < len(pivs) and pivs[idx] < piv:
            idx += 1
        rows.insert(idx, r)
        pivs.insert(idx, piv)
        return SpanQ(rows, pivs)

    def key(self):
        return self.rows  # RREF is a canonical representation of the row space


# ---------------------------------------------------------------- ternary vectors

def support(v):
    return tuple(i for i, x in enumerate(v) if x)

def ternary_on(coords, dim, min_supp):
    """Sign-normalized (first nonzero = +1) nonzero ternary vectors with
    support ⊆ coords and |support| >= min_supp, embedded in R^dim."""
    out = []
    coords = list(coords)
    for pat in product((-1, 0, 1), repeat=len(coords)):
        supp = [i for i, x in enumerate(pat) if x]
        if len(supp) < max(1, min_supp):
            continue
        if pat[supp[0]] != 1:
            continue
        v = [0] * dim
        for c, x in zip(coords, pat):
            v[c] = x
        out.append(tuple(v))
    return out

def forbidden_vectors(dim, mode):
    forb = []
    if mode == 'h':
        for i in range(dim):
            e = [0] * dim
            e[i] = 1
            forb.append(tuple(e))
    for i, j in combinations(range(dim), 2):
        v = [0] * dim; v[i] = 1; v[j] = -1
        forb.append(tuple(v))
        if mode == 'h':
            w = [0] * dim; w[i] = 1; w[j] = 1
            forb.append(tuple(w))
    return forb


# ---------------------------------------------------------------- refutation search

def refute_or_find(dim, k, mode, verbose=True):
    """Try to find a valid subspace V (mode-dependent constraints) such that every
    k-subset of coordinates supports a nonzero ternary vector of V
    (i.e. maxdiss <= k-1).  Returns (span or None, stats).
    None => PROOF that min over valid A of maxdiss(A) >= k."""
    t0 = time.time()
    forb = forbidden_vectors(dim, mode)
    forbset = set(forb)
    min_supp = 3 if mode == 'h' else 1
    subsets = list(combinations(range(dim), k))
    cand = {}
    for S in subsets:
        cand[S] = [v for v in ternary_on(S, dim, min_supp) if v not in forbset]

    seen = set()
    stats = {'nodes': 0}

    def valid_ext(sp):
        if sp.rank() >= dim:
            return False  # full space contains forbidden vectors always (dim>=1)
        for f in forb:
            if sp.contains(f):
                return False
        return True

    progress_every = 200000

    def dfs(sp, gens, uncovered):
        key = sp.key()
        if key in seen:
            return None
        seen.add(key)
        stats['nodes'] += 1
        if verbose and stats['nodes'] % progress_every == 0:
            print(f"  ... nodes={stats['nodes']} elapsed={round(time.time()-t0,1)}s",
                  flush=True)
        unc = [S for S in uncovered
               if not any(sp.contains(v) for v in cand[S])]
        if not unc:
            return gens
        S = unc[0]
        for w in cand[S]:
            sp2 = sp.extended(w)
            if sp2 is None:
                continue
            if not valid_ext(sp2):
                continue
            r = dfs(sp2, gens + [w], unc)
            if r is not None:
                return r
        return None

    # Root symmetry: canonical representatives of the first added vector.
    # Any adversary covers S0 = (0..k-1) by some ternary w, |supp w| = s in
    # [min_supp..k].
    # h-mode: the constraint list {e_i, e_i±e_j} is invariant under ALL signed
    #   permutations, so w can be mapped to all-ones on an initial segment.
    # f-mode: the constraint list {e_i - e_j} is NOT invariant under sign flips
    #   (flip of j maps e_i - e_j to e_i + e_j, which is allowed in f-mode), so
    #   only plain permutations and global negation (trivial on spans) may be
    #   used: canonical reps are +1^(s-j) (-1)^j on an initial segment, for each
    #   j <= floor(s/2) (one of ±w has <= s/2 minus signs; permute minuses last).
    root = Span()
    reps = []
    for s in range(max(1, min_supp), k + 1):
        max_minus = 0 if mode == 'h' else s // 2
        for jminus in range(0, max_minus + 1):
            v = [0] * dim
            for i in range(s):
                v[i] = -1 if i >= s - jminus else 1
            v = tuple(v)
            if v not in forbset:
                reps.append(v)
    result = None
    for v0 in reps:
        sp1 = root.extended(v0)
        if sp1 is None or not valid_ext(sp1):
            continue
        result = dfs(sp1, [v0], subsets)
        if result is not None:
            break
    stats['seconds'] = round(time.time() - t0, 2)
    stats['root_reps'] = [list(v) for v in reps]
    if verbose:
        print(f"[{mode}-mode dim={dim} k={k}] "
              f"{'ADVERSARY FOUND' if result is not None else 'REFUTED (lower bound proved)'} "
              f"nodes={stats['nodes']} time={stats['seconds']}s", flush=True)
    return result, stats


# ---------------------------------------------------------------- full enumeration

def enumerate_all(dim, mode, verbose=True):
    """Enumerate ALL valid subspaces; return (min maxdiss, extremal span, count)."""
    t0 = time.time()
    forb = forbidden_vectors(dim, mode)
    forbset = set(forb)
    min_supp = 3 if mode == 'h' else 1
    gens = [v for v in ternary_on(range(dim), dim, min_supp) if v not in forbset]
    all_tern = ternary_on(range(dim), dim, 1)  # for maxdiss computation

    def maxdiss_of(sp):
        supports = set()
        for v in all_tern:
            if sp.contains(v):
                supports.add(frozenset(support(v)))
        for size in range(dim, 0, -1):
            for S in combinations(range(dim), size):
                Sf = set(S)
                if not any(s <= Sf for s in supports):
                    return size
        return 0

    def valid_ext(sp):
        if sp.rank() >= dim:
            return False
        return not any(sp.contains(f) for f in forb)

    seen = set()
    best = [dim + 1, None]
    count = [0]

    def dfs(sp, gl):
        key = sp.key()
        if key in seen:
            return
        seen.add(key)
        count[0] += 1
        md = maxdiss_of(sp)
        if md < best[0]:
            best[0] = md
            best[1] = list(gl)
        for w in gens:
            sp2 = sp.extended(w)
            if sp2 is None:
                continue
            if not valid_ext(sp2):
                continue
            dfs(sp2, gl + [w])

    root = Span()
    dfs(root, [])
    dt = round(time.time() - t0, 2)
    if verbose:
        print(f"[enumerate {mode}-mode dim={dim}] min maxdiss = {best[0]} "
              f"over {count[0]} valid subspaces, time={dt}s", flush=True)
    return best[0], best[1], count[0], dt


# ---------------------------------------------------------------- realization

def realize_integer_point(gens, dim, mode, seed=12345, R=400, tries=20000):
    """Given ternary generators of a subspace V, find an integer point A in
    V-perp whose ternary coincidence pattern is EXACTLY V ∩ {-1,0,1}^dim and
    which satisfies the mode constraints. Exact rational arithmetic throughout.
    Returns list of ints or None."""
    rng = random.Random(seed)
    sp = SpanQ()
    for g in gens:
        sp2 = sp.extended(g)
        if sp2 is not None:
            sp = sp2
    piv = set(sp.pivots)
    free = [j for j in range(dim) if j not in piv]
    # nullspace basis: for each free var j, vector with x_j = 1, x_p = -row[j]
    nsbasis = []
    for j in free:
        vec = [Fraction(0)] * dim
        vec[j] = Fraction(1)
        for row, p in zip(sp.rows, sp.pivots):
            vec[p] = -row[j]
        nsbasis.append(vec)
    if not nsbasis:
        return None
    all_tern = ternary_on(range(dim), dim, 1)
    in_span = [sp.contains(v) for v in all_tern]
    for _ in range(tries):
        coeffs = [rng.randint(-R, R) for _ in nsbasis]
        A = [sum(c * b[i] for c, b in zip(coeffs, nsbasis)) for i in range(dim)]
        # clear denominators
        from math import lcm
        L = 1
        for x in A:
            L = lcm(L, x.denominator)
        A = [int(x * L) for x in A]
        ok = True
        for v, ins in zip(all_tern, in_span):
            d = sum(vi * ai for vi, ai in zip(v, A))
            if ins:
                assert d == 0, "span vector not orthogonal -- bug"
            elif d == 0:
                ok = False
                break
        if not ok:
            continue
        # mode constraints (should follow from validity, but verify concretely)
        if len(set(A)) != dim:
            ok = False
        if mode == 'h':
            if any(a == 0 for a in A):
                ok = False
            if any(A[i] + A[j] == 0 for i in range(dim) for j in range(i + 1, dim)):
                ok = False
        if ok:
            return A
    return None


# ---------------------------------------------------------------- direct semantics

def is_dissociated(B):
    """Direct definition: all 2^|B| subset sums distinct."""
    sums = set()
    for mask in range(1 << len(B)):
        s = 0
        m = mask
        i = 0
        while m:
            if m & 1:
                s += B[i]
            m >>= 1
            i += 1
        if s in sums:
            return False
        sums.add(s)
    return True

def maxdiss_direct(A, cap=None):
    """Largest dissociated subset, by direct subset-sum enumeration.
    Uses the fact that subsets of dissociated sets are dissociated:
    increase size until no dissociated subset of that size exists."""
    A = list(A)
    n = len(A)
    best = 0
    top = n if cap is None else min(cap, n)
    for size in range(1, top + 1):
        found = False
        for B in combinations(A, size):
            if is_dissociated(B):
                found = True
                break
        if not found:
            return best
        best = size
    return best


# ---------------------------------------------------------------- drivers

def cmd_h_exact(args):
    for m in args.dims:
        md, gens, cnt, dt = enumerate_all(m, 'h')
        if gens:
            A = realize_integer_point(gens, m, 'h')
            print(f"  h({m}) = {md}; extremal pattern gens {gens}; witness A = {A}")
            if A:
                dd = maxdiss_direct(A)
                print(f"  direct maxdiss check of witness: {dd} (must equal {md})")
                assert dd == md
        else:
            print(f"  h({m}) = {md} (trivial pattern)")

def cmd_refute(args):
    gens, stats = refute_or_find(args.dim, args.k, args.mode)
    if gens is not None:
        A = realize_integer_point(gens, args.dim, args.mode)
        print(f"  adversary gens {gens}; realized witness A = {A}")
        if A:
            dd = maxdiss_direct(A)
            print(f"  direct maxdiss of witness: {dd} (claim: <= {args.k - 1})")
            assert dd <= args.k - 1
    print(json.dumps(stats))

def cmd_witness(args):
    A = [int(x) for x in args.set.split(',')]
    print(f"maxdiss_direct({A}) = {maxdiss_direct(A)}")

def cmd_intervals(args):
    for m in range(1, args.upto + 1):
        A = list(range(1, m + 1))
        print(f"maxdiss([1..{m}]) = {maxdiss_direct(A)}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('h-exact'); p.add_argument('dims', nargs='+', type=int); p.set_defaults(func=cmd_h_exact)
    p = sub.add_parser('refute'); p.add_argument('mode', choices=['h', 'f'])
    p.add_argument('dim', type=int); p.add_argument('k', type=int); p.set_defaults(func=cmd_refute)
    p = sub.add_parser('witness'); p.add_argument('set'); p.set_defaults(func=cmd_witness)
    p = sub.add_parser('intervals'); p.add_argument('upto', type=int); p.set_defaults(func=cmd_intervals)
    args = ap.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
