#!/usr/bin/env python3
"""Aggregate the banked order-30 chunks into a certified whole-run result.

Checks that every chunk 0..CHUNK_COUNT-1 is banked, sums tree counts and the
order-independent sequence hashes, and compares the total count against the
OEIS A000055 value for n = 30.  Exits nonzero unless the sweep is complete
and the count matches exactly.
"""
import os
import re
import sys

CHUNK_COUNT = 240
EXPECTED_TREES = 14_830_871_802  # OEIS A000055(30)
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

line_pattern = re.compile(
    r"^CHECK trees=(\d+) nonunimodal=(\d+) nonlogconcave=(\d+) "
    r"hash=([0-9a-f]{16}) gentreeg_nout=(\d+) cpu=([\d.]+)"
)


def main():
    missing = []
    total_trees = total_nonuni = total_nonlc = 0
    hash_sum = 0
    total_cpu = 0.0
    for c in range(CHUNK_COUNT):
        path = os.path.join(LOG_DIR, f"chunk30_{c}.done")
        if not os.path.exists(path):
            missing.append(c)
            continue
        with open(path) as fh:
            match = None
            for line in fh:
                match = line_pattern.match(line) or match
        if match is None:
            print(f"ERROR: chunk {c}: banked file has no CHECK line")
            sys.exit(1)
        trees, nonuni, nonlc, hexhash, nout, cpu = match.groups()
        if trees != nout:
            print(f"ERROR: chunk {c}: checker count {trees} != gentreeg count {nout}")
            sys.exit(1)
        total_trees += int(trees)
        total_nonuni += int(nonuni)
        total_nonlc += int(nonlc)
        hash_sum = (hash_sum + int(hexhash, 16)) % 2**64
        total_cpu += float(cpu)

    if missing:
        print(f"INCOMPLETE: {len(missing)} chunks missing: {missing[:20]}"
              f"{' ...' if len(missing) > 20 else ''}")
        print(f"So far: trees={total_trees:,} nonunimodal={total_nonuni} "
              f"nonlogconcave={total_nonlc}")
        sys.exit(3)

    print(f"chunks:          {CHUNK_COUNT}/{CHUNK_COUNT}")
    print(f"trees checked:   {total_trees:,}")
    print(f"expected (OEIS A000055(30)): {EXPECTED_TREES:,}")
    print(f"non-unimodal:    {total_nonuni}")
    print(f"non-log-concave: {total_nonlc}")
    print(f"sequence hash:   {hash_sum:016x}")
    print(f"total checker CPU seconds: {total_cpu:,.0f}")
    if total_trees != EXPECTED_TREES:
        print("ERROR: tree count does not match OEIS A000055(30) — sweep NOT certified")
        sys.exit(1)
    print("CERTIFIED: every tree on 30 vertices was generated exactly once and checked")
    sys.exit(0)


if __name__ == "__main__":
    main()
