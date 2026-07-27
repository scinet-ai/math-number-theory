#!/bin/sh
# Spot-verification (target <5 min). Nonzero exit on any mismatch.
#  1. verify.py: every certified cell's stored family is valid, down-closed,
#     has the recorded size, and provably contains no k pairwise disjoint
#     edges (direct exhaustive search, no shifting assumption).
#  2. Deterministic re-solve of the headline window f(13..17; 4,3) from
#     scratch with CP-SAT; optima must reproduce the recorded values.
set -e
cd "$(dirname "$0")"
PY=.venv/bin/python
[ -x "$PY" ] || PY=python3

$PY code/verify.py

echo "--- re-solving f(n;4,3) n=13..17 (v1, full constraints) and f(21;4,5) (v2, lazy) from scratch ---"
$PY - <<'EOF'
import json, os, sys
sys.path.insert(0, "code")
from emc_solve import solve_cell
from emc_solve2 import solve_cell as solve_cell2
os.makedirs("/tmp/emc_reverify", exist_ok=True)
expected = {}
for line in open("results/results.jsonl"):
    r = json.loads(line)
    if r.get("certified_optimal"):
        expected[(r["r"], r["k"], r["n"])] = r["f"]
ok = True
for n in range(13, 18):
    rec = solve_cell(n, 4, 3, time_limit=120, lazy=False, outdir="/tmp/emc_reverify")
    good = rec["certified_optimal"] and rec["f"] == expected[(4, 3, n)]
    print(f"re-solve r=4 k=3 n={n}: f={rec['f']} expected={expected[(4,3,n)]} -> {'OK' if good else 'FAIL'}")
    ok &= good
rec = solve_cell2(21, 4, 5, time_limit=300, outdir="/tmp/emc_reverify")
good = rec["certified_optimal"] and rec["f"] == expected[(4, 5, 21)]
print(f"re-solve r=4 k=5 n=21: f={rec['f']} expected={expected[(4,5,21)]} -> {'OK' if good else 'FAIL'}")
ok &= good
sys.exit(0 if ok else 1)
EOF
echo "verify.sh: ALL CHECKS PASSED"
