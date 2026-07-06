"""
Admissible moduli for Erdos #273: covering systems whose moduli all have the
form p - 1 for a prime p >= 5.

Also implements the ISOLATED-PRIME REMOVAL LEMMA used to shrink the search space
without loss of generality.

Lemma (isolated-prime removal). Let S be a set of moduli and q a prime that
divides exactly one modulus m0 in S. Then m0 is redundant: any covering system
using classes with moduli in S implies a covering system using moduli in
S \ {m0}. Consequently a covering with moduli in S exists iff one exists with
moduli in S \ {m0}.

Proof. Let v = v_q(L) where L = lcm(S); note v = v_q(m0) since only m0 is
divisible by q. Suppose classes {a_i mod m_i : m_i in S} cover Z. Let U be the
set of residues mod L covered by NO class other than m0's. Every modulus except
m0 is coprime to q, so the set C = complement(U) covered by the other classes is
a union of APs with moduli dividing L' = L / q^v (all coprime to q); hence
membership in C depends only on x mod L', i.e. C (and therefore U) is invariant
under x -> x + L'. The map x -> x + L' has order q^v on Z/L (since gcd(L',q)=0,
L' generates the q^v-part), so each orbit has q^v points hitting every residue
mod q^v exactly once. The single class a0 mod m0 meets each such orbit in at most
one point (it pins x mod q^v to a0). A +L'-invariant set U contained in a set
meeting every orbit in <= 1 point can contain no full orbit, so U = empty. Thus
the other classes already cover Z and m0 is redundant. QED

The lemma is applied iteratively (removing one isolated-prime modulus can make
another prime isolated). Prime 2 divides every admissible modulus, so it is
never isolated.
"""
from math import gcd
from functools import reduce
from sympy import isprime, factorint


def admissible_moduli(max_mod):
    """All m = p - 1 <= max_mod with p prime >= 5, sorted ascending."""
    out = []
    p = 5
    while p - 1 <= max_mod:
        if isprime(p):
            out.append(p - 1)
        p += 2  # only odd p can be prime (>=5)
    return sorted(out)


def factor(m):
    return dict(factorint(m))


def lcm(nums):
    return reduce(lambda a, b: a * b // gcd(a, b), nums, 1)


def prime_support(moduli):
    """Map prime -> list of moduli in `moduli` divisible by it."""
    supp = {}
    for m in moduli:
        for q in factor(m):
            supp.setdefault(q, []).append(m)
    return supp


def reduce_local_density(moduli, verbose=False):
    """Iteratively remove ALL moduli divisible by a prime q whenever
        sum_{m in cur, q | m} q^{-v_q(m)}  <  1.

    Generalized removal lemma. Fix prime q, let v = max v_q over cur, and
    L' = lcm(cur)/q^v. The classes with q-coprime moduli cover a set C that is
    invariant under x -> x + L' (their moduli all divide L'); so U = complement
    of C is a union of full +L'-orbits, each a coset that ranges over ALL q^v
    residues mod q^v exactly once. A class a mod m with q^f || m (f>=1) meets any
    such orbit in at most q^{v-f} of its q^v points (it pins x mod q^f). Hence
    the q-divisible classes together cover at most q^v * sum q^{-v_q(m)} < q^v
    points of any orbit in U, so they cannot cover a full orbit. Therefore U must
    be empty: the q-coprime classes already cover Z, and EVERY q-divisible
    modulus is redundant. (Isolated prime = special case, sum = q^{-v} < 1.)

    Iterated to a fixpoint. `core` is EQUIVALENT to `moduli` for the covering-
    existence question (redundant removals both directions), so it is complete
    for BOTH witness search and bounded non-existence.

    Returns (core, removed_log) where removed_log is a list of
    (prime, weight, [moduli_removed]).
    """
    cur = set(moduli)
    removed_log = []
    changed = True
    while changed:
        changed = False
        supp = prime_support(cur)
        for q in sorted(supp):
            Dq = supp[q]
            weight = sum(q ** (-factor(m)[q]) for m in Dq)
            if weight < 1 - 1e-12:
                for m in Dq:
                    cur.discard(m)
                removed_log.append((q, weight, sorted(Dq)))
                if verbose:
                    print(f"  remove all {len(Dq)} multiples of {q} "
                          f"(weight {weight:.4f} < 1): {sorted(Dq)}")
                changed = True
                break  # recompute support
    return sorted(cur), removed_log


def reduce_isolated_primes(moduli, verbose=False):
    """Iteratively remove any modulus that carries a prime dividing no other
    modulus in the current set. Returns (core, removed_log).

    core is complete for the covering-existence question (see module docstring):
    a covering with `moduli` exists iff one exists with `core`.
    """
    cur = set(moduli)
    removed_log = []
    changed = True
    while changed:
        changed = False
        supp = prime_support(cur)
        # find a modulus with an isolated prime
        for m in sorted(cur):
            isolated = [q for q in factor(m) if len(supp[q]) == 1]
            if isolated:
                cur.discard(m)
                removed_log.append((m, isolated))
                if verbose:
                    print(f"  remove {m}: isolated prime(s) {isolated}")
                changed = True
                break  # recompute support
    return sorted(cur), removed_log


if __name__ == "__main__":
    import sys
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    S = admissible_moduli(M)
    print(f"Admissible moduli <= {M}: {S}")
    print(f"  count = {len(S)}, sum 1/m = {sum(1/m for m in S):.4f}")
    print(f"  lcm(full) = {lcm(S)}")
    core, log = reduce_local_density(S, verbose=True)
    print(f"Core after local-density removal: {core}")
    print(f"  count = {len(core)}, sum 1/m = {sum(1/m for m in core):.4f}")
    print(f"  lcm(core) = {lcm(core)}")
