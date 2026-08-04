# Erdos #388 case (6,4): independent integral-point computation in SageMath.
# Curve C: u^2 = t^3 + 10 t^2 + 24 t + 1  (model [0,10,0,24,1])
# Run: mamba run -n e388sage sage case64_sage.sage
E = EllipticCurve([0, 10, 0, 24, 1])
print("curve:", E.ainvs())
print("minimal model:", E.minimal_model().ainvs())
print("conductor:", E.conductor().factor())
print("torsion:", E.torsion_order())
print("rank (proven bounds):", E.rank(only_use_mwrank=False), "certified:", E.rank_bounds())
gens = E.gens(proof=True)
print("MW generators (proof=True):", gens)
pts = E.integral_points(both_signs=True)
print("integral points (both signs):", sorted((P[0], P[1]) for P in pts))
# filter to Erdos-388 (6,4) solutions: t = x^2+7x+6, u = y^2+5y+5, x,y >= 1
sols = []
for P in pts:
    t, u = P[0], P[1]
    d1 = 4*t + 25
    if d1 >= 0 and Integer(d1).is_square():
        a = sqrt(Integer(d1))
        for xx in [(a - 7)/2, (-a - 7)/2]:
            if xx in ZZ and xx >= 1:
                d2 = 4*u + 5
                if d2 >= 0 and Integer(d2).is_square():
                    b = sqrt(Integer(d2))
                    for yy in [(b - 5)/2, (-b - 5)/2]:
                        if yy in ZZ and yy >= 1:
                            sols.append((xx, yy))
print("positive-integer solutions (x,y) of (x+1)..(x+6)=(y+1)..(y+4):", sorted(set(sols)))
