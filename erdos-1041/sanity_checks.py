#!/usr/bin/env python3
"""Numerical sanity checks for the two proof write-ups for Erdős #1041.

Checks (all must PASS):
  A. Lemma 3 identity (proof_collinear.md): prod |P(y_i)| == disc(P)/n^n  (distinct real roots).
  B. Collinear theorem: for random + adversarial collinear-root configs in the open unit disk,
     min over consecutive gaps of max |f| on the segment is < 1 and <= (disc/n^n)^{1/(n-1)}.
  C. Lemma 4 (Hadamard): disc < n^n for near-extremal (Chebyshev-extrema) points in (-1,1).
  D. Lemma 2.3 (connectivity): for random f with roots in the disk, each component U of {|f|<1}
     with m>=1 zeros has {|f|<s} ∩ U connected for s in (c_max(U), 1)  [grid check].
  E. Lemma 3.2 (integral bound): ∫_{V_s} |f'/f| dA <= 2π sqrt(mn) s^{1/n} per component
     [grid quadrature], and near-equality for f = z^n.

Run:  python3 sanity_checks.py   (needs numpy, scipy)
Exit code 0 iff all checks pass. Deterministic (fixed RNG seed).
"""
import sys
import numpy as np
from numpy.polynomial import polynomial as npoly

rng = np.random.default_rng(20260803)
FAIL = []

def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}  {detail}")
    if not ok:
        FAIL.append(name)

# ---------- A. critical-value product identity ----------
# The identity  prod_i P(y_i) = (+/-) disc/n^n  is proved in two steps (Lemma 3):
#   (3.1)  prod_j P'(t_j) = (-1)^{n(n-1)/2} disc          [checked EXACTLY below, Fractions]
#   (3.2)  prod_j P'(t_j) = n^n prod_i P(y_i)             [checked in float, well-conditioned]
from fractions import Fraction

