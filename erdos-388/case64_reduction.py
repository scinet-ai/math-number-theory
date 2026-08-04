#!/usr/bin/env python3
"""Erdos #388, case (k1,k2)=(6,4): symbolic verification of the reduction
   (x+1)(x+2)(x+3)(x+4)(x+5)(x+6) = (y+1)(y+2)(y+3)(y+4)
      <=>  u^2 = t^3 + 10 t^2 + 24 t + 1
   with t = x^2+7x+6, u = y^2+5y+5,
plus curve invariants, an integral-point search up to a large height bound,
and the filter recovering (x,y) from integral points (t,u)."""
import sympy as sp
from sympy import symbols, expand, simplify, Integer, isprime, factorint, sqrt

x, y, t, u = symbols('x y t u')

# ---------- 1. Symbolic identities ----------
P6 = expand(sp.prod([x + i for i in range(1, 7)]))
P4 = expand(sp.prod([y + i for i in range(1, 5)]))

T = x**2 + 7*x + 6
U = y**2 + 5*y + 5

id1 = expand(P6 - (T * (T + 4) * (T + 6)))          # must be 0
id2 = expand(P4 + 1 - U**2)                          # must be 0
print("identity (x+1)..(x+6) == t(t+4)(t+6) with t=x^2+7x+6 :", id1 == 0)
print("identity (y+1)..(y+4)+1 == (y^2+5y+5)^2            :", id2 == 0)

# equation P6 = P4  <=>  t(t+4)(t+6) = u^2 - 1  <=>  u^2 = t^3+10t^2+24t+1
cubic = expand(t * (t + 4) * (t + 6) + 1)
print("u^2 =", cubic)

# ---------- 2. Curve invariants (a1=a3=0, a2=10, a4=24, a6=1) ----------
a1, a2, a3, a4, a6 = 0, 10, 0, 24, 1
b2 = a1**2 + 4*a2
b4 = 2*a4 + a1*a3
b6 = a3**2 + 4*a6
b8 = a1**2*a6 + 4*a2*a6 - a1*a3*a4 + a2*a3**2 - a4**2
c4 = b2**2 - 24*b4
c6 = -b2**3 + 36*b2*b4 - 216*b6
Delta = -b2**2*b8 - 8*b4**3 - 27*b6**2 + 9*b2*b4*b6
print("Delta =", Delta, "=", factorint(Delta))
print("c4 =", c4, "=", factorint(c4))
j = sp.Rational(c4**3, Delta)
print("j =", j, "=", sp.factorint(sp.Rational(j).p), "/", sp.factorint(sp.Rational(j).q))
# Delta is 12th-power-free => this model has minimal discriminant.

# ---------- 3. Integral-point search on u^2 = t^3+10t^2+24t+1, |t| <= B ----------
import math

def f(tv):
    return tv**3 + 10*tv**2 + 24*tv + 1

B = 10**7
pts = []
for tv in range(-10, B + 1):
    v = f(tv)
    if v >= 0:
        r = math.isqrt(v)
        if r * r == v:
            pts.append((tv, r))
print("integral points with -10 <= t <= 10^7 (u >= 0):", pts)

# ---------- 4. Filter: which points come from positive integers x,y ----------
# t = x^2+7x+6  <=>  4t+25 = (2x+7)^2 ;  u = y^2+5y+5  <=>  4u+5 = (2y+5)^2
print("\nfilter to (x,y) with x,y positive integers:")
sols = []
for (tv, uv) in pts:
    d1 = 4*tv + 25
    if d1 < 0:
        continue
    r1 = sp.integer_nthroot(d1, 2)
    if not r1[1]:
        continue
    for sgn_x in (+1, -1):
        xx = sp.Rational(sgn_x * r1[0] - 7, 2)
        if xx != int(xx) or xx < 1:
            continue
        for su in (uv, -uv):
            d2 = 4*su + 5
            if d2 < 0:
                continue
            r2 = sp.integer_nthroot(d2, 2)
            if not r2[1]:
                continue
            for sgn_y in (+1, -1):
                yy = sp.Rational(sgn_y * r2[0] - 5, 2)
                if yy != int(yy) or yy < 1:
                    continue
                sols.append((int(xx), int(yy), tv, su))
sols = sorted(set(sols))
for (xx, yy, tv, uv) in sols:
    lhs = sp.prod([xx + i for i in range(1, 7)])
    rhs = sp.prod([yy + i for i in range(1, 5)])
    dis = "DISJOINT" if xx + 6 <= yy else "OVERLAP"
    print(f"  x={xx} y={yy}  ({xx+1}..{xx+6})=({yy+1}..{yy+4})  {lhs}=={rhs}: {lhs==rhs}  {dis}")

# ---------- 5. Direct brute-force cross-check on the original equation ----------
# For x up to 2*10^6, test whether P6(x) is a product of 4 consecutive integers:
# P6+1 must be a perfect square (y^2+5y+5)^2 with y integer.
found = []
for xx in range(1, 2 * 10**6 + 1):
    p6 = (xx+1)*(xx+2)*(xx+3)*(xx+4)*(xx+5)*(xx+6)
    r = math.isqrt(p6 + 1)
    if r * r == p6 + 1:
        d2 = 4*r + 5
        r2 = math.isqrt(d2)
        if r2 * r2 == d2 and (r2 - 5) % 2 == 0:
            yy = (r2 - 5) // 2
            if yy >= 1:
                found.append((xx, yy))
print("\ndirect search x <= 2*10^6:", found)

# ---------- 6. LMFDB curve 10388.b1: transform + integral point list ----------
# Shift t = X - 3 maps our model to Y^2 = X^3 + X^2 - 9X - 8 (LMFDB 10388.b1).
X = symbols('X')
shift_id = expand((X - 3)**3 + 10*(X - 3)**2 + 24*(X - 3) + 1 - (X**3 + X**2 - 9*X - 8))
print("\nshift identity (t=X-3) maps to 10388.b1 model:", shift_id == 0)

# Complete integral point list of 10388.b1 per LMFDB (accessed 2026-08-03):
lmfdb_X = [-3, -1, 3, 4, 17, 41, 137]
lmfdb_pts = [(-3, 1), (-1, 1), (3, 1), (4, 6), (17, 71), (41, 265), (137, 1609)]
# check they lie on 10388.b1 and map exactly onto our search list
ok = all(Y**2 == Xv**3 + Xv**2 - 9*Xv - 8 for (Xv, Y) in lmfdb_pts)
print("LMFDB points lie on 10388.b1:", ok)
mapped = sorted((Xv - 3, Y) for (Xv, Y) in lmfdb_pts)
print("LMFDB points mapped by t=X-3 :", mapped)
print("matches independent search   :", mapped == sorted(pts))
assert ok and mapped == sorted(pts)
