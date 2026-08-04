#!/usr/bin/env python3
"""Independent cross-check of the C sieve at small N (default 10^7).

Runs sieve_fmin with a table dump, then recomputes the full certified table
{(a, f(a)) : a <= A_max = floor(N/R(10))} with a DIFFERENT algorithm in a
different language (numpy additive totient sieve + vectorized descending
first-occurrence), and compares the two tables entry by entry.
"""
import os
import subprocess
import sys

import numpy as np

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10**7
here = os.path.dirname(os.path.abspath(__file__))
exe = os.path.join(here, "sieve_fmin")
os.makedirs(os.path.join(here, "data"), exist_ok=True)
dumpf = os.path.join(here, "data", "dump_%d.txt" % N)

r = subprocess.run([exe, str(N), dumpf], capture_output=True, text=True)
done = [l for l in r.stdout.splitlines() if l.startswith("DONE")]
assert done, "no DONE line from sieve_fmin: " + r.stderr[-500:]
_, N_c, A_max, tot_c, ge2_c, maxr_c = done[0].split()
N_c, A_max, tot_c = int(N_c), int(A_max), int(tot_c)
assert N_c == N

# --- independent totient sieve (numpy, additive algorithm) ---
phi = np.arange(N + 1, dtype=np.int64)
for p in range(2, N + 1):
    if phi[p] == p:                      # p prime
        phi[p::p] -= phi[p::p] // p

first = np.zeros(A_max + 1, dtype=np.int64)
pv = phi[1:N + 1]
n_desc = np.arange(N, 0, -1)             # n = N .. 1
pv_desc = phi[n_desc]
sel = pv_desc <= A_max
first[pv_desc[sel]] = n_desc[sel]        # descending: last (smallest n) wins

a_vals = np.nonzero(first)[0]
tot_py = len(a_vals)
ge2_py = int((first[a_vals] >= 2 * a_vals).sum())

# --- compare with the C dump ---
ca, cn = np.loadtxt(dumpf, dtype=np.int64, unpack=True)
order = np.argsort(ca)
ca, cn = ca[order], cn[order]

ok = True
if tot_py != tot_c or len(ca) != tot_py:
    print("FAIL: totient counts differ: C=%d py=%d dumped=%d" % (tot_c, tot_py, len(ca)))
    ok = False
elif not (np.array_equal(ca, a_vals) and np.array_equal(cn, first[a_vals])):
    bad = np.nonzero((ca != a_vals) | (cn != first[a_vals]))[0][:10]
    print("FAIL: table mismatch at rows", bad)
    ok = False
else:
    ge2_ok = (ge2_py == int(ge2_c))
    print("PASS: N=%d A_max=%d — %d totient values, tables identical; "
          "ratio>=2 count %d (C: %s) %s"
          % (N, A_max, tot_py, ge2_py, ge2_c, "" if ge2_ok else "GE2-MISMATCH"))
    ok = ge2_ok

sys.exit(0 if ok else 1)