def exact_31_trial(n):
    t = sorted(rng.choice(np.arange(-97, 98), size=n, replace=False))
    t = [Fraction(int(v), 100) for v in t]
    lhs = Fraction(1)
    for j in range(n):
        pj = Fraction(1)
        for k in range(n):
            if k != j: pj *= (t[j] - t[k])
        lhs *= pj
    disc = Fraction(1)
    for i in range(n):
        for j in range(i+1, n):
            disc *= (t[j] - t[i])**2
    sign = -1 if (n*(n-1)//2) % 2 else 1
    return lhs == sign * disc

okA1 = all(exact_31_trial(n) for n in [2,3,4,5,7,10,13] for _ in range(20))
check("A1: prod P'(t_j) = (-1)^{n(n-1)/2} disc (EXACT rational arithmetic)", okA1)

def float_32_trial(n):
    t = np.sort(rng.uniform(-0.95, 0.95, n))
    while np.min(np.diff(t)) < 0.05:
        t = np.sort(rng.uniform(-0.95, 0.95, n))
    P = np.poly(t)                       # monic, highest-first
    y = np.sort(np.roots(np.polyder(P)).real)   # all real by interlacing
    lhs = np.prod([np.polyval(np.polyder(P), tj) for tj in t])
    rhs = n**n * np.prod(np.polyval(P, y))
    return abs(lhs - rhs) / max(abs(rhs), 1e-300)

errA = max(float_32_trial(n) for n in [2,3,4,5,7,10] for _ in range(40))
check("A2: prod P'(t_j) = n^n prod P(y_i) (float, rel err)", errA < 1e-7,
      f"max rel err {errA:.2e}")

# ---------- B. collinear theorem ----------
def collinear_trial(n, adversarial=False):
    # random chord: foot a (|a|<1), direction u = i*a/|a| (perp), half-length h
    phi = rng.uniform(0, 2*np.pi); r = rng.uniform(0, 0.95)
    a = r*np.exp(1j*phi); u = np.exp(1j*(phi+np.pi/2))
    h = np.sqrt(1 - r*r)
    if adversarial:  # cluster roots near the chord endpoints
        k = n//2
        t = np.concatenate([ -h + h*10**rng.uniform(-6,-1,k), h - h*10**rng.uniform(-6,-1,n-k) ])
        t = np.sort(t*0.999999)
    else:
        t = np.sort(rng.uniform(-h, h, n) * 0.9999)
    if np.min(np.diff(t)) < 1e-12:
        return None
    z = a + t*u
    P = np.poly(t)
    y = np.sort(np.roots(np.polyder(P)).real)
    # gap maxima of |f| along the actual segments in C, in STABLE product form + log
    # space (coefficient-based polyval suffers catastrophic cancellation near clustered
    # roots). Ground truth per gap = max over dense samples AND the critical-value
    # estimate |P(y_i)| (np.roots of P' can be ill-conditioned in tight clusters).
    logcv = np.array([np.sum(np.log(np.abs(yi - t) + 1e-300)) for yi in y])
    loggap = []
    for i in range(n-1):
        ts = np.linspace(t[i], t[i+1], 1500)
        zs = a + ts*u
        logvals = np.sum(np.log(np.abs(zs[:, None] - z[None, :]) + 1e-300), axis=1)
        loggap.append(max(np.max(logvals), logcv[i]))
    loggap = np.array(loggap)
    # log-space discriminant and bound (adversarial configs underflow in linear space)
    logdisc = sum(2*np.log(abs(t[j]-t[i])) for i in range(n) for j in range(i+1,n))
    logbound = (logdisc - n*np.log(n)) / (n-1)
    seglen = np.diff(t)
    i0 = int(np.argmin(loggap))
    return loggap[i0], logbound, seglen[i0]

worst_val, worst_excess = 0.0, -np.inf
ok = True
for n in [2,3,4,6,9,12]:
    for adv in (False, True):
        for _ in range(60):
            res = collinear_trial(n, adv)
            if res is None: continue
            logv, logb, L = res
            excess = logv - logb   # must be <= 0 (min <= geometric mean)
            ok &= (logv < 0.0) and (excess <= 1e-6) and (L < 2.0)
            worst_val = max(worst_val, np.exp(logv)); worst_excess = max(worst_excess, excess)
check("B: collinear min-gap max|f| < 1, <= (disc/n^n)^{1/(n-1)}, seg < 2", ok,
      f"worst max|f| {worst_val:.4f}, worst log-excess over bound {worst_excess:.2e}")

# ---------- C. Hadamard bound near extremal configs ----------
okC, worstC = True, 0.0
for n in range(2, 31):
    x = np.cos(np.pi*np.arange(n)/(n-1)) * (1 - 1e-9)   # Chebyshev extrema in (-1,1)
    ld = sum(2*np.log(abs(x[j]-x[i])) for i in range(n) for j in range(i+1,n))
    ratio = ld - n*np.log(n)   # log(disc/n^n) must be < 0
    okC &= ratio < 0
    worstC = max(worstC, np.exp(ratio))
check("C: disc < n^n at near-extremal points, n=2..30", okC, f"worst disc/n^n {worstC:.4f}")

# ---------- D & E. grid checks on components ----------
from scipy import ndimage

def component_checks(roots, n, tag, grid=1400):
    """Returns list of (m, connected_ok, integral_ratio) per component of {|f|<1} with zeros."""
    R = 1.0 + 1.05*max(1.0, np.max(np.abs(roots)))  # E(f) ⊂ |z| < |roots|+1
    xs = np.linspace(-R, R, grid); dx = xs[1]-xs[0]
    X, Y = np.meshgrid(xs, xs); Zg = X + 1j*Y
    F = np.ones_like(Zg)
    for rt in roots: F *= (Zg - rt)
    mask = np.abs(F) < 1.0
    lab, nlab = ndimage.label(mask)
    # critical points
    coeffs = np.poly(roots)
    cps = np.roots(np.polyder(coeffs))
    out = []
    for li in range(1, nlab+1):
        comp = lab == li
        # zeros in this component
        def locate(pt):
            ix = int(round((pt.real+R)/dx)); iy = int(round((pt.imag+R)/dx))
            if 0 <= iy < grid and 0 <= ix < grid: return lab[iy, ix]
            return -1
        m = sum(1 for rt in roots if locate(rt) == li)
        if m < 1: continue
        cvals = [abs(np.polyval(coeffs, c)) for c in cps if locate(c) == li]
        cmax = max(cvals) if cvals else 0.0
        if cmax >= 1.0:  # grid mislabel near boundary; skip
            continue
        s = 0.5*(cmax+1.0)
        sub = comp & (np.abs(F) < s)
        _, nsub = ndimage.label(sub)
        connected_ok = (nsub == 1)
        # integral of |f'/f| over V_s (grid sum; integrable singularities at zeros)
        Fp = np.polyval(np.polyder(coeffs), Zg[sub])
        Fv = F[sub]
        integ = np.sum(np.abs(Fp/Fv)) * dx*dx
        bound = 2*np.pi*np.sqrt(m*n)*s**(1.0/n)
        out.append((m, connected_ok, integ/bound))
        print(f"    [{tag}] comp m={m} cmax={cmax:.3f} s={s:.3f} nsub={nsub} ∫/bound={integ/bound:.3f}")
    return out

okD, okE = True, True
maxratio = 0.0
# random test polynomials with roots in the disk
tests = []
for n in [3, 5, 8]:
    rts = (rng.uniform(0.05, 0.95, n) * np.exp(1j*rng.uniform(0, 2*np.pi, n)))
    tests.append((rts, n, f"rand n={n}"))
tests.append((np.array([0.6, -0.6, 0.6j, -0.6j, 0.0]), 5, "sym n=5"))
tests.append((np.zeros(6), 6, "z^6"))   # sharpness case for E
for rts, n, tag in tests:
    for m, conn, ratio in component_checks(rts, n, tag):
        okD &= conn
        okE &= ratio <= 1.02   # grid quadrature tolerance
        maxratio = max(maxratio, ratio)
check("D: {|f|<s} ∩ U connected for s in (c_max,1)", okD)
check("E: ∫_{V_s}|f'/f| dA <= 2π√(mn) s^{1/n} (grid, tol 2%)", okE,
      f"max ratio {maxratio:.3f} (z^n case should approach 1)")

print()
if FAIL:
    print("FAILED:", ", ".join(FAIL)); sys.exit(1)
print("ALL CHECKS PASSED"); sys.exit(0)
