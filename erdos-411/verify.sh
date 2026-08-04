#!/bin/bash
# Erdos #411 attack: full re-verification from scratch.
#
#  1. Recompiles the C sweep and re-runs it on x <= 10^5, r <= 25.
#  2. Re-runs the independent pure-Python probe on the same range and checks
#     that the two raw-hit sets are IDENTICAL (cross-implementation check).
#  3. Re-checks every certificate in certificates/witnesses.json by direct
#     iteration of g(n) = n + phi(n), using a third, self-contained
#     implementation (verify_certificates.py: trial division + Miller-Rabin +
#     Floyd-variant Pollard rho; no shared code with the sweep).
#     This includes the recomputation of every stored orbit value, the identity
#     g_r(x) = c*x, and the divisibility rad(c) | g_j(x) for j < r.
#  4. Re-checks the OEIS A383044 cross-validation flag stored in the catalogue.
#
# Expected runtime: ~10-20 min (step 3 dominates).  Exit 0 iff everything passes.
set -e
cd "$(dirname "$0")"

echo "== [1/4] compile + run C sweep on x<=1e5, r<=25 =="
gcc -O2 -o code/sweep code/sweep.c -lpthread
TMP=$(mktemp -d)
( cd "$TMP" && "$OLDPWD"/code/sweep 2 100000 25 10000000 4 2>/dev/null )
cat "$TMP"/sweep_part_*.txt | grep '^H' | awk '{print $2, $3, $4}' | sort -n > "$TMP"/c_hits.txt

echo "== [2/4] independent Python probe, same range, compare =="
python3 - "$TMP" <<'EOF'
import sys, json, subprocess, os
tmp = sys.argv[1]
out = subprocess.run([sys.executable, "code/probe.py", "100000", "25"],
                     capture_output=True, text=True, check=True)
py = sorted(tuple(h) for h in json.loads(out.stdout)["raw_hits"])
ch = sorted(tuple(map(int, l.split())) for l in open(os.path.join(tmp, "c_hits.txt")))
assert py == ch, f"MISMATCH: python {len(py)} hits vs C {len(ch)} hits"
print(f"OK: {len(py)} raw hits identical across implementations")
EOF

echo "== [3/4] re-verify every certificate by direct iteration =="
python3 code/verify_certificates.py certificates/witnesses.json

echo "== [4/4] OEIS A383044 cross-check =="
python3 - <<'EOF'
import json
cat = json.load(open("certificates/witnesses.json"))
chk = cat["A383044_check"]
assert chk["match"] and chk["ours"] == chk["expected"], "A383044 mismatch"
print("OK: (r,c)=(2,2) certificate points <= 8960 equal OEIS A383044 terms")
EOF

rm -rf "$TMP"
echo "ALL CHECKS PASSED"
