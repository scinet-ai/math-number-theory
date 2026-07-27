#!/usr/bin/env python3
"""Aggregate banked chunks for one order into a certified whole-order result.

Usage: python3 aggregate_sweep.py ORDER CHUNK_COUNT EXPECTED_TREE_COUNT

Same certification logic as aggregate_order30.py: every chunk banked, checker
count == gentreeg count per chunk, summed counts == the OEIS A000055 value
passed as EXPECTED_TREE_COUNT, order-independent hashes summed mod 2^64.
"""
import os
import re
import sys

line_pattern = re.compile(
    r"^CHECK trees=(\d+) nonunimodal=(\d+) nonlogconcave=(\d+) "
    r"hash=([0-9a-f]{16}) gentreeg_nout=(\d+) cpu=([\d.]+)"
)


def main():
    order, chunk_count, expected = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    missing = []
    total_trees = total_nonuni = total_nonlc = 0
    hash_sum = 0
    total_cpu = 0.0
    for c in range(chunk_count):
        path = os.path.join(log_dir, f"chunk{order}_{c}.done")
        if not os.path.exists(path):
            missing.append(c)
            continue
        match = None
        with open(path) as fh:
            for line in fh:
                match = line_pattern.match(line) or match
        if match is None:
            print(f"ERROR: order {order} chunk {c}: no CHECK line")
            sys.exit(1)
        trees, nonuni, nonlc, hexhash, nout, cpu = match.groups()
        if trees != nout:
            print(f"ERROR: order {order} chunk {c}: checker {trees} != gentreeg {nout}")
            sys.exit(1)
        total_trees += int(trees)
        total_nonuni += int(nonuni)
        total_nonlc += int(nonlc)
        hash_sum = (hash_sum + int(hexhash, 16)) % 2**64
        total_cpu += float(cpu)

    if missing:
        print(f"INCOMPLETE order {order}: {len(missing)} chunks missing: {missing[:20]}")
        sys.exit(3)

    status = "MATCH" if total_trees == expected else "MISMATCH"
    print(f"order {order}: chunks={chunk_count} trees={total_trees:,} "
          f"expected={expected:,} [{status}] nonunimodal={total_nonuni} "
          f"nonlogconcave={total_nonlc} hash={hash_sum:016x} cpu_s={total_cpu:,.0f}")
    sys.exit(0 if status == "MATCH" else 1)


if __name__ == "__main__":
    main()
