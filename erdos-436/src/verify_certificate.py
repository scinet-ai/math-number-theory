#!/usr/bin/env python3
"""Independently verify a character-assignment certificate.

A certificate file (from search_character_assignments) has a header line
  # k=K m=M first_zero_run_at=R      (a branch that died at R)
or
  # k=K m=M no_zero_run_of_length_m_up_to=N   (a survivor branch)
followed by lines "q value" giving the assignment at each prime q in
increasing order.

This script rebuilds the completely multiplicative function f: n -> Z/k
from scratch (no shared code with the search) and checks:
  - death certificate: the FIRST run of m consecutive integers with
    f == 0 starts exactly at R;
  - survivor certificate: there is NO run of m consecutive zeros of f
    among 1..N.
Exits 0 on success, 1 on any mismatch.
"""
import sys
import re


def main(path: str) -> int:
    with open(path) as fh:
        header = fh.readline().strip()
        mo = re.match(r"# k=(\d+) m=(\d+) (first_zero_run_at|no_zero_run_of_length_m_up_to)=(\d+)", header)
        if not mo:
            print(f"FAIL: bad header: {header}")
            return 1
        k, m, kind, target = int(mo.group(1)), int(mo.group(2)), mo.group(3), int(mo.group(4))
        assign = {}
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            q, v = line.split()
            assign[int(q)] = int(v) % k

    limit = target + m - 1 if kind == "first_zero_run_at" else target
    # sieve of smallest prime factors, independent implementation
    spf = list(range(limit + 1))
    i = 2
    while i * i <= limit:
        if spf[i] == i:
            for j in range(i * i, limit + 1, i):
                if spf[j] == j:
                    spf[j] = i
        i += 1
    f = [0] * (limit + 1)
    for n in range(2, limit + 1):
        q = spf[n]
        if q == n:
            if n not in assign:
                print(f"FAIL: prime {n} <= {limit} missing from certificate")
                return 1
            f[n] = assign[n]
        else:
            f[n] = (f[q] + f[n // q]) % k

    first_run = None
    run = 0
    for n in range(1, limit + 1):
        run = run + 1 if f[n] == 0 else 0
        if run >= m:
            first_run = n - m + 1
            break

    if kind == "first_zero_run_at":
        if first_run == target:
            print(f"OK: k={k} m={m}: first zero-run of f at {target}, as claimed")
            return 0
        print(f"FAIL: claimed first zero-run {target}, recomputed {first_run}")
        return 1
    else:
        if first_run is None:
            print(f"OK: k={k} m={m}: no zero-run of length {m} up to {target}, as claimed")
            return 0
        print(f"FAIL: claimed no zero-run up to {target}, but found one at {first_run}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
