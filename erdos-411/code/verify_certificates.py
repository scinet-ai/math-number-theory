#!/usr/bin/env python3
"""Self-contained certificate verifier for Erdos #411 witnesses.

Reads a catalogue JSON (from postprocess.py) and re-checks EVERY certificate
from scratch by direct iteration of g(n) = n + phi(n):

  1. the stored orbit prefix is recomputed:  orbit[j+1] == orbit[j] + phi(orbit[j]);
  2. g_r(x) == c * x;
  3. rad(c) divides orbit[j] for all 0 <= j < r.

By the certificate equivalence theorem (proof_structural_lemmas.md, Theorem 2),
1-3 imply g_{k+r}(n) = c * g_k(n) for all k >= K for every n whose orbit reaches x
at index K -- in particular for n = x, for all k >= 0.

No imports from the sweep/probe code: phi is computed here by trial division up
to 10^6 followed by deterministic Miller-Rabin and Pollard's rho (floyd cycle,
distinct from probe.py's Brent variant).  Exit code 0 iff all certificates pass.

Usage: verify_certificates.py catalogue.json [--primitive-only]
"""
import sys, json, math

def _is_prime(n):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2; s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):  # deterministic < 3.3e24
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True

def _rho_floyd(n):
    """Pollard rho, Floyd cycle-finding. n odd composite with no factor <= 10^6."""
    c = 1
    while True:
        x = y = 2
        d = 1
        while d == 1:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            d = math.gcd(abs(x - y), n)
        if d != n:
            return d
        c += 1

def factor(n):
    fs = {}
    for p in range(2, 1000):
        while n % p == 0:
            fs[p] = fs.get(p, 0) + 1
            n //= p
        if p * p > n:
            break
    if n > 1:
        stack = [n]
        while stack:
            m = stack.pop()
            if m == 1:
                continue
            if _is_prime(m):
                fs[m] = fs.get(m, 0) + 1
                continue
            # try trial division a bit deeper before rho
            hit = False
            for p in range(1000, 10 ** 6, 2):
                if p * p > m:
                    break
                if m % p == 0:
                    stack.extend([p, m // p]); hit = True; break
            if not hit:
                d = _rho_floyd(m)
                stack.extend([d, m // d])
    return fs

def phi(n):
    if n == 1:
        return 1
    r = 1
    for p, e in factor(n).items():
        r *= (p - 1) * p ** (e - 1)
    return r

def rad(n):
    return math.prod(factor(n).keys())

def main():
    cat = json.load(open(sys.argv[1]))
    prim_only = "--primitive-only" in sys.argv
    certs = cat["certificates"]
    if prim_only:
        primx = {(p["x"], p["r"], p["c"]) for p in cat["primitive"]}
        certs = [c for c in certs if (c["x"], c["r"], c["c"]) in primx]
    bad = 0
    for i, cd in enumerate(certs):
        x, r, c, orbit = cd["x"], cd["r"], cd["c"], cd["orbit"]
        ok = (len(orbit) == r + 1 and orbit[0] == x)
        if ok:
            for j in range(r):
                if orbit[j + 1] != orbit[j] + phi(orbit[j]):
                    ok = False; break
        if ok and orbit[r] != c * x:
            ok = False
        if ok:
            rc = rad(c)
            if any(orbit[j] % rc for j in range(r)):
                ok = False
        if not ok:
            bad += 1
            print(f"FAIL: x={x} r={r} c={c}")
        if (i + 1) % 500 == 0:
            print(f"  ... {i+1}/{len(certs)} verified", file=sys.stderr)
    print(f"{len(certs) - bad}/{len(certs)} certificates verified"
          f"{' (primitive only)' if prim_only else ''}; {bad} failures")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
