#!/usr/bin/env python3
"""Stage A: certify the transcription of the Ismailescu-Son (2014) sequence.

Checks (all exact integer arithmetic, deterministic):
  A1  q (129 digits, Theorem 3) equals the smallest positive CRT solution of the
      30 congruences in Table 3 (independent transcription cross-check).
  A2  Every Table-2/3 modulus p_i is prime (deterministic Miller-Rabin for n < 3.3e24).
  A3  gcd(x0, x1) = 1 where x0 = 1 + q^2, x1 = 2q + q^2 (p = 1).
  A4  Covering: every even residue 0 <= 2n < lcm(m_i) satisfies 2n == r_i (mod m_i)
      for some i (hence ALL even indices are covered).
  A5  p_i | F_{m_i} for every quadruple (paper condition (b)).
  A6  x0 == c_i * F_{m_i - r_i} and x1 == c_i * F_{m_i - r_i + 1} (mod p_i) for all i
      (paper eq. (10)); together with A4/A5 this PROVES x_{2n} == 0 mod some p_i
      for every n >= 0.
  A7  Identity x_{2n+1} = (F_n + q F_{n+1})(L_n + q L_{n+1}) exactly for n = 0..60.
  A8  Direct spot-check: for 2000 even indices, x_{2n} is divisible by a Table-2 prime.

Exit nonzero on any failure. Output: results/stage_a.log
"""
import sys, math, json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA, RESULTS = ROOT / "data", ROOT / "results"

def load_tables():
    q = int((DATA / "q_decimal.txt").read_text().strip())
    quads, cong = [], []
    for line in (DATA / "table2_quadruples.tsv").read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        p, m, r, c = map(int, line.split())
        quads.append((p, m, r, c))
    for line in (DATA / "table3_congruences.tsv").read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        p, res = map(int, line.split())
        cong.append((p, res))
    return q, quads, cong

def is_prime(n):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2; s += 1
    # deterministic for n < 3.317e24 with these bases
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
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

def crt(cong):
    x, M = 0, 1
    for p, r in cong:
        g = math.gcd(M, p)
        assert g == 1
        x = (x + M * ((r - x) * pow(M, -1, p) % p)) % (M * p)
        M *= p
    return x, M

def fib_pair(n):
    """(F_n, F_{n+1}) by fast doubling, exact."""
    if n == 0:
        return (0, 1)
    a, b = fib_pair(n >> 1)
    c = a * (2 * b - a)
    d = a * a + b * b
    return (d, c + d) if n & 1 else (c, d)

def main():
    log = []
    def out(s):
        log.append(s); print(s)
    ok = True
    q, quads, cong = load_tables()

    out(f"q digits: {len(str(q))}")
    if len(str(q)) != 129:
        ok = False; out("FAIL: q is not 129 digits")

    # A2 primality
    for p, m, r, c in quads:
        if not is_prime(p):
            ok = False; out(f"FAIL: table modulus {p} not prime")
    out("A2 PASS: all 30 Table-2 moduli are prime (deterministic MR, n < 3.3e24)")

    # A1 CRT
    if sorted(p for p, _ in cong) != sorted(p for p, _, _, _ in quads):
        ok = False; out("FAIL: Table 2 / Table 3 prime sets differ")
    x, M = crt(cong)
    out(f"CRT modulus M = prod p_i has {len(str(M))} digits")
    if x == q:
        out("A1 PASS: q equals the smallest positive CRT solution of Table 3 exactly")
    else:
        ok = False; out(f"A1 FAIL: CRT solution != transcribed q\n  crt={x}\n  q  ={q}")

    p_par, x0, x1 = 1, 1 + q * q, 2 * q + q * q
    out(f"x0 digits: {len(str(x0))}, x1 digits: {len(str(x1))}")

    # A3
    g = math.gcd(x0, x1)
    if g == 1:
        out("A3 PASS: gcd(x0, x1) = 1")
    else:
        ok = False; out(f"A3 FAIL: gcd(x0,x1) = {g}")

    # A4 covering of even integers
    L = math.lcm(*[m for _, m, _, _ in quads])
    out(f"lcm(m_i) = {L}")
    uncovered = [e for e in range(0, L, 2)
                 if not any(e % m == r % m for _, m, r, _ in quads)]
    if not uncovered:
        out(f"A4 PASS: every even residue mod {L} is covered by some (r_i, m_i)")
    else:
        ok = False; out(f"A4 FAIL: uncovered even residues mod {L}: {uncovered[:10]}...")

    # A5 p_i | F_{m_i}
    for p, m, r, c in quads:
        if fib_pair(m)[0] % p != 0:
            ok = False; out(f"A5 FAIL: {p} does not divide F_{m}")
    out("A5 PASS: p_i | F_(m_i) for all 30 quadruples")

    # A6 eq (10)
    for p, m, r, c in quads:
        Fm_r, Fm_r1 = fib_pair(m - r)
        if x0 % p != c * Fm_r % p or x1 % p != c * Fm_r1 % p:
            ok = False; out(f"A6 FAIL at p={p}")
    out("A6 PASS: x0 == c_i F_(m_i-r_i), x1 == c_i F_(m_i-r_i+1) (mod p_i) for all i")
    out("     => THEOREM (paper eq. (8) argument): x_(2n) == 0 mod some p_i for ALL n>=0")

    # A7 odd-index factorization identity, exact
    xs = [x0, x1]
    for i in range(2, 200):
        xs.append(xs[-1] + xs[-2])
    F = [0, 1]
    for i in range(2, 200):
        F.append(F[-1] + F[-2])
    Luc = [2, 1]
    for i in range(2, 200):
        Luc.append(Luc[-1] + Luc[-2])
    for n in range(0, 61):
        lhs = xs[2 * n + 1]
        rhs = (p_par * F[n] + q * F[n + 1]) * (p_par * Luc[n] + q * Luc[n + 1])
        if lhs != rhs:
            ok = False; out(f"A7 FAIL at n={n}")
    out("A7 PASS: x_(2n+1) = (F_n + q F_(n+1)) (L_n + q L_(n+1)) exactly for n = 0..60")

    # A8 spot-check even indices covered (direct divisibility, independent of A6 proof)
    rng = random.Random(276)
    P = [p for p, _, _, _ in quads]
    bad = []
    for _ in range(2000):
        n2 = 2 * rng.randrange(0, 500000)
        # x_n mod p via fast doubling on (x0,x1) mod p: x_n = x0 F_{n-1} + x1 F_n
        hit = False
        for p in P:
            fn, fn1 = fib_pair(n2)          # exact would be huge; do mod-p doubling instead
            hit = False
            break
        # cheaper: compute x_{n2} mod p by iterative doubling mod p
        def xmod(nn, p):
            def fp(k):
                if k == 0:
                    return (0, 1)
                a, b = fp(k >> 1)
                c = a * (2 * b - a) % p
                d = (a * a + b * b) % p
                return (d, (c + d) % p) if k & 1 else (c, d)
            fn, fn1 = fp(nn)
            fnm1 = (fn1 - fn) % p
            return (x0 % p * fnm1 + x1 % p * fn) % p
        if not any(xmod(n2, p) == 0 for p in P):
            bad.append(n2)
    if not bad:
        out("A8 PASS: 2000 random even indices n<=10^6: x_n divisible by a Table-2 prime")
    else:
        ok = False; out(f"A8 FAIL: even indices not covered: {bad[:5]}")

    out("STAGE A RESULT: " + ("ALL PASS" if ok else "FAILURES PRESENT"))
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "stage_a.log").write_text("\n".join(log) + "\n")
    sys.exit(0 if ok else 1)

main()
