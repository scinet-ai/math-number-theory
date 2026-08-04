#!/bin/sh
# Re-checks, from scratch, the numerical sanity certificates supporting
# proof_collinear.md and proof_uniform_bound.md (Erdős #1041 workspace).
# Deterministic (fixed seed). Runtime ~1-2 min. Exit 0 iff all checks pass.
cd "$(dirname "$0")"
exec uv run --with numpy --with scipy python3 sanity_checks.py
