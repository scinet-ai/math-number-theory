#!/usr/bin/env python3
"""Reduce probe/sweep certificates to primitive witness orbits.

A certificate triple (x, r, c) [with orbit prefix] is discarded as DERIVED if:
  P1 (power):    there is a certificate (x, r0, c0) with r = j*r0, c = c0^j, j >= 2;
  P2 (orbit):    x = g_m(y) for an earlier certificate point y with the same (r, c)
                 (checked via forward-orbit membership of listed certificate points);
  P3 (scaling):  x = s*y for a certificate (y, r, c) with s >= 2 and, for every
                 orbit point of y in the certificate window, rad(s) | g_j(y)
                 (then g_j(x) = s*g_j(y) for all j: scaling lemma).
Remaining triples are PRIMITIVE witness orbits.
Usage: analyze.py probe_output.json
"""
import sys, json, math
from probe import factorize, rad

def main():
    data = json.load(open(sys.argv[1]))
    certs = data["certificates"]
    bykey = {}          # (r,c) -> list of cert dicts
    byx = {}            # x -> list of cert dicts
    for cdict in certs:
        bykey.setdefault((cdict["r"], cdict["c"]), []).append(cdict)
        byx.setdefault(cdict["x"], []).append(cdict)

    prim = []
    for cd in certs:
        x, r, c, orbit = cd["x"], cd["r"], cd["c"], cd["orbit"]
        # P1: power of a shorter relation at the same x
        derived = False
        for cd0 in byx[x]:
            r0, c0 = cd0["r"], cd0["c"]
            if r0 < r and r % r0 == 0 and c0 ** (r // r0) == c:
                derived = True; break
        if derived:
            cd["status"] = "derived-power"; continue
        # P2: x lies on the forward orbit of an earlier same-(r,c) cert point
        for cd0 in bykey[(r, c)]:
            if cd0["x"] < x and x in cd0["orbit"]:
                derived = True
                cd["status"] = f"orbit-of-{cd0['x']}"
                break
        if derived:
            continue
        # P3: scaling of a smaller same-(r,c) cert point
        for cd0 in bykey[(r, c)]:
            y = cd0["x"]
            if y < x and x % y == 0:
                s = x // y
                rs = rad(s)
                if all(v % rs == 0 for v in cd0["orbit"][:r]):
                    if all(orbit[j] == s * cd0["orbit"][j] for j in range(r + 1)):
                        derived = True
                        cd["status"] = f"scale-{s}x-of-{y}"
                        break
        if derived:
            continue
        cd["status"] = "primitive"
        prim.append(cd)

    # P2 across different starts whose orbits merge later: also mark x primitive
    # only if no smaller primitive's orbit (extended) reaches x.  Extend orbits:
    from probe import phi_sieve, phi_big
    SIEVE = 4_000_000
    phi = phi_sieve(SIEVE)
    cache = {}
    def g(v):
        return v + (phi[v] if v <= SIEVE else phi_big(v, cache))
    # extend each primitive orbit forward 60 steps, drop later primitives that appear
    prim.sort(key=lambda d: d["x"])
    reach = {}  # (r,c) -> set of reachable values
    final = []
    for cd in prim:
        key = (cd["r"], cd["c"])
        if cd["x"] in reach.get(key, ()):  # noqa
            cd["status"] = "orbit-merge"
            continue
        final.append(cd)
        s = reach.setdefault(key, set())
        v = cd["x"]
        for _ in range(60):
            v = g(v)
            if v > 10**13:
                break
            s.add(v)

    for cd in final:
        f = factorize(cd["x"])
        cd["factorization"] = " * ".join(
            (f"{p}^{e}" if e > 1 else str(p)) for p, e in sorted(f.items()))
    print(json.dumps({"n_certificates": len(certs),
                      "n_primitive": len(final),
                      "primitive": [{k: cd[k] for k in ("x", "r", "c", "factorization")}
                                    for cd in final]}, indent=1))

if __name__ == "__main__":
    main()
