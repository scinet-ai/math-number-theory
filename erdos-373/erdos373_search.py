#!/usr/bin/env python3
"""
Erdos #373  -- exhaustive search for nontrivial factorial-product representations of n!.

Equation:
    n! = a_1! a_2! ... a_k!    with    n-1 > a_1 >= a_2 >= ... >= a_k >= 2.

The constraint a_1 <= n-2 EXCLUDES the trivial family n! = (n-1)! * n (which occurs
whenever n itself is a product of small factorials). Every factor is a nontrivial
factorial (index >= 2, value >= 2! = 2).

Known sporadic solutions (Erdos -- only three n are known):
    9!  = 7! 3! 3! 2!
    10! = 7! 6!   =   7! 5! 3!      (two distinct representations)
    16! = 14! 5! 2!
Erdos conjectured there are only finitely many such solutions. This script certifies, by
exhaustive search using exact prime-valuation (Legendre) arithmetic, that there is NO
solution other than n in {9, 10, 16} for every n <= N.

------------------------------------------------------------------------------------------
METHOD (prime-valuation / Legendre -- no giant integers are ever formed)

Fix a_1, the LARGEST factor. Then
        R := n! / a_1! = (a_1+1)(a_1+2) ... n
must itself be a product of factorials each <= a_1! (indices in [2, a_1]).

COMPLETENESS PRUNE (this is what makes the per-n search finite and exact):
  Any prime p with a_1 < p <= n divides R but divides NO factorial <= a_1! (a factorial
  m! with m <= a_1 < p contains no factor p). So a representation can exist only if the
  interval (a_1, n] contains no prime, i.e.  a_1 >= q,  where q = largest prime <= n.
  Hence the only candidate largest-factors are  q <= a_1 <= n-2.  If q > n-2 (i.e. n or
  n-1 is prime, or more generally the prime gap immediately below n is < 2) there is
  nothing to search for that n.  In particular, by construction every prime factor of R
  is <= a_1.

DECOMPOSING R into factorials (backtracking, largest-prime-first):
  Let p = the largest prime dividing the current remainder. The largest factorial index J
  used to cover it satisfies  p <= J < nextprime(p): any J >= nextprime(p) would inject a
  prime in (p, J] that R does not contain. Moreover v_2(J!) <= v_2(R), and v_2(J!) ~ J, so
  J is small whenever R is (R is a product of only a prime-gap's worth of consecutive
  integers). These two bounds make the branching tiny; we enumerate ALL decompositions.
  Everything is exact integer arithmetic on prime exponents (Legendre's formula), so a
  referee recomputes bit-for-bit.

Deterministic and re-runnable. Output depends only on N.
------------------------------------------------------------------------------------------
"""
import sys
import time
from array import array
from bisect import bisect_right


def build_spf(N):
    """Smallest-prime-factor sieve for 2..N. spf[i]==i iff i is prime."""
    spf = array('i', bytes(4 * (N + 1)))  # zero-initialised int32 array of length N+1
    for i in range(2, N + 1):
        if spf[i] == 0:            # i is prime
            spf[i] = i
            if i * i <= N:
                for j in range(i * i, N + 1, i):
                    if spf[j] == 0:
                        spf[j] = i
    return spf


def factor(m, spf):
    """Return dict {prime: exponent} of m using the SPF sieve. O(log m)."""
    d = {}
    while m > 1:
        p = spf[m]
        c = 0
        while m % p == 0:
            m //= p
            c += 1
        d[p] = d.get(p, 0) + c
    return d


def legendre(p, m):
    """v_p(m!) = sum_{i>=1} floor(m / p^i)."""
    s = 0
    pk = p
    while pk <= m:
        s += m // pk
        pk *= p
    return s


NODE_CAP = 5_000_000      # safety valve on decomposition backtracking nodes
SOL_CAP = 100_000         # safety valve on number of decompositions collected per (n,a_1)


class Explosion(Exception):
    pass


def decompose(rem, b, primes, counter):
    """
    Enumerate every multiset of factorial indices in [2, b] whose factorials multiply to
    exactly `rem` (a dict prime->positive exponent). Returns a list of tuples in
    non-increasing order. Largest-prime-first backtracking with the two bounds above.
    """
    if not rem:
        return [()]
    counter[0] += 1
    if counter[0] > NODE_CAP:
        raise Explosion("node cap exceeded")

    p = max(rem)                      # largest prime still to cover
    r2 = rem.get(2, 0)                # available power of 2

    # nextprime(p): p is prime, so it's the next entry in `primes`.
    idx = bisect_right(primes, p)
    nextp = primes[idx] if idx < len(primes) else (p + 1)  # (p+1) only if p is last prime
    hi = min(b, nextp - 1)
    # tighten by the power-of-2 budget: v_2(j!) must be <= r2
    while hi >= p and legendre(2, hi) > r2:
        hi -= 1

    results = []
    for j in range(hi, p - 1, -1):
        # does j! fit inside rem?  (check every prime <= j)
        vj = []
        ok = True
        for pp in primes:
            if pp > j:
                break
            v = legendre(pp, j)
            if v > rem.get(pp, 0):
                ok = False
                break
            vj.append((pp, v))
        if not ok:
            continue
        newrem = dict(rem)
        for pp, v in vj:
            nv = newrem[pp] - v
            if nv == 0:
                del newrem[pp]
            else:
                newrem[pp] = nv
        for tail in decompose(newrem, j, primes, counter):
            results.append((j,) + tail)
            if len(results) >= SOL_CAP:
                return results
    return results


