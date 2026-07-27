"""Core library for the Erdos #169 f(4) record attack.

Definitions (following Walker, arXiv:2203.06045v2):
  - K(S, b): the Kempner set of all non-negative integers whose base-b digits
    all lie in S (subset of [0, b-1], with 0 in S).  Note 0 is in K(S, b).
  - A set S in [0, b-1] is "k-free mod b" if there is NO ordinary arithmetic
    progression of length k with common difference not divisible by b whose
    reduction mod b lands inside S.  Equivalently: for every residue a and
    every difference d in [1, b-1], the k residues (a + j*d) mod b, j=0..k-1,
    are not all contained in S.
  - Walker's Theorem 1.2: if S is k-free mod b and 0 in S, then K(S, b)
    contains no k-term arithmetic progression.
  - The quantity of record is the harmonic sum of the shifted set,
        H(K(S,b) + 1) = sum_{n in K(S,b)} 1/(n+1),
    a lower bound for M_k = f(k) when K(S,b) is k-free.

All record-relevant numerics here are CERTIFIED: harmonic sums are returned
as (lower, upper) enclosures computed with exact integer floor divisions and
exact Fraction arithmetic for tail bounds.  No floating point enters the
certified path.
"""

from fractions import Fraction
import numpy as np

SCALE = 2 ** 62  # fixed-point scale for exact reciprocal-sum bounds


# ---------------------------------------------------------------------------
# k-AP-freeness mod b
# ---------------------------------------------------------------------------

def is_kfree_mod(S, b, k=4):
    """Exhaustive check that digit set S is k-free mod b.

    Checks every start a in [0,b) and difference d in [1,b): the k residues
    (a + j*d) mod b must never all lie in S.  O(b^2 * k) with numpy.
    """
    mask = np.zeros(b, dtype=bool)
    mask[list(S)] = True
    a = np.arange(b, dtype=np.int64)
    for d in range(1, b):
        hit = mask[a]
        for j in range(1, k):
            hit &= mask[(a + j * d) % b]
            if not hit.any():
                break
        else:
            if hit.any():
                return False
    return True


def kfree_mod_violation(S, b, k=4):
    """Return one witness (a, d) if S is NOT k-free mod b, else None."""
    mask = np.zeros(b, dtype=bool)
    mask[list(S)] = True
    a = np.arange(b, dtype=np.int64)
    for d in range(1, b):
        hit = mask[a]
        for j in range(1, k):
            hit &= mask[(a + j * d) % b]
        if hit.any():
            return int(a[hit][0]), d
    return None


def addable_digits(S, b, k=4):
    """Digits c not in S such that S + {c} is still k-free mod b.

    Assumes S itself is k-free mod b.  Any violating progression in the
    augmented set must pass through c, so only progressions through c are
    checked.  Vectorised over the difference d.
    """
    mask = np.zeros(b, dtype=bool)
    mask[list(S)] = True
    d = np.arange(1, b, dtype=np.int64)
    out = []
    for c in range(b):
        if mask[c]:
            continue
        aug = mask.copy()
        aug[c] = True
        blocked = False
        # c occupies position t of a k-term progression c + (j - t)*d
        for t in range(k):
            offsets = [j - t for j in range(k) if j != t]
            hit = np.ones(b - 1, dtype=bool)
            for off in offsets:
                hit &= aug[(c + off * d) % b]
                if not hit.any():
                    break
            if hit.any():
                blocked = True
                break
        if not blocked:
            out.append(c)
    return out


def digit_is_addable(S_mask, b, c, k=4):
    """Fast single-candidate version of addable_digits (S_mask boolean array)."""
    if S_mask[c]:
        return False
    aug = S_mask.copy()
    aug[c] = True
    d = np.arange(1, b, dtype=np.int64)
    for t in range(k):
        offsets = [j - t for j in range(k) if j != t]
        hit = np.ones(b - 1, dtype=bool)
        for off in offsets:
            hit &= aug[(c + off * d) % b]
            if not hit.any():
                break
        if hit.any():
            return False  # adding c would create a k-term progression mod b
    return True


# ---------------------------------------------------------------------------
# Certified harmonic sums  H(K(S,b)+1) = sum_{n in K} 1/(n+1)
# ---------------------------------------------------------------------------

