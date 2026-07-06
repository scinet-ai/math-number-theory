#!/usr/bin/env bash
# Re-runs a fast verification slice for the Erdos #273 bounded-non-existence
# result, plus the KNOWN-SYSTEM sanity check. Deterministic; ~1-2 min.
#
#   1. Sanity suite: covering verifier accepts the classic covering system
#      {0/2,0/3,1/4,5/6,7/12} and rejects an incomplete variant; the SAT and
#      backtracking engines agree on random instances; and the local-density
#      removal LEMMA is validated (coverability of full set == coverability of
#      reduced core) on random modulus sets.
#   2. Master reduction sweep: prints the largest search-free NON-EXISTENCE
#      bound and the first bound requiring exact search.
#   3. Mechanical UNSAT confirmation at the boundary M=276 (core reciprocal
#      sum < 1 => root-prune certificate) via the backtracking engine.
set -euo pipefail
cd "$(dirname "$0")"

RUN() { uv run --with sympy --with numpy --with python-sat python3 -u "$@"; }

echo "############ [1/3] sanity + lemma validation ############"
RUN test_sanity.py

echo; echo "############ [2/3] master reduction sweep (M<=1000) ############"
RUN run_results.py 1000

echo; echo "############ [3/3] mechanical UNSAT at boundary M=276 ############"
RUN frontier_search.py 276 30

echo; echo "############ frontier demo: exact search on a tiny sum>=1 core ############"
echo "(coverable {2,3,4,6,12} -> witness;  uncoverable {2,4,6,12} -> UNSAT)"
RUN - <<'PY'
from frontier_search import search
from cover_sat import covers
from admissible import lcm
for moduli in ([2,3,4,6,12],[2,4,6,12]):
    L=lcm(moduli); m,st,el=search(moduli,L,30)
    print(f"  {moduli} sum={sum(1/x for x in moduli):.3f} -> "
          f"{'WITNESS '+str(sorted(m)) if m else 'UNSAT'} "
          f"(verified={covers(m,L)[0] if m else 'n/a'}, nodes={st['nodes']})")
PY

echo; echo "ALL VERIFICATION STEPS COMPLETED."
