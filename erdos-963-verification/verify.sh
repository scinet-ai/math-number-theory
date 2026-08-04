#!/bin/sh
# Re-checks, from scratch, the machine-verifiable claims backing proof_main.md
# (Erdős #963: verification + effectivization of KoishiChan's forum proof).
# Pure-stdlib Python; deterministic (seeded). Exit 0 iff all checks pass.
set -e
cd "$(dirname "$0")"
exec python3 verify.py --seed 963
