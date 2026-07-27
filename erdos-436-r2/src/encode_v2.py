#!/usr/bin/env python3
"""Round-2 CNF encoder for the consecutive k-th power residue assignment
problem (Erdos #436), now correct for EVEN k as well as odd k.

Question encoded: does there exist a completely multiplicative
f : {1,...,B+m-1} -> Z/k, *admissible* in the sense below, with NO window
of m consecutive zeros starting at any r in [1, B]?

Admissibility (the even-k correction, following Rabung-Jordan 1970 and
Reble 2019; derived from quadratic reciprocity):
  - If 8 | k:  f(2) must be EVEN.  Reason: an order-k character mod p
    requires p = 1 (mod k), hence p = 1 (mod 8), hence (2|p) = +1; but
    chi^(k/2)(2) = (-1)^f(2) = (2|p).  So the index of 2 is even.  For
    odd primes q, (q|p) = (p|q) (p = 1 mod 4) is free via CRT, and the
    only multiplicative entanglement among the Kummer generators is
    sqrt(2) in Q(zeta_8), so no other constraint arises.  For k not
    divisible by 8 (including k = 2, 4, 6), p mod 8 is unconstrained by
    p = 1 (mod k) with enough freedom that no constraint arises.
  - SAT  -> admissible f exists; by Mills' preassigned-character theorem
            (used for k = 8 exactly this way by Rabung-Jordan 1970),
            infinitely many p realize it: Lambda(k,m) >= B+1.
  - UNSAT -> every admissible f has a zero window starting <= B.  The
            index character mod any p > B+m-1 reduces to an admissible f
            (for every gcd class d = gcd(k, p-1): lift the mod-d index
            character g to f = (k/d)*g, which has the same zero set and
            f(2) = (k/d) g(2) even whenever 8 | k and d < k... [d=k case
            is the character itself, admissible since p = 1 mod 8]), so
            r(k,m,p) <= B for all p > B+m-1: Lambda(k,m) <= B.

Hence Lambda(k,m) = B* + 1 where B* is the largest SAT bound.

Encoding (one-hot, lean):
  - var(n,i), i in [0,k): "f(n) = i".  n in [1, B+m-1].
  - n = 1: unit v(1,0).
  - primes p: exactly-one over the k literals (ALO + pairwise AMO).
  - composites n (spf q, s = n/q): channeling only,
        v(q,i) & v(s,j) -> v(n,(i+j) mod k).
    No ALO/AMO on composites: channeling forces the true-value literal,
    which is the only literal windows test negatively, so soundness in
    both directions is preserved (models of real f satisfy everything;
    any model yields a real f via its prime blocks whose zero windows
    are blocked).
  - windows: clause NOT(v(r,0) & ... & v(r+m-1,0)) for r in [1,B].
  - symmetry breaking + admissibility at n = 2: the unit group of Z/k
    acts on solutions by global rescaling (preserving zero sets and
    admissibility); orbits of values are gcd classes, so f(2) may be
    restricted to {0} u {d : d | k, d < k}, intersected with the even
    values when 8 | k.  (Round 1 used {0,1}, valid only for prime k.)

Usage:
  encode_v2.py encode k m B out.cnf [--free2]   (--free2: drop the 8|k
                                                 parity constraint at 2,
                                                 for control runs ONLY)
  encode_v2.py decode k m B solver_output cert.txt
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


def allowed_at_2(k: int, free2: bool):
    reps = {0} | {d for d in range(1, k) if k % d == 0}
    if k % 8 == 0 and not free2:
        reps = {a for a in reps if a % 2 == 0}
    return sorted(reps)


def encode(k: int, m: int, bound: int, out_path: str, free2: bool) -> None:
    top = bound + m - 1
    spf = smallest_factors(top)
    allow2 = allowed_at_2(k, free2)
    n_primes = sum(1 for n in range(2, top + 1) if spf[n] == n)
    n_composite = top - 1 - n_primes
    n_clauses = (1                                    # f(1) = 0
                 + n_primes * (1 + k * (k - 1) // 2)  # exactly-one at primes
                 + n_composite * k * k                # channeling
                 + (k - len(allow2))                  # forbidden values at 2
                 + bound)                             # forbidden windows
    with open(out_path, "w", buffering=1 << 22) as fh:
        write = fh.write
        write(f"p cnf {top * k} {n_clauses}\n")
        write(f"{var(1, 0, k)} 0\n")
        for n in range(2, top + 1):
            if spf[n] == n:
                block = [var(n, i, k) for i in range(k)]
                lines = [" ".join(map(str, block)) + " 0"]
                for i in range(k):
                    for j in range(i + 1, k):
                        lines.append(f"{-block[i]} {-block[j]} 0")
                write("\n".join(lines) + "\n")
            else:
                q, s = spf[n], n // spf[n]
                lines = []
                for i in range(k):
                    vq = -var(q, i, k)
                    base = var(n, 0, k)
                    for j in range(k):
                        lines.append(f"{vq} {-var(s, j, k)} {base + (i + j) % k} 0")
                write("\n".join(lines) + "\n")
        for i in range(k):
            if i not in allow2:
                write(f"{-var(2, i, k)} 0\n")
        for r in range(1, bound + 1):
            write(" ".join(str(-var(r + j, 0, k)) for j in range(m)) + " 0\n")
    print(f"wrote {out_path}: k={k} m={m} B={bound} vars={top * k} "
          f"clauses={n_clauses} allow_f2={allow2}", flush=True)


def decode(k: int, m: int, bound: int, solver_out: str, cert_path: str) -> None:
    # keep only POSITIVE literals: decode reads membership of var(n,i) for
    # primes n only, and storing the ~80% negative literals of a 50M-var
    # model would waste several GB of RAM for nothing.
    lits = set()
    with open(solver_out) as fh:
        for line in fh:
            if line.startswith("v "):
                lits.update(int(t) for t in line.split()[1:]
                            if t != "0" and not t.startswith("-"))
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
    print(f"wrote {cert_path}", flush=True)


if __name__ == "__main__":
    mode = sys.argv[1]
    k, m, bound = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    if mode == "encode":
        encode(k, m, bound, sys.argv[5], "--free2" in sys.argv[6:])
    elif mode == "decode":
        decode(k, m, bound, sys.argv[5], sys.argv[6])
    else:
        sys.exit("mode must be encode or decode")
