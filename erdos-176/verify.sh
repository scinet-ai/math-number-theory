#!/bin/bash
# Spot-verification for the erdos-176 N(k,l) table (target: < 5 min).
# 1. Re-checks every stored witness with the independent checker.
# 2. Re-runs drat-trim on every stored (cnf, proof) certificate pair.
# 3. Regenerates one CNF from scratch and diffs it against the stored copy.
# Nonzero exit on any mismatch.
set -u
cd "$(dirname "$0")"
PY=.venv/bin/python
DT=tools-drat-trim/drat-trim
fail=0

echo "== 1. witnesses =="
for w in witnesses/k*.txt; do
  base=$(basename "$w" .txt)            # k{K}l{L}_N{N}
  k=${base#k}; k=${k%%l*}
  l=${base#*l}; l=${l%%_*}
  out=$($PY code/check_witness.py "$k" "$l" "$(cat "$w")") || { echo "FAIL $w: $out"; fail=1; continue; }
  echo "ok $base: $out"
done

echo "== 2. DRAT certificates =="
shopt -s nullglob
for cnf in certs/*.cnf; do
  base=${cnf%.cnf}
  proof=$base.drat
  [ -f "$proof.gz" ] && gunzip -k -f "$proof.gz"
  if [ ! -f "$proof" ]; then echo "FAIL missing proof for $cnf"; fail=1; continue; fi
  res=$($DT "$cnf" "$proof" | tr -d '\r' | grep -E "^s ")
  if [ "$res" = "s VERIFIED" ]; then
    echo "ok $(basename "$base"): drat-trim s VERIFIED"
  else
    echo "FAIL $(basename "$base"): drat-trim said '$res'"; fail=1
  fi
  [ -f "$proof.gz" ] && rm -f "$proof"
done

echo "== 3. CNF regeneration determinism =="
sample=$(ls certs/*.cnf | head -1)
if [ -n "$sample" ]; then
  base=$(basename "$sample" .cnf)       # k{K}l{L}_N{N}
  k=${base#k}; k=${k%%l*}
  l=${base#*l}; l=${l%%_*}
  N=${base#*_N}
  $PY code/encode.py "$N" "$k" "$l" /tmp/regen_$base.cnf >/dev/null
  if cmp -s /tmp/regen_$base.cnf "$sample"; then
    echo "ok $base: regenerated CNF is byte-identical"
  else
    echo "FAIL $base: regenerated CNF differs"; fail=1
  fi
  rm -f /tmp/regen_$base.cnf
fi

if [ $fail -eq 0 ]; then echo "ALL VERIFICATIONS PASSED"; else echo "VERIFICATION FAILURES PRESENT"; fi
exit $fail
