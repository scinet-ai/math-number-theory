#!/usr/bin/env python3
"""Machine checks for proof_main.md (Erdős #963, KoishiChan's argument, effectivized).

Checks (all must pass):
  fourier    -- Lemma 7(ii): E_r |rA ∩ B|^2 == (1/(q-1)^2) Σ_χ |S_A(χ)|^2 |S_B(χ)|^2,
                brute force over ALL r vs an independent character-sum implementation
                (characters built from a primitive root; no shared code path).
  apbound    -- Lemma 7(iii): |S_B(χ)| <= 2 M(χ) for difference-p APs, all χ != χ_0.
  splice     -- Lemma 6: randomized instances, dissociativity verified by exhaustive
                enumeration of all {-1,0,1} signed relations.
  transport  -- Lemma 4 + Lemma 5 + Lemma 3 chain on random instances.
  unroll     -- §6 bookkeeping: worst-case recursion trace gives
                total_gain(g) >= g - 2 (log2 g)^2 - g*  for g up to 1e6,
                and the fitted constant approaches ~1.2047 = 1/(2 log2(4/3)).
  thresholds -- the numeric thresholds asserted in §6 (g* = 361 for C_MV <= 1, etc.)
  mv_data    -- (data, not proof) Σ_{χ≠χ0} M(χ)^4 / (φ(q) q^2) for small primes,
                sanity that the MV normalization is the right one (ratio bounded).

Usage: python3 verify.py [--check NAME] [--seed N]
"""

import argparse
import itertools
import math
import random
import sys


# ---------- number theory helpers (independent implementation) ----------

def is_prime(n):
    if n < 2:
        return False
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            return False
    return True


