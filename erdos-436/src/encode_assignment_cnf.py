#!/usr/bin/env python3
"""CNF encoder for the consecutive k-th power residue assignment problem.

Question encoded (Erdos #436): does there exist a completely multiplicative
f : {1,...,B+m-1} -> Z/k with NO window of m consecutive zeros starting at
any r in [1, B]?

  SAT   -> such f exists; via Mills' preassigned-character theorem (odd k)
           infinitely many primes p realize it, so Lambda(k,m) >= B+1.
  UNSAT -> every f has a zero window starting <= B; since the k-th power
           residue character of any prime p > B+m-1 (with p = 1 mod k) is
           such an f, r(k,m,p) <= B for ALL such p, so Lambda(k,m) <= B.

Hence Lambda(k,m) = B*+1 where B* is the largest SAT bound.

Encoding: one-hot block of k Boolean variables per integer n in [1, B+m-1]
(variable v(n,i) means f(n) = i).  Blocks of composites are channeled to
smallest-prime-factor blocks: v(q,i) & v(n/q,j) -> v(n,(i+j) mod k).
f(1) = 0 is a unit.  Symmetry breaking (global scaling of Z/k): the value
at the prime 2 is restricted to {0, 1}.

Usage:
  encode:  encode_assignment_cnf.py encode k m B out.cnf
  decode:  encode_assignment_cnf.py decode k m B kissat_output.txt cert.txt
           (extracts the model into a certificate for verify_certificate.py)
"""
import sys


def var(n: int, i: int, k: int) -> int:
    return (n - 1) * k + i + 1


def smallest_factors(limit: int):
    spf = list(range(limit + 1))
    i = 2
    while i * i <= limit:
        if spf[i] == i:
            for j in range(i * i, limit + 1, i):
                if spf[j] == j:
                    spf[j] = i
        i += 1
    return spf


def encode(k: int, m: int, bound: int, out_path: str) -> None:
    top = bound + m - 1
    spf = smallest_factors(top)
    n_composite = sum(1 for n in range(2, top + 1) if spf[n] != n)
    n_clauses = (1 + (k - 1)                      # f(1) = 0
                 + (top - 1) * (1 + k * (k - 1) // 2)  # one-hot blocks for n >= 2
                 + n_composite * k * k            # channeling
                 + (k - 2)                        # symmetry at the prime 2
                 + bound)                         # forbidden windows
    with open(out_path, "w") as fh:
        write = fh.write
        write(f"p cnf {top * k} {n_clauses}\n")
        # f(1) = 0
        write(f"{var(1, 0, k)} 0\n")
        for i in range(1, k):
            write(f"{-var(1, i, k)} 0\n")
        for n in range(2, top + 1):
            block = [var(n, i, k) for i in range(k)]
            write(" ".join(map(str, block)) + " 0\n")  # at least one value
            for i in range(k):
                for j in range(i + 1, k):
                    write(f"{-block[i]} {-block[j]} 0\n")  # at most one value
            if spf[n] != n:
                q, s = spf[n], n // spf[n]
                lines = []
                for i in range(k):
                    vq = -var(q, i, k)
                    for j in range(k):
                        lines.append(f"{vq} {-var(s, j, k)} {var(n, (i + j) % k, k)} 0")
                write("\n".join(lines) + "\n")
        # symmetry: f(2) in {0, 1}
        for i in range(2, k):
            write(f"{-var(2, i, k)} 0\n")
        # no zero window starting at r <= bound
        for r in range(1, bound + 1):
            write(" ".join(str(-var(r + j, 0, k)) for j in range(m)) + " 0\n")
    print(f"wrote {out_path}: {top * k} vars, {n_clauses} clauses")


def decode(k: int, m: int, bound: int, solver_out: str, cert_path: str) -> None:
    lits = set()
    with open(solver_out) as fh:
        for line in fh:
            if line.startswith("v "):
                lits.update(int(t) for t in line.split()[1:] if t != "0")
    if not lits:
        print("no model lines found (UNSAT or wrong file)")
        sys.exit(1)
    top = bound + m - 1
    spf = smallest_factors(top)
    with open(cert_path, "w") as fh:
        fh.write(f"# k={k} m={m} no_zero_run_of_length_m_up_to={top}\n")
        for n in range(2, top + 1):
            if spf[n] == n:
                vals = [i for i in range(k) if var(n, i, k) in lits]
                assert len(vals) == 1, (n, vals)
                fh.write(f"{n} {vals[0]}\n")
    print(f"wrote {cert_path}")


if __name__ == "__main__":
    mode = sys.argv[1]
    k, m, bound = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    if mode == "encode":
        encode(k, m, bound, sys.argv[5])
    elif mode == "decode":
        decode(k, m, bound, sys.argv[5], sys.argv[6])
    else:
        sys.exit("mode must be encode or decode")
