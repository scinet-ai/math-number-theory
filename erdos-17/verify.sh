#!/bin/bash
# Spot-verification for the Erdős #17 cluster-prime sweep (<= 5 min).
# Nonzero exit on any mismatch.
set -e
cd "$(dirname "$0")"

echo "== 1. rebuild from source =="
clang -O3 -march=native -o cluster_verify cluster.c

echo "== 2. re-derive [0,1e6) and diff against OEIS b-file A038134 (8287 terms) =="
./cluster_verify 0 1000000 --emit-cluster-list 2>/tmp/verify_clusters.txt >/dev/null
diff <(awk 'NF{print $2}' frontier/b038134.txt) /tmp/verify_clusters.txt
echo "   b-file match OK"

echo "== 3. re-derive fixed blocks, compare against committed results.csv =="
for BLK in "0 1000000000" "5000000000000 5010000000000" "9990000000000 10000000000000"; do
  set -- $BLK
  LINE_NEW=$(./cluster_verify $1 $2 | cut -d, -f1-18)
  LINE_OLD=$(grep "^$1,$2," results.csv | head -1 | cut -d, -f1-18)
  if [ -z "$LINE_OLD" ]; then echo "   block $1 not in results.csv (skip)"; continue; fi
  if [ "$LINE_NEW" != "$LINE_OLD" ]; then
    echo "   MISMATCH block $1:"; echo "   new: $LINE_NEW"; echo "   old: $LINE_OLD"; exit 1
  fi
  echo "   block $1..$2 reproduced (counts+FNV) OK"
done

echo "== 4. independent Miller-Rabin spot checks (witnesses + cluster verdicts) =="
python3 spot_check.py

echo "ALL VERIFICATION PASSED"
