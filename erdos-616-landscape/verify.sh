#!/bin/sh
# From-scratch verification driver for the t8/t11 round (proof_t8_t11.md):
#   - Fatness Lemma machine half (r = 8, 9, 10; control r = 11)
#   - independent double-check (covering exhaustion + second r=8 enumeration)
#   - r=8 lower-bound witnesses (literal bitmask sweeps)
#   - H(r,7,5) r=11..15 and H(r,10,7) r=16..20 witnesses (t(11)=t(12)=3 etc.)
#   - EHT91-derivable landscape extraction (pinned r<=20, first open r=21)
#   - randomized tau>=3 falsification search at r=8
# Pure Python 3 stdlib.  Runtime dominated by the r=10 enumeration (~2.5 min),
# the bitmask sweeps (~1.5 min), and the randomized search (~30-60 min; pass
# --quick for a reduced version).
set -e
cd "$(dirname "$0")"

echo "=============================================================="
echo "[1/6] Exhaustive survivor classification + Fatness Lemma check"
echo "      (r = 8, 9, 10; negative control r = 11)"
echo "=============================================================="
python3 -u classify_fatness.py

echo "=============================================================="
echo "[2/6] Independent double-check (covering exhaustion +"
echo "      independent r=8 enumeration; shares no code with [1])"
echo "=============================================================="
python3 -u independent_check.py

echo "=============================================================="
echo "[3/6] Lower-bound witnesses at r=8 (literal L(8) bitmask sweep,"
echo "      tau = 2 exact, planted-bug negative control)"
echo "=============================================================="
python3 -u gadget_check_r8.py

echo "=============================================================="
echo "[4/6] EHT91 witnesses H(r,7,5) r=11..15 and H(r,10,7) r=16..20"
echo "      (tau and L(r) certified; negative controls)"
echo "=============================================================="
python3 -u witness_t11.py

echo "=============================================================="
echo "[5/6] EHT91-derivable landscape (pinned r<=20; first open r=21)"
echo "=============================================================="
python3 -u eht_landscape.py

echo "=============================================================="
echo "[6/6] Randomized tau >= 3 falsification search at r = 8"
echo "=============================================================="
python3 -u search_tau3.py "$@"

echo ""
echo "ALL t8/t11 VERIFICATIONS PASSED"
