"""Scan product-construction seeds at bases beyond Walker's k=4 search range.

Walker (arXiv:2203.06045v2) searched 4-free sets mod b only for b <= 200.
Product theorem (proof in README.md): if S1 is 4-free mod b1 and S2 is
4-free mod b2 then S1 + b1*S2 is 4-free mod b1*b2.  This builds certified
4-free digit sets at bases 605, 1210, 3025, ... on which we then local-search.

Outputs results/products.json ranked by certified harmonic-sum lower bound.
"""
import itertools
import json
import sys
import time

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from kempner import (is_kfree_mod, harmonic_sum_bounds, product_digit_set,
                     addable_digits)

# --- Walker's Table 1 (transcribed from arXiv:2203.06045v2, p.7) ----------
TABLE1 = [
    (4.43975, 55, [0,1,2,4,5,9,10,11,14,16,17,18,21,24,30,37,39,41,42,45,47]),
    (4.42175, 11, [0,1,2,4,5,7]),
    (4.41989, 22, [0,1,2,4,5,7,8,9,14,17]),
    (4.39620, 191, [0,1,2,4,5,7,8,9,14,16,17,18,26,30,31,32,36,37,39,40,42,
                    50,51,55,56,58,59,62,64,67,69,70,77,81,83,87,91,94,102,
                    109,110,111,113,117,119,120,122,123,125,127]),
    (4.37859, 177, [0,1,2,4,5,7,8,9,14,16,17,18,22,29,30,31,34,35,37,39,42,
                    45,47,49,57,58,61,63,65,66,70,71,72,78,80,81,82,89,96,
                    100,102,108,110,116,136,149]),
    (4.37699, 193, [0,1,2,4,5,7,8,9,14,16,17,18,22,29,30,31,34,35,37,39,42,
                    45,47,49,57,58,60,61,64,65,66,70,71,72,74,92,96,100,102,
                    106,110,113,116,117,118,122,124,125,157]),
    (4.37665, 157, [0,1,2,4,5,7,8,9,14,16,17,18,22,28,29,30,32,35,36,37,39,
                    45,57,59,61,62,67,68,69,71,75,76,78,80,84,95,104,108,115,
                    119,137,142,146]),
    (4.37583, 97, [0,1,2,4,5,7,8,17,18,20,21,23,24,25,30,32,37,45,48,54,56,
                   58,59,61,63,64,66,68,74,77,85,90,92]),
    (4.37486, 193, [0,1,2,4,5,7,8,9,14,16,17,18,22,29,30,31,34,35,37,39,42,
                    45,47,49,57,58,60,61,64,65,66,70,71,72,74,92,96,100,102,
                    106,113,116,117,118,122,124,125,128,157]),
    (4.37406, 105, [0,1,2,4,5,7,8,9,15,16,18,19,20,25,26,28,29,31,32,33,36,
                    45,50,51,59,61,63,68,70,72,79]),
]

MAX_PRODUCT_BASE = 6200
ENCLOSURE_TARGET = 1e-6
MAX_ENUM = 4 * 10 ** 7  # cap on m^depth for evaluation


def eval_enclosure(S, b):
    """Adaptive-depth certified enclosure."""
    m = len(S)
    depth = 2
    while True:
        lo, hi = harmonic_sum_bounds(S, b, depth)
        if float(hi - lo) <= ENCLOSURE_TARGET or m ** (depth + 1) > MAX_ENUM:
            return lo, hi, depth
        depth += 1


def best_small_base_sets(bmax=14):
    """Exhaust all digit sets containing 0 for tiny bases; keep the max-H set
    per base (product components)."""
    out = []
    for b in range(3, bmax + 1):
        best = None
        for r in range(1, b):
            for comb in itertools.combinations(range(1, b), r):
                S = [0] + list(comb)
                if not is_kfree_mod(S, b, 4):
                    continue
                lo, hi, _ = eval_enclosure(S, b)
                if best is None or lo > best[0]:
                    best = (lo, hi, S)
        if best:
            out.append((float(best[0]), b, best[2]))
    return out


if __name__ == "__main__":
    t_start = time.time()

    # 1. validate transcription of Table 1
    library = []
    for h_pub, b, S in TABLE1:
        assert is_kfree_mod(S, b, 4), f"transcription error: b={b} not 4-free"
        lo, hi, depth = eval_enclosure(S, b)
        err = abs(float(lo) - h_pub)
        status = "OK" if err < 5e-5 else "MISMATCH"
        print(f"table1 b={b:4d} |S|={len(S):3d} published={h_pub:.5f} "
              f"certified=[{float(lo):.7f},{float(hi):.7f}] {status}")
        assert err < 5e-5, f"transcription error: b={b} H off by {err}"
        library.append((b, S, float(lo)))

    # 2. tiny-base components
    print("\nexhausting tiny bases (components only) ...")
    for h, b, S in best_small_base_sets(12):
        print(f"tiny  b={b:4d} S={S} H={h:.5f}")
        library.append((b, S, h))

    # 3. ordered products
    print("\nscanning ordered products with b1*b2 <=", MAX_PRODUCT_BASE)
    results = []
    for (b1, S1, h1), (b2, S2, h2) in itertools.product(library, repeat=2):
        B = b1 * b2
        if B > MAX_PRODUCT_BASE:
            continue
        S = product_digit_set(S1, b1, S2)
        assert is_kfree_mod(S, B, 4), \
            f"PRODUCT THEOREM VIOLATED at ({b1},{b2})"  # theorem test
        lo, hi, depth = eval_enclosure(S, B)
        n_add = len(addable_digits(S, B, 4)) if B <= 3200 else -1
        results.append({
            "b": B, "b1": b1, "b2": b2, "m": len(S),
            "H_lo": float(lo), "H_hi": float(hi), "depth": depth,
            "addable": n_add, "S": S,
        })
        print(f"product {b1:4d}x{b2:<4d} b={B:5d} m={len(S):4d} "
              f"H=[{float(lo):.7f},{float(hi):.7f}] addable={n_add}")

    results.sort(key=lambda r: -r["H_lo"])
    with open(__file__.rsplit("/", 2)[0] + "/results/products.json", "w") as f:
        json.dump({"record_bar": 4.439753370, "results": results}, f, indent=1)

    print(f"\ntop products by certified lower bound "
          f"({time.time()-t_start:.0f}s total):")
    for r in results[:10]:
        print(f"  b={r['b']:5d} ({r['b1']}x{r['b2']}) m={r['m']:4d} "
              f"H_lo={r['H_lo']:.7f} addable={r['addable']}")
