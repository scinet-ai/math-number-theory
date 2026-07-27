#!/usr/bin/env python3
"""Independently verify a character-assignment certificate (round 2).

Same contract as round 1's verify_certificate.py — rebuilds the completely
multiplicative f : n -> Z/k from the certificate's prime values with an
independent sieve and checks the claimed zero-run property — plus the
even-k admissibility check: when 8 | k the certificate must have the value
at the prime 2 EVEN (else Mills-type realizability fails and the
certificate does not support a Lambda lower bound).

Certificate header:  # k=K m=M no_zero_run_of_length_m_up_to=N
followed by "q value" lines for every prime q <= N.
Exits 0 on success, 1 on any mismatch.
"""
import sys
import re


def main(path: str) -> int:
    with open(path) as fh:
        header = fh.readline().strip()
        mo = re.match(r"# k=(\d+) m=(\d+) no_zero_run_of_length_m_up_to=(\d+)", header)
        if not mo:
            print(f"FAIL: bad header: {header}")
            return 1
        k, m, limit = int(mo.group(1)), int(mo.group(2)), int(mo.group(3))
        assign = {}
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            q, v = line.split()
            assign[int(q)] = int(v) % k

    if k % 8 == 0:
        if 2 <= limit and assign.get(2, 0) % 2 != 0:
            print(f"FAIL: 8 | k={k} requires f(2) even (quadratic reciprocity: "
                  f"p=1 mod 8 => (2|p)=+1), but f(2)={assign.get(2)}")
            return 1
        print(f"admissibility: f(2)={assign.get(2)} is even, OK for 8 | k")

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

    run = 0
    for n in range(1, limit + 1):
        run = run + 1 if f[n] == 0 else 0
        if run >= m:
            print(f"FAIL: claimed no zero-run up to {limit}, found one at {n - m + 1}")
            return 1
    print(f"OK: k={k} m={m}: no zero-run of length {m} up to {limit}, as claimed"
          + (" (admissible for even k)" if k % 2 == 0 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
