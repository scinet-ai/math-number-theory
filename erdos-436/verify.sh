#!/bin/bash
# Spot verification for the Erdos #436 computation (< 5 minutes).
# Re-checks: (1) every certificate underlying a claimed bound, from scratch;
# (2) the SAT reproduction of the two published frontiers Lambda(3,3)=23532
#     and Lambda(5,2)=7888, re-encoding and re-solving both directions;
# (3) two slices of the per-prime scans against the banked witness records.
# Exits nonzero on any mismatch.
set -e
cd "$(dirname "$0")"
fail() { echo "VERIFY FAIL: $1"; exit 1; }

echo "== 1. certificates (independent re-derivation) =="
for cert in results/sat_k5_m3_B5000000_cert.txt \
            results/sat_k5_m3_B1600000_cert.txt \
            results/sat_k7_m3_B1600000_cert.txt \
            results/sat_k7_m3_B400000_cert.txt \
            results/sat_k3_m3_B23531_cert.txt \
            results/sat_k5_m2_B7887_cert.txt \
            results/dfs_k2_m2_cert.txt results/dfs_k3_m2_cert.txt; do
    python3 src/verify_certificate.py "$cert" || fail "certificate $cert"
done

echo "== 2. SAT frontier reproduction (encode + solve both directions) =="
command -v kissat >/dev/null || fail "kissat not installed (brew install kissat)"
tmp=$(mktemp -d)
python3 src/encode_assignment_cnf.py encode 3 3 23531 "$tmp/a.cnf" >/dev/null
python3 src/encode_assignment_cnf.py encode 3 3 23532 "$tmp/b.cnf" >/dev/null
python3 src/encode_assignment_cnf.py encode 5 2 7887  "$tmp/c.cnf" >/dev/null
python3 src/encode_assignment_cnf.py encode 5 2 7888  "$tmp/d.cnf" >/dev/null
rc=0; kissat "$tmp/a.cnf" > "$tmp/a.out" || rc=$?; [ $rc -eq 10 ] || fail "expected SAT at k=3 m=3 B=23531"
rc=0; kissat -q "$tmp/b.cnf" > /dev/null || rc=$?; [ $rc -eq 20 ] || fail "expected UNSAT at k=3 m=3 B=23532"
rc=0; kissat -q "$tmp/c.cnf" > /dev/null || rc=$?; [ $rc -eq 10 ] || fail "expected SAT at k=5 m=2 B=7887"
rc=0; kissat -q "$tmp/d.cnf" > /dev/null || rc=$?; [ $rc -eq 20 ] || fail "expected UNSAT at k=5 m=2 B=7888"
python3 src/encode_assignment_cnf.py decode 3 3 23531 "$tmp/a.out" "$tmp/a_cert.txt" >/dev/null
python3 src/verify_certificate.py "$tmp/a_cert.txt" || fail "fresh 23531 certificate"
echo "Lambda(3,3)=23532 and Lambda(5,2)=7888 reproduced (both directions)."

echo "== 3. scan slices vs banked records =="
clang -O3 -o "$tmp/scan" src/scan_least_consecutive_residues.c || fail "scanner build"
"$tmp/scan" 5 3 27000000 27500000 > "$tmp/s1.log"
grep -q "^SUM 5 3 27000000 27500000 .* 2283 27327371" "$tmp/s1.log" \
    || fail "k=5 slice: expected max r(5,3,p)=2283 at p=27327371"
"$tmp/scan" 3 2 13800000 13850000 > "$tmp/s2.log"
grep -q "^REC 3 2 13817029 77" "$tmp/s2.log" \
    || fail "k=3 slice: expected r(3,2,13817029)=77 (Lambda(3,2) attained)"
grep -q "^SUM 5 3 2 10000000 166104 498475 3329 3331" results/scan_k5_m3_seg0_to1e7.log \
    || fail "banked k=5 seg0 summary changed"
echo "scan slices match banked records."

rm -rf "$tmp"
echo "ALL VERIFICATIONS PASSED"
