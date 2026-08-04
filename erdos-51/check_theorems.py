#!/usr/bin/env python3
"""Verify Theorem 1 (proof_ratio2_family.md) instances by exhaustive enumeration,
and the elementary obstruction bound (Theorem 4 of proof_obstruction_lemmas.md),
independently of the C sieve.

Checks, for every k in 1..KMAX (default 40):
  * invphi(2^k) equals EXACTLY the preimage set predicted by Theorem 1:
      {2^(k+1-sigma(S)) * prod_{i in S} F_i : S subset of P0, sigma(S) <= k}
      union {prod_{i in B(k)} F_i} if B(k) subset of P0,
    where P0 = {i <= 5 : F_i prime} = {0,1,2,3,4} (F_5 composite, checked via 641).
    (For k <= 40 every bit of k is <= 5 and every candidate S has max index <= 5;
     indices i >= 6 cannot appear because sigma would need 2^i = 64 > k.)
  * the dichotomy: f(2^k) = 2^(k+1) iff some bit of k indexes a composite Fermat
    number; otherwise f(2^k) = prod F_i in (2^k, 2^(k+1)).
  * Theorem 4: for each k, v_2(2^k) = k >= (K^2-4)/8 where K = f(2^k)/2^k.
Exit code 0 iff all checks pass.
"""
import sys
from sympy import isprime
from invphi import invphi

KMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 40

F = {i: 2**(2**i) + 1 for i in range(6)}
assert F[5] % 641 == 0 and F[5] == 641 * 6700417, "Euler's factorization of F_5"
P0 = {i for i in range(6) if isprime(F[i])}
assert P0 == {0, 1, 2, 3, 4}, "known Fermat primes among F_0..F_5"

def prod(xs):
    r = 1
    for x in xs:
        r *= x
    return r

fails = 0
for k in range(1, KMAX + 1):
    a = 2**k
    bits = {i for i in range(k.bit_length()) if (k >> i) & 1}
    # predicted preimages
    pred = set()
    idxs = sorted(P0)
    for mask in range(1 << len(idxs)):
        S = [idxs[j] for j in range(len(idxs)) if (mask >> j) & 1]
        sig = sum(2**i for i in S)
        if sig <= k:
            pred.add(2**(k + 1 - sig) * prod(F[i] for i in S))
    odd_exists = bits <= P0
    if odd_exists:
        pred.add(prod(F[i] for i in bits))
    got = set(invphi(a))
    ok_set = (got == pred)
    fmin = min(got)
    if odd_exists:
        expect_min = prod(F[i] for i in bits)
        ok_min = fmin == expect_min and a < fmin < 2 * a
        regime = "odd, ratio=%.6f<2" % (fmin / a)
    else:
        ok_min = fmin == 2 * a
        regime = "ratio exactly 2"
    K = fmin / a
    ok_t4 = k >= (K * K - 4) / 8
    status = "OK " if (ok_set and ok_min and ok_t4) else "FAIL"
    if status == "FAIL":
        fails += 1
    print("%s k=%2d  #pre=%3d  f(2^k)=%d  %s" % (status, k, len(got), fmin, regime))

print("check_theorems: %d failures (k=1..%d)" % (fails, KMAX))
sys.exit(1 if fails else 0)
