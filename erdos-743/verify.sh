#!/bin/bash
# Spot verification for the n=10 tree-packing sweep (runs in ~2-4 minutes).
#
# 1. Regenerates the tree lists from scratch, re-running the two independent
#    isomorph-completeness checks (OEIS A000055 counts + AHU canonical forms).
# 2. Rebuilds the C solver and re-runs two full chunks of the n=10 sweep plus
#    one chunk of the n=9 calibration sweep; the freshly produced chunk files
#    (family counts, per-code counts, witness hash) must be byte-identical to
#    the banked results.
# 3. Independently re-validates a slice of the banked packing witnesses with
#    networkx (partition of E(K_10) + per-tree isomorphism).
#
# Exits nonzero on any mismatch. Requires: clang, uv (for python+networkx).
set -euo pipefail
cd "$(dirname "$0")"

RECHECK_N10_CHUNKS="003 042"
RECHECK_N9_CHUNKS="000"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "== 1/3 tree lists: regenerate + completeness checks =="
cp -r trees "$TMP/trees_banked"
uv run --with networkx python generate_trees.py 10
for f in trees_02 trees_03 trees_04 trees_05 trees_06 trees_07 trees_08 trees_09 trees_10; do
  cmp "trees/$f.txt" "$TMP/trees_banked/$f.txt" \
    || { echo "MISMATCH: regenerated $f.txt differs from banked"; exit 1; }
done
echo "tree lists reproduce byte-identically"

echo "== 2/3 solver: rebuild + re-run chunks =="
clang -O2 -o "$TMP/packer" packer.c
mkdir -p "$TMP/n10" "$TMP/n9"
for c in $RECHECK_N10_CHUNKS; do
  "$TMP/packer" 10 "$((10#$c))" trees "$TMP/n10" 50000 1000000000
  cmp "$TMP/n10/chunk_$c.txt" "results/n10/chunk_$c.txt" \
    || { echo "MISMATCH: n=10 chunk $c differs from banked result"; exit 1; }
  cmp "$TMP/n10/sample_$c.txt" "results/n10/sample_$c.txt" \
    || { echo "MISMATCH: n=10 sample $c differs from banked result"; exit 1; }
done
for c in $RECHECK_N9_CHUNKS; do
  "$TMP/packer" 9 "$((10#$c))" trees "$TMP/n9" 50000 1000000000
  cmp "$TMP/n9/chunk_$c.txt" "results/n9/chunk_$c.txt" \
    || { echo "MISMATCH: n=9 chunk $c differs from banked result"; exit 1; }
done
echo "re-run chunks reproduce byte-identically (incl. witness hashes)"

echo "== 3/3 witnesses: independent networkx validation (slice) =="
uv run --with networkx python check_witnesses.py 10 trees results/n10 40
uv run --with networkx python check_witnesses.py 9 trees results/n9 40
# every CP-SAT-resolved straggler witness, in full
uv run --with networkx python check_witnesses.py 10 trees results/n10/hard

echo "== summary over banked n=10 chunks =="
n_chunks=$(ls results/n10/chunk_*.txt | wc -l | tr -d ' ')
grep -h '^greedy' results/n10/chunk_*.txt \
  | awk -v nc="$n_chunks" '{g+=$2;b+=$4;u+=$6;d+=$8}
      END {print "chunks",nc,"families",g+b+u+d,"greedy",g,"backtrack",b,"unsat",u,"undecided",d;
           if (nc!=106 || g+b+u+d!=45376056 || u!=0) {print "SUMMARY MISMATCH"; exit 1}}'
incomplete=$(grep -L '^complete yes' results/n10/chunk_*.txt | wc -l | tr -d ' ')
[ "$incomplete" -eq 0 ] || { echo "MISMATCH: some chunks not complete"; exit 1; }
# node-cap stragglers: every family the C search left undecided must have a
# validated CP-SAT packing witness in results/n10/hard (same family indices)
undecided_lines=$(grep -h 'code 3' results/n10/chunk_*.txt | sort)
hard_lines=$(awk '{printf "%s", $1; for (i=3; i<=10; i++) printf " %s", $i; print ""}' \
               results/n10/hard/sample_*.txt | sort)
undecided_keys=$(echo "$undecided_lines" | awk '{printf "%s", $2; for (i=6; i<=13; i++) printf " %s", $i; print ""}' | sort)
[ "$undecided_keys" = "$hard_lines" ] \
  || { echo "MISMATCH: undecided families vs resolved straggler witnesses"; exit 1; }
echo "stragglers reconcile: $(echo "$hard_lines" | wc -l | tr -d ' ') undecided families all have validated packing witnesses"
echo "VERIFY OK: every family of trees T_2..T_10 packs K_10"