def fmt_solution(n, a1, tail):
    factors = [a1] + list(tail)
    rhs = " ".join(f"{a}!" for a in factors)
    return f"{n}! = {rhs}"


def search(N, log=sys.stdout, progress_every=0):
    t0 = time.time()
    print(f"# Erdos #373 exhaustive search, N = {N}", file=log)
    print(f"# building smallest-prime-factor sieve up to {N} ...", file=log)
    log.flush()
    spf = build_spf(N)
    primes = [i for i in range(2, N + 1) if spf[i] == i]
    print(f"# sieve done ({time.time()-t0:.1f}s); pi(N) = {len(primes)} primes", file=log)
    log.flush()

    solutions = []            # list of (n, [factors...])
    n_with_candidates = 0
    pairs_examined = 0
    exploded = []
    last_prime = 0            # largest prime <= current n

    for n in range(2, N + 1):
        if spf[n] == n:
            last_prime = n
        q = last_prime
        # candidate largest-factors a_1 in [q, n-2]; empty unless q <= n-2
        if q > n - 2:
            if progress_every and n % progress_every == 0:
                print(f"# n={n}  t={time.time()-t0:.0f}s  solutions={len(solutions)}", file=log)
                log.flush()
            continue
        n_with_candidates += 1
        # R = n!/a1! built incrementally as a1 decreases from n-2 to q
        rem = {}
        # start with a1 = n-2  =>  R = n*(n-1)
        for m in (n, n - 1):
            for pp, e in factor(m, spf).items():
                rem[pp] = rem.get(pp, 0) + e
        a1 = n - 2
        while a1 >= q:
            pairs_examined += 1
            # decompose the current R = product_{j=a1+1}^{n} j  into factorials <= a1!
            counter = [0]
            try:
                # work on a copy so decompose can mutate freely
                decs = decompose(dict(rem), a1, primes, counter)
            except Explosion:
                exploded.append((n, a1))
                decs = []
            for tail in decs:
                # a genuine nontrivial solution: n! = a1! * prod(tail!)
                solutions.append((n, [a1] + list(tail)))
            # step to next smaller a1: multiply R by a1 (the new (a1+1)-1 = a1)
            a1 -= 1
            if a1 >= q:
                for pp, e in factor(a1 + 1, spf).items():
                    rem[pp] = rem.get(pp, 0) + e
        if progress_every and n % progress_every == 0:
            print(f"# n={n}  t={time.time()-t0:.0f}s  solutions={len(solutions)}", file=log)
            log.flush()

    dt = time.time() - t0
    print("#", "-" * 70, file=log)
    print(f"# DONE  N={N}  time={dt:.1f}s  n_with_candidates={n_with_candidates}"
          f"  (n,a1)_pairs_examined={pairs_examined}", file=log)
    if exploded:
        print(f"# WARNING: backtracking node cap hit at {len(exploded)} pairs: {exploded[:10]}",
              file=log)
    print(f"# total solutions (representations) found: {len(solutions)}", file=log)
    for (n, factors) in solutions:
        print("SOLUTION: " + fmt_solution(n, factors[0], factors[1:]), file=log)
    log.flush()
    return solutions, dt, pairs_examined, exploded


def main(argv):
    N = int(argv[1]) if len(argv) > 1 else 100000
    progress = int(argv[2]) if len(argv) > 2 else 0
    solutions, dt, pairs, exploded = search(N, progress_every=progress)

    # Verdict vs. the three known Erdos solutions.
    found_ns = sorted({n for (n, _) in solutions})
    print("#", "=" * 70)
    print(f"# VERDICT for n <= {N}:")
    print(f"#   distinct n admitting a nontrivial representation: {found_ns}")
    known = {9, 10, 16}
    extra = [n for n in found_ns if n not in known]
    missing = [n for n in known if n not in found_ns and n <= N]
    if not extra and not missing:
        print("#   EXACTLY the three known Erdos solutions {9,10,16} -- NO new witness. "
              "Conjecture holds for this range.")
    else:
        if missing:
            print(f"#   ERROR: known solution(s) NOT rediscovered: {missing}  (searcher is BROKEN)")
        if extra:
            print(f"#   *** NEW WITNESS/WITNESSES: {extra}  *** investigate!")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
