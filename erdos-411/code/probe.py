#!/usr/bin/env python3
"""Erdos #411 probe: independent implementation.

g(n) = n + phi(n).  Find all "raw multiplier hits" g_r(x) = c*x (integer c >= 2)
for 2 <= x <= X, 1 <= r <= R, then filter to *certificates*:

    g_r(x) = c*x   and   rad(c) | g_j(x) for all 0 <= j < r,

which (by the certificate lemma, proof_structural_lemmas.md) is equivalent to
the eventual relation g_{k+r}(n) = c*g_k(n) for all large k, for any n whose
orbit passes through x.

Pure Python, no third-party deps.  Own linear totient sieve + deterministic
Miller-Rabin + Brent-Pollard rho for orbit values beyond the sieve.

Usage: python3 probe.py [X] [R]   (defaults 100000 25)
Output: raw hits and certified witnesses as JSON lines on stdout.
"""
import sys, json, math, random

# ---------- linear totient sieve ----------
def phi_sieve(n):
    phi = list(range(n + 1))
    for i in range(2, n + 1):
        if phi[i] == i:  # i prime
            for j in range(i, n + 1, i):
                phi[j] -= phi[j] // i
    return phi

# ---------- deterministic Miller-Rabin (valid for n < 3.3e24) ----------
_MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
def is_prime(n):
    if n < 2:
        return False
    for p in _MR_BASES:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2; s += 1
    for a in _MR_BASES:
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

def _brent(n):
    if n % 2 == 0:
        return 2
    while True:
        y = random.randrange(1, n); c = random.randrange(1, n); m = 128
        g = r = q = 1
        while g == 1:
            x = y
            for _ in range(r):
                y = (y * y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, r - k)):
                    y = (y * y + c) % n
                    q = q * abs(x - y) % n
                g = math.gcd(q, n)
                k += m
            r <<= 1
        if g == n:
            g = 1
            while g == 1:
                ys = (ys * ys + c) % n
                g = math.gcd(abs(x - ys), n)
        if g != n:
            return g

def factorize(n, out=None):
    """Return dict prime -> exponent."""
    if out is None:
        out = {}
    if n == 1:
        return out
    if is_prime(n):
        out[n] = out.get(n, 0) + 1
        return out
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47):
        while n % p == 0:
            out[p] = out.get(p, 0) + 1
            n //= p
    if n == 1:
        return out
    if is_prime(n):
        out[n] = out.get(n, 0) + 1
        return out
    d = _brent(n)
    factorize(d, out)
    factorize(n // d, out)
    return out

def phi_big(n, cache):
    v = cache.get(n)
    if v is None:
        f = factorize(n)
        v = 1
        for p, e in f.items():
            v *= (p - 1) * p ** (e - 1)
        cache[n] = v
    return v

def rad(n):
    return math.prod(factorize(n).keys())

def main():
    X = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
    R = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    SIEVE = min(4 * X, 4_000_000)
    phi = phi_sieve(SIEVE)
    cache = {}

    def g(v):
        return v + (phi[v] if v <= SIEVE else phi_big(v, cache))

    hits = []
    for x in range(2, X + 1):
        v = x
        for r in range(1, R + 1):
            v = g(v)
            if v % x == 0:
                c = v // x
                if c >= 2:
                    hits.append((x, r, c))

    certs = []
    for (x, r, c) in hits:
        radc = rad(c)
        orbit = [x]
        v = x
        ok = True
        for j in range(r):
            if orbit[j] % radc != 0:
                ok = False
                break
            v = g(v)
            orbit.append(v)
        if ok:
            assert orbit[r] == c * x
            certs.append({"x": x, "r": r, "c": c, "orbit": orbit})

    print(json.dumps({"X": X, "R": R,
                      "raw_hits": [list(h) for h in hits],
                      "certificates": certs}))
    sys.stderr.write(f"raw hits: {len(hits)}, certificates: {len(certs)}\n")

if __name__ == "__main__":
    main()
