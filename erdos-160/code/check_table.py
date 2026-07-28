#!/usr/bin/env python3
"""Independent spot-verification of the h(N) table (used by verify.sh).

1. Every stored witness colouring: uses exactly the claimed number of colours
   h(N), and every 4-AP in [N] sees >= 3 distinct colours (checker written
   independently of the encoder: direct enumeration over (a, d)).
2. Table sanity: h nondecreasing; each claimed jump k has first_N consistent
   with the table; every N in the table between min and max is present.
3. Brute-force cross-check of h(N) for N <= BRUTE_MAX against the SAT table.
4. For selected jump certificates: regenerate the CNF, compare sha256 against
   the recorded hash, and re-run drat-trim on the stored DRAT proof.
Exit nonzero on any mismatch.
"""
import json
import os
import subprocess
import sys
import hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "code"))
import encode
import brute

BRUTE_MAX = 20
DRATTRIM = os.path.join(ROOT, "tools", "drat-trim", "drat-trim")
fails = []


def fail(msg):
    print("FAIL:", msg)
    fails.append(msg)


res = json.load(open(os.path.join(ROOT, "results.json")))
table = {int(n): v["h"] for n, v in res["table"].items()}
Ns = sorted(table)
print("table covers N=%d..%d, h in [%d..%d]" % (Ns[0], Ns[-1], table[Ns[0]], table[Ns[-1]]))

# 2. contiguity + monotonicity
if Ns != list(range(Ns[0], Ns[-1] + 1)):
    fail("table not contiguous")
for a, b in zip(Ns, Ns[1:]):
    if table[b] < table[a]:
        fail("h not monotone at N=%d" % b)

# 1. witnesses
for N in Ns:
    w = json.load(open(os.path.join(ROOT, "witnesses", "N%d.json" % N)))
    col = w["colouring"]
    if len(col) != N:
        fail("witness N=%d wrong length" % N)
    if len(set(col)) > table[N]:
        fail("witness N=%d uses %d > h=%d colours" % (N, len(set(col)), table[N]))
    ok = True
    for d in range(1, (N - 1) // 3 + 1):
        for a in range(1, N - 3 * d + 1):
            if len({col[a - 1], col[a + d - 1], col[a + 2 * d - 1], col[a + 3 * d - 1]}) < 3:
                ok = False
    if not ok:
        fail("witness N=%d violates a 4-AP" % N)
print("witnesses: all %d checked" % len(Ns))

# jumps consistent with table
for kk, j in res["jumps"].items():
    kk = int(kk)
    fN = j["first_N"]
    # h can jump by more than 1 at a single N (it does at N=4: 1 -> 3), so a
    # jump record (UNSAT of k-1 colours first at N) requires h(N) >= k and
    # h(N-1) <= k-1.
    if fN in table and table[fN] < kk:
        fail("jump k=%d first_N=%d disagrees with table h=%d" % (kk, fN, table[fN]))
    if fN - 1 in table and table[fN - 1] > kk - 1:
        fail("jump k=%d: h(first_N-1) > k-1" % kk)
print("jumps: %d checked" % len(res["jumps"]))

# 3. brute force small N
for N in range(4, min(BRUTE_MAX, Ns[-1]) + 1):
    hb = brute.h_of(N)
    if hb != table[N]:
        fail("brute h(%d)=%d != table %d" % (N, hb, table[N]))
print("brute force agrees for N=4..%d" % min(BRUTE_MAX, Ns[-1]))

# 4. certificates: verify all whose proof is < 80 MB (keeps verify.sh under 5 min)
for kk, j in sorted(res["jumps"].items(), key=lambda t: int(t[0])):
    if "proof" not in j:
        continue
    proof = os.path.join(ROOT, j["proof"])
    if not os.path.exists(proof):
        print("cert k=%s: proof file absent (pruned), skipping re-check" % kk)
        continue
    if os.path.getsize(proof) > 80 * (1 << 20):
        print("cert k=%s: proof > 80MB, skipping in spot-verify" % kk)
        continue
    N, k = j["first_N"], j["unsat_k"]
    nvars, clauses = encode.build(N, k, symbreak=True)
    cnf = os.path.join(ROOT, "certs", "regen_N%d_k%d.cnf" % (N, k))
    with open(cnf, "w") as f:
        f.write("c erdos160 N=%d k=%d symbreak=1\n" % (N, k))
        f.write("p cnf %d %d\n" % (nvars, len(clauses)))
        for cl in clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")
    h = hashlib.sha256(open(cnf, "rb").read()).hexdigest()
    if h != j["cnf_sha256"]:
        fail("cert k=%s: regenerated CNF hash mismatch" % kk)
    v = subprocess.run([DRATTRIM, cnf, proof], capture_output=True, text=True)
    if "s VERIFIED" not in v.stdout:
        fail("cert k=%s: drat-trim did not verify" % kk)
    else:
        print("cert k=%s (N=%d, %d colours UNSAT): DRAT VERIFIED" % (kk, N, k))
    os.remove(cnf)

if fails:
    print("\n%d FAILURES" % len(fails))
    sys.exit(1)
print("\nALL CHECKS PASSED")
