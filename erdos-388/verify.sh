#!/bin/bash
# Erdos #388 attack verification driver.
#   ./verify.sh         fast checks (~1 min): witness, dual-implementation sweeps
#                       at 10^18 and 10^24, and the (6,4) reduction script
#   ./verify.sh full    adds 10^30 dual sweep (~15 s) and 10^36 dual sweep (~8 min)
#   ./verify.sh sage    additionally re-runs the Sage integral-point proof
#                       (requires the e388sage mamba env; see case64_sage.sage)
set -e
TMPD=$(mktemp -d)
trap 'rm -rf "$TMPD"' EXIT
cd "$(dirname "$0")"
PY=.venv/bin/python
[ -x "$PY" ] || PY=python3

fail() { echo "VERIFY FAIL: $1"; exit 1; }

echo "== [1/4] witness identity and factorization =="
$PY - <<'EOF'
import math
a = math.prod(range(8, 15))
b = 63 * 64 * 65 * 66
assert a == b == 17297280, (a, b)
f = 2**7 * 3**3 * 5 * 7 * 11 * 13
assert a == f
# blocks [8..14] (m1=7,k1=7) and [63..66] (m2=62,k2=4): k1,k2>3, disjoint m1+k1=14<=62=m2
assert 7 + 7 <= 62
print("   17297280 = 8..14 = 63..66 = 2^7 3^3 5 7 11 13 ; k1,k2>3, disjoint  OK")
EOF

echo "== [2/4] build C implementation =="
cc -O2 -o sweep sweep.c
echo "   built"

check_pair() {
    E=$1
    $PY sweep.py "$E" > "$TMPD"/e388_py_$E.txt
    ./sweep "$E" > "$TMPD"/e388_c_$E.txt
    diff <(grep '^count' "$TMPD"/e388_py_$E.txt) <(grep '^count' "$TMPD"/e388_c_$E.txt) >/dev/null || fail "counts differ at 10^$E"
    diff <(grep '^checksum' "$TMPD"/e388_py_$E.txt) <(grep '^checksum' "$TMPD"/e388_c_$E.txt) >/dev/null || fail "checksums differ at 10^$E"
    diff <(grep 'collision' "$TMPD"/e388_py_$E.txt | sort) <(grep 'collision' "$TMPD"/e388_c_$E.txt | sort) >/dev/null || fail "collision lists differ at 10^$E"
    D=$(grep -c DISJOINT "$TMPD"/e388_c_$E.txt) || true
    [ "$D" = "1" ] || fail "expected exactly 1 disjoint collision at 10^$E, got $D"
    grep -q 'DISJOINT: 17297280 = \[8\.\.14\] = \[63\.\.66\]' "$TMPD"/e388_c_$E.txt || fail "unique disjoint collision is not the known one at 10^$E"
    echo "   10^$E: Python == C (counts, checksum, collisions); unique disjoint collision = 17297280  OK"
}

echo "== [3/4] dual-implementation exhaustive sweeps =="
check_pair 18
check_pair 24
if [ "$1" = "full" ] || [ "$2" = "full" ]; then
    check_pair 30
    check_pair 36
fi

echo "== [4/4] (6,4) case reduction and integral-point filter =="
$PY case64_reduction.py > "$TMPD"/e388_case64.txt
grep -q 'identity (x+1)..(x+6) == t(t+4)(t+6) with t=x\^2+7x+6 : True' "$TMPD"/e388_case64.txt || fail "identity 1"
grep -q 'identity (y+1)..(y+4)+1 == (y\^2+5y+5)\^2            : True' "$TMPD"/e388_case64.txt || fail "identity 2"
grep -q 'direct search x <= 2\*10\^6: \[(1, 6)\]' "$TMPD"/e388_case64.txt || fail "direct (6,4) search"
grep -q 'matches independent search   : True' "$TMPD"/e388_case64.txt || fail "LMFDB list vs search"
grep -q 'x=1 y=6.*OVERLAP' "$TMPD"/e388_case64.txt || fail "unique (6,4) solution filter"
echo "   (6,4): identities, invariants, point search, LMFDB map, filter  OK"

if [ "$1" = "sage" ] || [ "$2" = "sage" ]; then
    echo "== [sage] independent Mordell-Weil + integral points (proof=True) =="
    mamba run -n e388sage sage case64_sage.sage > "$TMPD"/e388_sage.txt 2>&1
    grep -q "certified: (2, 2)" "$TMPD"/e388_sage.txt || fail "sage rank certificate"
    grep -q "positive-integer solutions (x,y) of (x+1)..(x+6)=(y+1)..(y+4): \[(1, 6)\]" "$TMPD"/e388_sage.txt || fail "sage (6,4) solutions"
    echo "   sage: rank (2,2) certified, integral points complete, unique solution (1,6)  OK"
fi

echo "ALL CHECKS PASSED"
