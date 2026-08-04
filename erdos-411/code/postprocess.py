#!/usr/bin/env python3
"""Post-process raw sweep hits into certificates + primitive witness catalogue.

Input: a hits file with lines "H x r c" (raw multiplier hits g_r(x) = c*x)
       produced by sweep.c (or probe.py converted), plus X (max x) and R (max r).
Output (JSON to stdout):
  - all raw hits;
  - all certificate triples (x, r, c) with orbit prefix g_0..g_r;
  - primitive reduction (power / orbit-membership / scaling / merge closure);
  - A383044 cross-check for the (r,c)=(2,2) certificate points.

Usage: postprocess.py hits.txt X R > catalogue.json
"""
import sys, json
from probe import phi_sieve, phi_big, rad

SIEVE = 20_000_000
_phi = None
_cache = {}

def g(v):
    return v + (_phi[v] if v <= SIEVE else phi_big(v, _cache))

def main():
    global _phi
    hits_file, X, R = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    _phi = phi_sieve(SIEVE)

    byx = {}
    for line in open(hits_file):
        parts = line.split()
        if not parts or parts[0] != "H":
            continue
        x, r, c = int(parts[1]), int(parts[2]), int(parts[3])
        byx.setdefault(x, []).append((r, c))

    # certificate filter (orbit computed once per x, to max needed r)
    certs = []
    for x in sorted(byx):
        rmax = max(r for r, _ in byx[x])
        orbit = [x]
        v = x
        for _ in range(rmax):
            v = g(v)
            orbit.append(v)
        for (r, c) in sorted(byx[x]):
            assert orbit[r] == c * x, (x, r, c)   # re-check the C sweep's arithmetic
            radc = rad(c)
            if all(orbit[j] % radc == 0 for j in range(r)):
                certs.append({"x": x, "r": r, "c": c, "orbit": orbit[:r + 1]})

    # primitive reduction
    bykey, bx = {}, {}
    for cd in certs:
        bykey.setdefault((cd["r"], cd["c"]), []).append(cd)
        bx.setdefault(cd["x"], []).append(cd)
    prim = []
    for cd in certs:
        x, r, c, orbit = cd["x"], cd["r"], cd["c"], cd["orbit"]
        st = None
        for cd0 in bx[x]:                                   # power
            r0, c0 = cd0["r"], cd0["c"]
            if r0 < r and r % r0 == 0 and c0 ** (r // r0) == c:
                st = f"power-{r//r0}-of-(r={r0},c={c0})"; break
        if st is None:                                       # forward orbit of smaller
            for cd0 in bykey[(r, c)]:
                if cd0["x"] < x and x in cd0["orbit"]:
                    st = f"orbit-of-{cd0['x']}"; break
        if st is None:                                       # scaling of smaller
            for cd0 in bykey[(r, c)]:
                y = cd0["x"]
                if y < x and x % y == 0:
                    s = x // y
                    rs = rad(s)
                    if all(v % rs == 0 for v in cd0["orbit"][:r]) and \
                       all(orbit[j] == s * cd0["orbit"][j] for j in range(r + 1)):
                        st = f"scale-{s}x-of-{y}"; break
        cd["status"] = st or "primitive"
        if st is None:
            prim.append(cd)

    # orbit-merge closure among primitives: extend orbits 80 steps (or to 1e16)
    prim.sort(key=lambda d: d["x"])
    reach = {}
    final = []
    for cd in prim:
        key = (cd["r"], cd["c"])
        if cd["x"] in reach.get(key, set()):
            cd["status"] = "orbit-merge"; continue
        final.append(cd)
        s = reach.setdefault(key, set())
        v = cd["x"]
        for _ in range(80):
            v = g(v)
            if v > 10 ** 16:
                break
            s.add(v)

    # A383044 cross-check: (2,2)-certificate points up to min(X, 8960)
    a383044 = [4,6,8,10,12,14,16,20,24,28,32,40,48,56,64,70,80,94,96,112,128,140,
               160,188,192,224,256,280,320,376,384,448,512,560,640,752,768,896,1024,
               1120,1280,1504,1536,1792,2048,2240,2560,3008,3072,3584,4096,4480,5120,
               6016,6144,7168,8192,8960]
    ours22 = sorted(cd["x"] for cd in certs if (cd["r"], cd["c"]) == (2, 2)
                    and cd["x"] <= 8960)
    from probe import factorize
    for cd in final:
        f = factorize(cd["x"])
        cd["factorization"] = " * ".join((f"{p}^{e}" if e > 1 else str(p))
                                         for p, e in sorted(f.items()))
    out = {"X": X, "R": R,
           "n_raw_hits": sum(len(v) for v in byx.values()),
           "n_certificates": len(certs),
           "n_primitive": len(final),
           "primitive": [{k: cd[k] for k in ("x", "r", "c", "factorization")}
                         for cd in final],
           "certificates": [{k: cd[k] for k in ("x", "r", "c", "status", "orbit")}
                            for cd in certs],
           "A383044_check": {"expected": a383044, "ours": ours22,
                             "match": ours22 == a383044}}
    json.dump(out, sys.stdout, indent=1)
    sys.stderr.write(f"raw={out['n_raw_hits']} certs={len(certs)} primitive={len(final)} "
                     f"A383044={out['A383044_check']['match']}\n")

if __name__ == "__main__":
    main()
