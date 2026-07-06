"""
Exact covering-existence over Z/L for a set of moduli.

Question solved: given distinct moduli m_1..m_k (all dividing L = lcm), does there
exist a choice of residues a_i (one per modulus) such that every integer is in
some class a_i mod m_i, i.e. the classes cover Z/L?

Two independent engines (they must agree -- cross-check):
  1. SAT (pysat / Cadical): one-hot residue vars + one "covered" clause per point.
  2. Backtracking bitset search (numpy): pick least uncovered point, branch over
     which unassigned modulus covers it (residue forced). Returns a witness or
     proves UNSAT by exhaustion.

Plus a standalone VERIFIER `covers()` that checks a concrete assignment.
"""
import numpy as np


# ---------------------------------------------------------------- verifier
def covers(assignment, L=None):
    """assignment: list of (a, m). Returns (is_cover, first_uncovered_or_None).
    Checks that classes a mod m cover every residue 0..L-1, L=lcm(moduli)."""
    from admissible import lcm
    if L is None:
        L = lcm([m for _, m in assignment])
    covered = np.zeros(L, dtype=bool)
    for a, m in assignment:
        covered[(a % m)::m] = True
    if covered.all():
        return True, None
    return False, int(np.argmin(covered))


# ---------------------------------------------------------------- SAT engine
def solve_sat(moduli, L, want_model=True):
    """Returns (sat: bool, model_or_None). model is list of (a, m)."""
    from pysat.solvers import Cadical195
    from pysat.formula import IDPool
    vp = IDPool()

    def y(m, r):
        return vp.id((m, r % m))

    solver = Cadical195()
    # exactly-one residue per modulus: at-least-one + pairwise at-most-one.
    for m in moduli:
        solver.add_clause([y(m, r) for r in range(m)])
        for r1 in range(m):
            for r2 in range(r1 + 1, m):
                solver.add_clause([-y(m, r1), -y(m, r2)])
    # each point covered by some class
    for x in range(L):
        solver.add_clause([y(m, x % m) for m in moduli])
    sat = solver.solve()
    model = None
    if sat and want_model:
        truth = set(v for v in solver.get_model() if v > 0)
        model = []
        for m in moduli:
            for r in range(m):
                if vp.id((m, r)) in truth:
                    model.append((r, m))
                    break
    solver.delete()
    return sat, model


# ------------------------------------------------- backtracking bitset search
def solve_backtrack(moduli, L, find_witness=True, node_budget=None):
    """Exhaustive DFS. Returns (sat, model_or_None, nodes_explored).
    If sat, model covers Z/L. If not sat, UNSAT proven by exhaustion
    (subject to node_budget; None => unbounded)."""
    moduli = sorted(moduli, reverse=True)  # try large moduli... actually order below
    # We branch by least uncovered point; ordering of moduli affects only tie-break.
    k = len(moduli)
    inv_m = moduli
    stats = {"nodes": 0, "hit_budget": False}

    def recurse(covered, used_mask, assign):
        stats["nodes"] += 1
        if node_budget is not None and stats["nodes"] > node_budget:
            stats["hit_budget"] = True
            return None
        # find least uncovered
        nxt = np.argmin(covered)
        if covered[nxt]:
            return list(assign)  # all covered -> witness
        x = int(nxt)
        remaining_uncovered = L - int(covered.sum())
        # prune: max new coverage from unassigned moduli
        cap = 0
        for i in range(k):
            if not (used_mask >> i) & 1:
                cap += L // inv_m[i]
        if cap < remaining_uncovered:
            return None
        # branch: some unassigned modulus must cover x, residue forced = x % m
        for i in range(k):
            if (used_mask >> i) & 1:
                continue
            m = inv_m[i]
            a = x % m
            new_covered = covered.copy()
            new_covered[a::m] = True
            res = recurse(new_covered, used_mask | (1 << i),
                          assign + [(a, m)])
            if res is not None:
                return res
        return None

    covered0 = np.zeros(L, dtype=bool)
    model = recurse(covered0, 0, [])
    sat = model is not None
    return sat, model, stats


if __name__ == "__main__":
    # smoke test on the classic covering system
    classic = [(0, 2), (0, 3), (1, 4), (5, 6), (7, 12)]
    ok, bad = covers(classic)
    print("classic {0/2,0/3,1/4,5/6,7/12} covers Z/12:", ok, "(bad point", bad, ")")
