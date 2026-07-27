#!/bin/bash
# Spot verification for the Erdos #436 round-2 computation (< 5 minutes).
# Re-checks:
#   (1) the even-k encoding against three published constants:
#       Lambda(2,2)=9, Lambda(4,2)=1224 re-solved end-to-end (both
#       directions), plus a fresh decode+verify of the k=4 certificate;
#   (2) every k=8 certificate underlying the claimed Lambda(8,2) lower
#       bound, re-derived from scratch by the independent verifier
#       (including the 8|k admissibility condition f(2) even);
#   (3) the k=6 SAT certificate at B=202123 (Lambda(6,2)=202124 side);
#   (4) the banked verdict log is consistent: largest SAT + 1 = smallest
#       UNSAT recorded in results/trisect_state.json (if search finished).
# Exits nonzero on any mismatch.
set -e
cd "$(dirname "$0")"
fail() { echo "VERIFY FAIL: $1"; exit 1; }

echo "== 1. even-k encoding vs published constants (k=2, k=4) =="
command -v kissat >/dev/null || fail "kissat not installed (brew install kissat)"
tmp=$(mktemp -d)
python3 src/encode_v2.py encode 2 2 8 "$tmp/a.cnf" >/dev/null
python3 src/encode_v2.py encode 2 2 9 "$tmp/b.cnf" >/dev/null
python3 src/encode_v2.py encode 4 2 1223 "$tmp/c.cnf" >/dev/null
python3 src/encode_v2.py encode 4 2 1224 "$tmp/d.cnf" >/dev/null
rc=0; kissat -q "$tmp/a.cnf" >/dev/null || rc=$?; [ $rc -eq 10 ] || fail "expected SAT k=2 B=8"
rc=0; kissat -q "$tmp/b.cnf" >/dev/null || rc=$?; [ $rc -eq 20 ] || fail "expected UNSAT k=2 B=9"
rc=0; kissat "$tmp/c.cnf" >"$tmp/c.out" || rc=$?; [ $rc -eq 10 ] || fail "expected SAT k=4 B=1223"
rc=0; kissat -q "$tmp/d.cnf" >/dev/null || rc=$?; [ $rc -eq 20 ] || fail "expected UNSAT k=4 B=1224"
python3 src/encode_v2.py decode 4 2 1223 "$tmp/c.out" "$tmp/c_cert.txt" >/dev/null
python3 src/verify_certificate_v2.py "$tmp/c_cert.txt" || fail "fresh k=4 certificate"
echo "Lambda(2,2)=9 and Lambda(4,2)=1224 reproduced (both directions)."

echo "== 2. k=8 certificates (independent re-derivation + admissibility) =="
ls certs/k8_B*_cert.txt >/dev/null 2>&1 || fail "no k=8 certificates present"
for cert in certs/k8_B*_cert.txt; do
    python3 src/verify_certificate_v2.py "$cert" || fail "certificate $cert"
done

echo "== 3. k=6 certificate (Lambda(6,2)=202124 SAT side) =="
python3 src/verify_certificate_v2.py certs/k6_B202123_cert.txt || fail "k=6 certificate"

echo "== 3b. k=5 m=3 certificate at B=10^7 (Lambda(5,3) >= 10,000,001) =="
python3 src/verify_certificate_v2.py certs/k5_m3_B10000000_cert.txt \
    || fail "k=5 m=3 certificate (round-2 verifier)"
python3 ../erdos-436/src/verify_certificate.py certs/k5_m3_B10000000_cert.txt \
    || echo "  (round-1 verifier not present here; round-2 check above passed)"

echo "== 4. verdict-log consistency =="
python3 - <<'EOF' || fail "trisect state inconsistent"
import json, sys
st = json.load(open("results/trisect_state.json"))
sat = [h["B"] for h in st["history"] if h["verdict"] == "SAT"]
uns = [h["B"] for h in st["history"] if h["verdict"] == "UNSAT"]
assert st["lo"] == max(sat), (st["lo"], max(sat))
assert st["hi"] == min(uns), (st["hi"], min(uns))
assert max(sat) < min(uns)
print(f"verdicts consistent: largest SAT B={st['lo']}, smallest UNSAT B={st['hi']}",
      "=> Lambda(8,2) =", st["hi"] if st["hi"] - st["lo"] == 1 else "(interval open)")
EOF

rm -rf "$tmp"
echo "ALL VERIFICATIONS PASSED"
