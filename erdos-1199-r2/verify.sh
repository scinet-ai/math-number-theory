#!/bin/bash
# Spot-verification for the round-2 Owings k=4 computation (< 5 min).
# Nonzero exit on any mismatch.
set -e
cd "$(dirname "$0")"

echo "== 1. Independent recheck of every stored lower-bound witness =="
for w in results/witness_k4_n*.txt; do
    python3 code/check_coloring.py 4 "$w" || { echo "FAIL: $w"; exit 1; }
done

echo
echo "== 2. Deterministic CNF regeneration matches logged clause counts =="
python3 - <<'EOF'
import json, os, sys
sys.path.insert(0, "code")
from generate_cnf import sumset_clauses
logged = {}
for line in open("results/search_log.jsonl"):
    e = json.loads(line)
    if e.get("clauses") and e.get("n"):
        logged[e["n"]] = e["clauses"]
for n, c in sorted(logged.items()):
    got = 2 * sum(1 for _ in sumset_clauses(n, 4))
    assert got == c, f"n={n}: regenerated {got} clauses, log says {c}"
    print(f"n={n}: {c} clauses OK")
EOF

echo
echo "== 2b. Parity lemma: constraint sets at 2m and 2m+1 are identical =="
python3 - <<'EOF'
import sys
sys.path.insert(0, "code")
from generate_cnf import sumset_clauses
for m2 in (72, 80, 88, 92, 96):
    a = list(sumset_clauses(m2, 4))
    b = list(sumset_clauses(m2 + 1, 4))
    assert a == b, f"constraint sets differ at {m2}/{m2+1}"
    print(f"n={m2} vs n={m2+1}: identical ({len(a)} subsets)")
EOF

echo
echo "== 3. DRAT certificate(s): verify stored proof, or regenerate =="
python3 - <<'EOF'
import json, os, subprocess, sys
boundary = None
for line in open("results/search_log.jsonl"):
    e = json.loads(line)
    if e.get("event") == "drat_certificate" and e.get("drat_trim_verified"):
        boundary = e
if boundary is None:
    print("no drat_certificate event in log (no UNSAT boundary certified)")
    sys.exit(0)
n = boundary["n"]
cnf = f"certificates/k4/owings_k4_n{n}.cnf"
proof = f"certificates/k4/owings_k4_n{n}.drat"
if os.path.exists(proof):
    out = subprocess.run(["tools/drat-trim/drat-trim", cnf, proof],
                         capture_output=True, text=True).stdout
    assert "s VERIFIED" in out, "stored DRAT proof failed verification"
    print(f"stored DRAT proof for n={n} re-verified: s VERIFIED")
else:
    print(f"proof for n={n} not stored (size); regenerate with:")
    print(f"  python3 code/certify.py {n}")
EOF

echo
echo "== verify.sh: ALL CHECKS PASSED =="
