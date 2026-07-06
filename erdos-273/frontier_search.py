"""
Exact covering search over Z/L for the reduced admissible CORE at a given bound
M, using in-place undo backtracking (single uint8 count array, no per-node
copies). Branches on the least-uncovered point; each modulus's residue is forced
to cover it. Prunes when remaining coverage capacity < remaining uncovered.

Emits a deterministic exhaustion log. If it returns UNSAT, no covering system
exists using admissible moduli <= M (the core is equivalent to the full set).
If it returns a model, that model is a WITNESS (verified before printing).

Usage: python frontier_search.py <M> [time_budget_seconds]
"""
import sys
import time
import numpy as np
from admissible import admissible_moduli, reduce_local_density, lcm
from cover_sat import covers


def search(core, L, time_budget=300.0):
    moduli = sorted(core)               # ascending; coarse moduli first as tie
    k = len(moduli)
    cap_each = [L // m for m in moduli]  # points each modulus covers
    count = np.zeros(L, dtype=np.uint8)  # how many chosen classes cover each pt
    uncovered = L                        # number of points with count==0
    used = [False] * k
    assign = []
    t0 = time.time()
    stats = {"nodes": 0, "timeout": False, "max_depth": 0}

    # remaining capacity if we still have moduli i with used[i] False
    def remaining_cap():
        return sum(cap_each[i] for i in range(k) if not used[i])

    def rec(depth):
        nonlocal uncovered
        stats["nodes"] += 1
        stats["max_depth"] = max(stats["max_depth"], depth)
        if time.time() - t0 > time_budget:
            stats["timeout"] = True
            return None
        if uncovered == 0:
            return list(assign)
        # capacity prune
        if remaining_cap() < uncovered:
            return None
        x = int(np.argmin(count))       # least uncovered point (count==0)
        for i in range(k):
            if used[i]:
                continue
            m = moduli[i]
            a = x % m
            sl = count[a::m]
            newly = int(np.count_nonzero(sl == 0))
            sl += 1                      # in-place assign
            used[i] = True
            assign.append((a, m))
            uncovered -= newly
            res = rec(depth + 1)
            if res is not None:
                return res
            # undo
            assign.pop()
            used[i] = False
            uncovered += newly
            sl -= 1
        return None

    model = rec(0)
    elapsed = time.time() - t0
    return model, stats, elapsed


def main():
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 280
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 300.0
    S = admissible_moduli(M)
    core, log = reduce_local_density(S)
    L = lcm(core) if core else 1
    csum = sum(1.0 / m for m in core)
    print(f"M={M}: |S|={len(S)}  |core|={len(core)}  lcm(core)={L}  "
          f"sum(1/m over core)={csum:.6f}")
    print(f"core = {core}")
    if not core:
        print("RESULT: core empty -> NO covering system (uncoverable). "
              "No search needed.")
        return
    if csum < 1.0:
        print(f"RESULT: core reciprocal sum {csum:.6f} < 1 "
              "-> NO covering system (uncoverable). Root-prune certificate.")
        return
    print(f"core sum >= 1: running exact backtracking search "
          f"(budget {budget:.0f}s) over Z/{L} ...")
    model, stats, elapsed = search(core, L, budget)
    print(f"  nodes={stats['nodes']} max_depth={stats['max_depth']} "
          f"elapsed={elapsed:.1f}s timeout={stats['timeout']}")
    if model is not None:
        ok, bad = covers(model, L)
        print(f"WITNESS FOUND (verified={ok}): {sorted(model, key=lambda t:t[1])}")
    elif stats["timeout"]:
        print(f"RESULT: INCONCLUSIVE within {budget:.0f}s "
              f"(explored {stats['nodes']} nodes). Frontier remains open at M={M}.")
    else:
        print(f"RESULT: UNSAT by exhaustion -> NO covering system using "
              f"admissible moduli <= {M}. (nodes={stats['nodes']})")


if __name__ == "__main__":
    main()
