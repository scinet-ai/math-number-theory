#!/usr/bin/env python3
"""Cross-validate the C dynamic-programming checker against a brute force.

Reads two streams for each order n in a range:
  1. `gentreeg -p -q n`            -> parent arrays (ground-truth tree list)
  2. `gentreeg_independence_debug` -> "SEQ ... par=... seq=..." lines from the DP

For every tree the brute force enumerates all 2^n vertex subsets, counts the
independent ones by size (an implementation sharing no logic with the DP), and
compares the resulting sequence with the DP output, tree by tree, in order.
Exits nonzero on any mismatch.
"""
import subprocess
import sys

GENTREEG = "./nauty2_8_9/gentreeg"
CHECKER_DEBUG = "./gentreeg_independence_debug"  # overridable via argv[3]


def brute_force_sequence(parents):
    n = len(parents)  # parents[i] is the parent (1-based) of vertex i+1; parents[0] == 0
    edges = []
    for child_1based in range(2, n + 1):
        parent_1based = parents[child_1based - 1]
        edges.append((child_1based - 1, parent_1based - 1))  # 0-based
    adj_mask = [0] * n
    for a, b in edges:
        adj_mask[a] |= 1 << b
        adj_mask[b] |= 1 << a
    counts = [0] * (n + 1)
    for subset in range(1 << n):
        s = subset
        independent = True
        while s:
            v = (s & -s).bit_length() - 1
            if adj_mask[v] & subset:
                independent = False
                break
            s &= s - 1
        if independent:
            counts[bin(subset).count("1")] += 1
    while counts and counts[-1] == 0:
        counts.pop()
    return counts


def main():
    global CHECKER_DEBUG
    n_lo, n_hi = int(sys.argv[1]), int(sys.argv[2])
    if len(sys.argv) > 3:
        CHECKER_DEBUG = sys.argv[3]
    total = 0
    for n in range(n_lo, n_hi + 1):
        gen = subprocess.run([GENTREEG, "-p", "-q", str(n)],
                             capture_output=True, text=True, check=True)
        parent_lines = [l for l in gen.stdout.splitlines() if l.strip()]

        chk = subprocess.run([CHECKER_DEBUG, "-q", str(n)],
                             capture_output=True, text=True, check=True)
        seq_lines = [l for l in chk.stdout.splitlines() if l.startswith("SEQ ")]

        if len(parent_lines) != len(seq_lines):
            print(f"FAIL n={n}: {len(parent_lines)} trees from gentreeg "
                  f"but {len(seq_lines)} sequences from checker")
            sys.exit(1)

        for raw_par, raw_seq in zip(parent_lines, seq_lines):
            parents = [int(x) for x in raw_par.split()]
            fields = dict(kv.split("=") for kv in raw_seq.split()[1:])
            checker_parents = [int(x) for x in fields["par"].split(",")]
            checker_seq = [int(x) for x in fields["seq"].split(",")]
            if parents != checker_parents:
                print(f"FAIL n={n}: tree order mismatch {parents} vs {checker_parents}")
                sys.exit(1)
            expected = brute_force_sequence(parents)
            if expected != checker_seq:
                print(f"FAIL n={n} par={parents}: brute force {expected} "
                      f"!= checker {checker_seq}")
                sys.exit(1)
        total += len(parent_lines)
        print(f"ok n={n}: {len(parent_lines)} trees, all sequences match")
    print(f"PASS: {total} trees cross-checked against brute force")


if __name__ == "__main__":
    main()
