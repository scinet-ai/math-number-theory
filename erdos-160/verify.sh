#!/bin/sh
# Spot-verification for the erdos-160 exact h(N) table (target: < 5 min).
#  - independent re-check of every witness colouring (all 4-APs, >= 3 colours)
#  - table monotonicity/contiguity + jump consistency
#  - brute-force recomputation of h(N) for N <= 20 (no SAT solver involved)
#  - CNF regeneration hash check + drat-trim re-verification of stored
#    UNSAT certificates (< 80 MB ones)
# Exits nonzero on any mismatch.
set -e
cd "$(dirname "$0")"
if [ ! -x tools/drat-trim/drat-trim ]; then
  echo "building drat-trim..."
  (cd tools/drat-trim && make >/dev/null)
fi
exec python3 code/check_table.py
