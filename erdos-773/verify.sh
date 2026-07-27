#!/bin/sh
# Spot-verification for the Erdos #773 computation (< 5 min).
# Nonzero exit on any mismatch. Requires: kissat on PATH; code/drat-trim
# (rebuilt from code/drat-trim.c if missing); python3 (stdlib only).
cd "$(dirname "$0")" || exit 2
[ -x code/drat-trim ] || clang -O2 -o code/drat-trim code/drat-trim.c || exit 2
PY=.venv/bin/python
[ -x "$PY" ] || PY=python3
exec "$PY" code/verify.py
