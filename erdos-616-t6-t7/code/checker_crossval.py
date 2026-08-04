#!/usr/bin/env python3
"""Cross-validation of the DFS local-property checker (full_local_check in
random_maximal_search.py) against an independent literal-definition oracle:
for every vertex subset S with r <= |S| <= 3r-3, the edges contained in S must
share a vertex. Random families are drawn WITHOUT filtering, so both
L-satisfying and L-violating families occur and agreement is two-sided (the
test has failure power in both directions).

Added by the pre-publication referee pass (2026-08-03): the original session
ran this cross-validation ephemerally ("400 random families" in the attack
report) without archiving it; this script makes it reproducible. The referee's
own independent run (different seed/implementation) also agreed on 400/400.
"""
import random
import sys
from itertools import combinations

from random_maximal_search import full_local_check, edge_mask

def literal_L(family, r, n):
    w = 3 * r - 3
    for size in range(r, w + 1):
        for S in combinations(range(n), size):
            Sm = 0
            for v in S:
                Sm |= 1 << v
            inter = -1
            found = False
            for E in family:
                if E & Sm == E:
                    inter &= E
                    found = True
            if found and inter == 0:
                return False
    return True

def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    rng = random.Random(616400)
    sat = 0
    for t in range(trials):
        r = rng.choice([6, 6, 6, 7])
        n = rng.randint(3 * r - 5, 3 * r - 2)  # keep the literal oracle cheap
        k = rng.randint(2, 7)
        fam = []
        seen = set()
        while len(fam) < k:
            e = tuple(sorted(rng.sample(range(n), r)))
            if e not in seen:
                seen.add(e)
                fam.append(edge_mask(e))
        a = full_local_check(fam, 3 * r - 3, r + 1)
        b = literal_L(fam, r, n)
        assert a == b, (f"CHECKER DISAGREEMENT trial {t}: dfs={a} literal={b} "
                        f"r={r} n={n} fam={fam}")
        sat += a
    print(f"{trials} random families: DFS checker and literal-definition oracle "
          f"agree on all (satisfying: {sat}, violating: {trials - sat})")
    print("CHECKER CROSS-VALIDATION PASSED")

if __name__ == "__main__":
    main()
