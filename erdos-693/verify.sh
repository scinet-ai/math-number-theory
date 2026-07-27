#!/bin/sh
# verify.sh — spot-verification for the Erdős #693 computation (~1-2 min).
# Nonzero exit on any mismatch.
set -e
cd "$(dirname "$0")"
clang -O3 -o sieve sieve.c
python3 verify.py