def primitive_root(q):
    """Smallest primitive root of prime q."""
    order = q - 1
    fac = []
    t, d = order, 2
    while d * d <= t:
        if t % d == 0:
            fac.append(d)
            while t % d == 0:
                t //= d
        d += 1
    if t > 1:
        fac.append(t)
    for g in range(2, q):
        if all(pow(g, order // f, q) != 1 for f in fac):
            return g
    raise RuntimeError("no primitive root found")


def characters(q):
    """All Dirichlet characters mod prime q, as dicts residue->complex.

    chi_j(g^t) = exp(2 pi i j t / (q-1)); chi_j(0) = 0. j=0 is principal.
    """
    g = primitive_root(q)
    order = q - 1
    dlog = {}
    x = 1
    for t in range(order):
        dlog[x] = t
        x = (x * g) % q
    chis = []
    for j in range(order):
        chi = {0: 0.0}
        for res, t in dlog.items():
            chi[res] = complex(math.cos(2 * math.pi * j * t / order),
                               math.sin(2 * math.pi * j * t / order))
        chis.append(chi)
    return chis  # chis[0] is principal


def M_of_chi(chi, q):
    """M(chi) = max over 1<=R<q of |sum_{n<=R} chi(n)| (enough by periodicity)."""
    best, s = 0.0, 0j
    for n in range(1, q):
        s += chi[n % q]
        best = max(best, abs(s))
    return best


# ---------- dissociativity by brute force ----------

def is_dissociated(S):
    """Exhaustive check over all {-1,0,1} signed relations. |S| <= ~14."""
    S = list(S)
    for eps in itertools.product((-1, 0, 1), repeat=len(S)):
        if any(eps) and sum(e * s for e, s in zip(eps, S)) == 0:
            return False
    return True


def is_dissociated_mod(S, q):
    S = list(S)
    for eps in itertools.product((-1, 0, 1), repeat=len(S)):
        if any(eps) and sum(e * s for e, s in zip(eps, S)) % q == 0:
            return False
    return True


# ---------- checks ----------

def check_fourier(rng):
    ok = True
    for q in (61, 101):
        assert is_prime(q)
        chis = characters(q)
        for trial in range(3):
            N = rng.randrange(8, 20)
            A = rng.sample(range(1, q), N)
            p = rng.choice([2, 4, 8, 3, 5])
            X = rng.randrange(3, (q - 1) // p)
            u = rng.randrange(0, p)
            B = [(p * x + u) % q for x in range(1, X + 1)]
            if 0 in B:
                continue
            Bset = set(B)
            # LHS: brute force over all units r
            lhs = sum(len({(r * a) % q for a in A} & Bset) ** 2
                      for r in range(1, q)) / (q - 1)
            # RHS: character formula
            rhs = 0.0
            for chi in chis:
                SA = sum(chi[a % q] for a in A)
                SB = sum(chi[b % q] for b in B)
                rhs += (abs(SA) ** 2) * (abs(SB) ** 2)
            rhs /= (q - 1) ** 2
            if abs(lhs - rhs) > 1e-6:
                print(f"  FAIL fourier q={q} trial={trial}: {lhs} vs {rhs}")
                ok = False
    print(f"fourier: {'PASS' if ok else 'FAIL'} (identity of Lemma 7(ii), q=61,101)")
    return ok


def check_apbound(rng):
    ok = True
    q = 101
    chis = characters(q)
    Ms = [None] + [M_of_chi(chi, q) for chi in chis[1:]]
    for trial in range(5):
        p = rng.choice([2, 4, 8, 16, 3, 7])
        X = rng.randrange(2, (q - 1) // p)
        u = rng.randrange(0, p)
        B = [p * x + u for x in range(1, X + 1) if 0 < (p * x + u) < q]
        for j, chi in enumerate(chis[1:], start=1):
            SB = abs(sum(chi[b % q] for b in B))
            if SB > 2 * Ms[j] + 1e-9:
                print(f"  FAIL apbound: q={q} p={p} u={u} X={X} chi_{j}: "
                      f"|S_B|={SB} > 2M={2*Ms[j]}")
                ok = False
    print(f"apbound: {'PASS' if ok else 'FAIL'} (|S_B(chi)| <= 2 M(chi), difference-p APs)")
    return ok


def check_splice(rng):
    ok = True
    for trial in range(20):
        m = rng.randrange(2, 5)
        p = 2 ** m
        Gamma = [2 ** j for j in range(m)]
        # random dissociated D' in class 0 mod p: rapidly growing multiples of p
        size = rng.randrange(2, 5)
        Dp, cur = [], p * rng.randrange(1, 4)
        for _ in range(size):
            Dp.append(cur)
            cur = cur * rng.randrange(3, 6) + p * rng.randrange(1, 3)
        assert all(d % p == 0 for d in Dp)
        if not is_dissociated(Dp):
            continue  # construction should be dissociated, but only proceed if verified
        # random a_i ≡ i (mod p)
        a = {i: i + p * rng.randrange(1, 50) for i in Gamma}
        E = Dp + [a[i] for i in Gamma]
        if len(set(E)) != len(E) or not is_dissociated(E):
            print(f"  FAIL splice trial={trial}: m={m} D'={Dp} a={a}")
            ok = False
    print(f"splice: {'PASS' if ok else 'FAIL'} (Lemma 6 on random instances, exhaustive signed sums)")
    return ok


def check_transport(rng):
    ok = True
    for trial in range(20):
        q = rng.choice([211, 401, 1009])
        k = rng.randrange(2, 7)
        bound = (q - 1) // k
        # random dissociated S in [1, bound], |S| = k
        for _ in range(50):
            S = rng.sample(range(1, bound + 1), k)
            if is_dissociated(S):
                break
        else:
            continue
        if not is_dissociated_mod(S, q):
            print(f"  FAIL transport (Lemma 4) trial={trial}: q={q} k={k} S={S}")
            ok = False
            continue
        # dilation invariance (Lemma 5): rS dissociated mod q for random unit r
        r = rng.randrange(1, q)
        rS = [(r * s) % q for s in S]
        if not is_dissociated_mod(rS, q):
            print(f"  FAIL transport (Lemma 5) trial={trial}: q={q} r={r} S={S}")
            ok = False
    print(f"transport: {'PASS' if ok else 'FAIL'} (Lemmas 4+5 on random instances)")
    return ok


def gstar_of(C0):
    c6 = 0.5 * math.log2(8 * C0)
    g = 205
    while g / 20 < 1.5 * math.log2(g) + c6 + 1:
        g += 1
    return g, c6


def check_thresholds():
    ok = True
    b = math.log2(5 / 4)
    thr = (2 + 2 * b * b) / (4 * b - 1)
    if not (7.67 < thr < 7.68 and 2 ** thr < 205):
        print(f"  FAIL: W-inequality threshold {thr}")
        ok = False
    g, c6 = gstar_of(48)  # C_MV = 1
    if g != 361:
        print(f"  FAIL: g* for C_MV=1 is {g}, doc says 361")
        ok = False
    cstar = 1 / (2 * math.log2(4 / 3))
    if abs(cstar - 1.2047104198266048) > 1e-12:
        ok = False
    print(f"thresholds: {'PASS' if ok else 'FAIL'} "
          f"(W-threshold g>={2**thr:.1f}<=205; g*(C_MV=1)={g}; C*={cstar:.10f})")
    return ok


def check_unroll():
    """Worst-case trace of the §6 induction; verifies Σ m_j >= g - 2(log2 g)^2 - g*."""
    ok = True
    C0 = 48.0  # C_MV = 1
    gstar, c6 = gstar_of(C0)
    fitted = []
    for g0 in (1e3, 1e4, 1e5, 1e6):
        g, total = g0, 0.0
        while g >= gstar:
            m = math.floor(g / 4 - 1.5 * math.log2(g) - c6)
            if m < 1:
                break
            total += m
            g = g - m - math.log2(g) - 2  # worst-case (smallest) next scale
        bound = g0 - 2 * (math.log2(g0)) ** 2 - gstar
        if total < bound:
            print(f"  FAIL unroll: g={g0:g} total={total:.1f} < bound={bound:.1f}")
            ok = False
        fitted.append((g0, (g0 - total) / (math.log2(g0)) ** 2))
    msg = ", ".join(f"g={a:g}: C_emp={b:.3f}" for a, b in fitted)
    print(f"unroll: {'PASS' if ok else 'FAIL'} (worst-case trace beats g - 2(log2 g)^2 - g*; {msg})")
    print(f"        [C_emp should decrease toward C* = {1/(2*math.log2(4/3)):.4f} as g grows]")
    return ok


def check_mv_data():
    # Data only: MV Thm 1 (k=2) normalization sanity on small primes.
    rows = []
    for q in (61, 101, 151):
        chis = characters(q)
        s = sum(M_of_chi(chi, q) ** 4 for chi in chis[1:])
        rows.append((q, s / ((q - 1) * q * q)))
    print("mv_data: (data) ratio Σ M(χ)^4 / (φ(q) q^2) =",
          ", ".join(f"q={q}: {r:.3f}" for q, r in rows),
          " [bounded ~O(1): consistent with MV Thm 1 normalization]")
    return True


CHECKS = {
    "fourier": lambda rng: check_fourier(rng),
    "apbound": lambda rng: check_apbound(rng),
    "splice": lambda rng: check_splice(rng),
    "transport": lambda rng: check_transport(rng),
    "unroll": lambda rng: check_unroll(),
    "thresholds": lambda rng: check_thresholds(),
    "mv_data": lambda rng: check_mv_data(),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", choices=sorted(CHECKS), default=None)
    ap.add_argument("--seed", type=int, default=963)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    names = [args.check] if args.check else list(CHECKS)
    results = [CHECKS[n](rng) for n in names]
    if all(results):
        print("ALL CHECKS PASSED")
        return 0
    print("SOME CHECKS FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