def _exact_recip_sums(values_iter, shift):
    """Given an iterator of uint64 numpy arrays of values v, return exact
    integer bounds L, U with  L/SCALE <= sum 1/(v+shift) <= U/SCALE.

    Uses exact numpy uint64 floor division; accumulates in Python ints.
    """
    lo = 0
    n_terms = 0
    for arr in values_iter:
        q = SCALE // (arr + shift)          # exact floor division, elementwise
        # chunked accumulation to avoid uint64 overflow in the reduction
        qmax = int(q.max()) if q.size else 0
        if qmax == 0:
            n_terms += arr.size
            continue
        chunk = max(1, (2 ** 63) // (qmax + 1))
        s = 0
        for i in range(0, q.size, chunk):
            s += int(np.sum(q[i:i + chunk], dtype=np.uint64))
        lo += s
        n_terms += arr.size
    # floor(x) <= x <= floor(x) + 1  per term
    return lo, lo + n_terms


def _digit_strings(S_sorted, b, length, lead_nonzero, chunk_digits=None):
    """Yield numpy uint64 arrays of the values of all base-b digit strings of
    the given length with digits in S (leading digit nonzero if requested).
    Chunked over the leading digit to bound memory."""
    S = np.array(S_sorted, dtype=np.uint64)
    S_lead = S[S > 0] if lead_nonzero else S
    if length == 1:
        yield S_lead.copy()
        return
    # all (length-1)-strings with unrestricted leading zeros, built iteratively
    rest = S.copy()
    for _ in range(length - 2):
        rest = (rest[:, None] * b + S[None, :]).ravel()
    for lead in S_lead:
        yield (int(lead) * (b ** np.uint64(length - 1)) + rest).astype(np.uint64)


def harmonic_sum_bounds(S, b, depth):
    """Certified enclosure (lower, upper) of H(K(S,b)+1) as Fractions.

    Head: exact fixed-point bounds over all members with at most `depth`
    base-b digits (leading digit nonzero), plus the n=0 term (value 1).
    Tail: members with more than `depth` digits are grouped by their leading
    `depth` digits p; each of the m^j extensions by j more digits has value v
    with  p*b^j <= v <= (p+1)*b^j - 1, hence
        1/((p+1) b^j)  <=  1/(v+1)  <=  1/(p b^j + 1) < 1/(p b^j).
    Summing the geometric series in j with ratio q = m/b (< 1 required):
        tail_lower = (q/(1-q)) * sum_p 1/(p+1)
        tail_upper = (q/(1-q)) * sum_p 1/p
    All sums use exact integer arithmetic at scale 2^62.
    """
    S = sorted(set(int(s) for s in S))
    assert 0 in S, "digit set must contain 0"
    assert all(0 <= s < b for s in S)
    m = len(S)
    assert m < b, "need |S| < b for convergence"

    head_lo = 0
    head_hi = 0
    for length in range(1, depth + 1):
        lo, hi = _exact_recip_sums(_digit_strings(S, b, length, True), 1)
        head_lo += lo
        head_hi += hi

    # tail over prefixes of exactly `depth` digits
    pref_lo, _ = _exact_recip_sums(_digit_strings(S, b, depth, True), 1)  # sum 1/(p+1) lower
    _, pref_hi = _exact_recip_sums(_digit_strings(S, b, depth, True), 0)  # sum 1/p upper
    ratio = Fraction(m, b - m)  # q/(1-q)

    lower = 1 + Fraction(head_lo, SCALE) + ratio * Fraction(pref_lo, SCALE)
    upper = 1 + Fraction(head_hi, SCALE) + ratio * Fraction(pref_hi, SCALE)
    return lower, upper


# ---------------------------------------------------------------------------
# Fast float evaluation for search ranking (NOT certified)
# ---------------------------------------------------------------------------

def harmonic_sum_float(S, b, depth):
    """Float64 estimate of H(K(S,b)+1) with the same head+tail structure."""
    S = sorted(set(int(s) for s in S))
    m = len(S)
    total = 1.0
    tail_pref = 0.0
    for length in range(1, depth + 1):
        for arr in _digit_strings(S, b, length, True):
            v = arr.astype(np.float64)
            total += float(np.sum(1.0 / (v + 1.0)))
            if length == depth:
                tail_pref += float(np.sum(1.0 / (v + 1.0)))  # ~ sum 1/(p+1)
    q = m / b
    total += (q / (1.0 - q)) * tail_pref
    return total


# ---------------------------------------------------------------------------
# Product construction
# ---------------------------------------------------------------------------

def product_digit_set(S1, b1, S2):
    """S1 + b1*S2 as a sorted list: digit set in base b1*b2.

    Theorem (proved in README.md): if S1 is k-free mod b1 and S2 is k-free
    mod b2, then S1 + b1*S2 is k-free mod b1*b2.
    """
    return sorted(s + b1 * t for s in S1 for t in S2)


# Walker's published sets (arXiv:2203.06045v2, Section 2 and Table 1)
WALKER_S11 = [0, 1, 2, 4, 5, 7]
WALKER_S55 = [0, 1, 2, 4, 5, 9, 10, 11, 14, 16, 17, 18, 21, 24, 30, 37,
              39, 41, 42, 45, 47]
WALKER_S22 = [0, 1, 2, 4, 5, 7, 8, 9, 14, 17]
WALKER_H55 = 4.43975   # published record for M_4
WALKER_H11 = 4.421746  # published value for K(S11, 11) + 1
