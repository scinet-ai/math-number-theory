#!/usr/bin/env python3
r"""Independent LP cross-check of the span lemma (Lemma 2 in proof_small_r.md).

Lemma 2 states: if F = {E_1, ..., E_m} is an inclusion-minimal family of
r-sets with empty common intersection (m >= 2), then |E_1 ∪ ... ∪ E_m|
<= m(r - m + 2), and this is attained.

Any such family determines an "atom vector": for each nonempty A ⊊ [m],
x_A = #{vertices belonging to exactly the edges indexed by A}.  (The atom
A = [m] is empty because the total intersection is empty.)  The structural
facts used are ONLY:

  (i)   each edge has r vertices:            sum_{A ∋ i} x_A = r  for all i;
  (ii)  minimality gives, for each i, a vertex in every edge except E_i:
        x_{[m] \ {i}} >= 1  (these are the distinguished vertices x_i);
  (iii) x_A >= 0.

The span is  sum_A x_A.  This script maximizes the span by LINEAR
PROGRAMMING over (i)-(iii) -- a relaxation containing every legal atom
vector -- and checks that the LP optimum equals m(r-m+2) exactly.  Since the
LP optimum upper-bounds the true combinatorial maximum, LP = m(r-m+2)
re-proves Lemma 2 numerically without using the proof's counting argument.
It also confirms attainability (the LP optimum is attained by the integer
point: required atoms = 1, remainder in singletons).

Consequently max_m LP(r, m) = 3r-3 for r = 3,4,5 (Theorem A's engine) and
= 16 > 15 at r = 6, m = 4 (the gadget's escape hatch).

Failure-power controls:
  - dropping constraint (ii) must raise the optimum to mr for m >= 3
    (checks the constraint is load-bearing);
  - the deliberately wrong formula m(r-m+1) must NOT match.

Requires scipy.  Exit code 0 iff all checks pass.
"""
import itertools
import sys

import numpy as np
from scipy.optimize import linprog

FAIL = []


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
    if not ok:
        FAIL.append(name)


def lp_max_span(r, m, require_minimality=True):
    atoms = [frozenset(A)
             for k in range(1, m)
             for A in itertools.combinations(range(m), k)]
    n = len(atoms)
    A_eq = np.zeros((m, n))
    for j, A in enumerate(atoms):
        for i in A:
            A_eq[i, j] = 1.0
    b_eq = np.full(m, float(r))
    bounds = []
    for A in atoms:
        lb = 1.0 if (require_minimality and len(A) == m - 1) else 0.0
        bounds.append((lb, None))
    res = linprog(c=-np.ones(n), A_eq=A_eq, b_eq=b_eq, bounds=bounds,
                  method="highs")
    if not res.success:
        return None
    return -res.fun


def main():
    print("== LP certificate: max span of minimal empty-intersection family")
    tol = 1e-7
    for r in range(3, 13):
        best = None
        for m in range(2, r + 2):
            opt = lp_max_span(r, m)
            target = m * (r - m + 2)
            ok = opt is not None and abs(opt - target) < tol
            check(f"LP r={r} m={m}: optimum == m(r-m+2) = {target}", ok,
                  f"LP={opt}")
            if opt is not None:
                best = max(best, opt) if best is not None else opt
        if r <= 5:
            check(f"LP r={r}: max_m span == 3r-3 = {3*r-3}",
                  abs(best - (3 * r - 3)) < tol, f"max={best}")
        else:
            check(f"LP r={r}: max_m span = {best} > 3r-3 = {3*r-3}",
                  best > 3 * r - 3 + 1 - tol, f"max={best}")

    print("== failure-power controls")
    # (ii) is load-bearing: without minimality the optimum jumps to mr (m>=3)
    r, m = 6, 4
    opt_free = lp_max_span(r, m, require_minimality=False)
    check("control: dropping minimality raises optimum to mr = 24",
          abs(opt_free - r * m) < tol, f"LP={opt_free}")
    # wrong formula must mismatch
    opt = lp_max_span(6, 4)
    check("control: wrong formula m(r-m+1) = 12 must NOT match LP = 16",
          abs(opt - 4 * (6 - 4 + 1)) > 1, f"LP={opt}")

    print()
    if FAIL:
        print(f"OVERALL: FAIL ({len(FAIL)}): {FAIL}")
        sys.exit(1)
    print("OVERALL: ALL LP CHECKS PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
