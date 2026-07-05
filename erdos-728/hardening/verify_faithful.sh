#!/usr/bin/env bash
# Hardening of the Erdős #728 faithfulness claim.
#
# An INDEPENDENT Lean formalization of #728 (Erdos728Independent.Statement — authored blind to the
# resolved statement, with different formalization choices: an explicit ε-threshold rather than a
# filter, and the ℕ-truncated excess a+b−n rather than a+b directly) is proven EQUIVALENT to the
# exact statement the resolved proof establishes (erdos_728_fc), kernel-checked and sorry-free.
# This upgrades faithfulness from "textual match against the community statement" to "machine-verified
# equivalence between two independently-authored formalizations."
#
# It builds `Erdos728Faithful.faithful : Erdos728Independent.Statement ↔ FC728`, where FC728 is
# anchored to the real theorem by a type-checking `example : FC728 := ...erdos_728_fc` (so the
# equivalence is against the genuine resolved statement, not a re-typed lookalike).
set -euo pipefail

PLBY_COMMIT="97957fb9083d6b321843fbb3c1cbff82e076aa66"   # provides Lean v4.32.0-rc1 + mathlib + Erdos728 (the resolved proof)
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"; LOG="$WORK/faithful.log"

echo "[1/4] ensure elan"
command -v elan >/dev/null 2>&1 || [ -x "$HOME/.elan/bin/elan" ] || \
  curl -sSf https://elan.lean-lang.org/elan-init.sh | sh -s -- -y --default-toolchain none
export PATH="$HOME/.elan/bin:$PATH"

echo "[2/4] clone the env + the resolved #728 proof (Erdos728)"
git clone --quiet https://github.com/plby/lean-proofs.git "$WORK/lp"
git -C "$WORK/lp" checkout --quiet "$PLBY_COMMIT"
cd "$WORK/lp/src/latest"

echo "[3/4] drop in the independent formalization + the equivalence proof, and build"
cp "$HERE/Erdos728Independent.lean" "$HERE/Erdos728Faithful.lean" ErdosProblems/
lake exe cache get
lake build ErdosProblems.Erdos728Faithful 2>&1 | tee "$LOG"

echo "[4/4] assert the equivalence is pure-kernel and sorry-free"
grep -q "Build completed successfully" "$LOG" || { echo "FAIL: build did not complete (so the anchoring example : FC728 := erdos_728_fc also did not type-check)"; exit 1; }
line="$(grep "'Erdos728Faithful.faithful' depends on axioms" "$LOG" || true)"
[ -n "$line" ] || { echo "FAIL: no axiom report for faithful"; exit 1; }
echo "  $line"
echo "$line" | grep -q "sorryAx" && { echo "FAIL: faithful depends on sorryAx"; exit 1; }
echo "$line" | grep -q "propext, Classical.choice, Quot.sound" || { echo "FAIL: unexpected axioms for faithful"; exit 1; }
echo "VERIFIED: an independent, blind formalization of Erdős #728 is kernel-checked equivalent"
echo "         (pure-kernel [propext, Classical.choice, Quot.sound], no sorryAx) to the resolved statement."
