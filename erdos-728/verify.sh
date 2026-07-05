#!/usr/bin/env bash
# Independent formal verification of the Lean 4 proof of Erdős Problem #728.
#
# Reproduces the kernel check: clones the upstream proof at a pinned commit, fetches the pinned
# mathlib olean cache, builds the answer file, and asserts the answer theorems are sorry-free
# (their axiom set is exactly {propext, Classical.choice, Quot.sound}; any sorryAx => FAIL).
#
# Exit 0 iff verified. Credit: proof by Barreto & ChatGPT-5.2; Lean by Aristotle, Barreto,
# Alexeev (github.com/plby/lean-proofs). SciNet only re-runs and checks it.
set -euo pipefail

UPSTREAM="https://github.com/plby/lean-proofs.git"
COMMIT="97957fb9083d6b321843fbb3c1cbff82e076aa66"
PROJECT="src/latest"
TARGET="ErdosProblems.Erdos728"          # defines `erdos_728` and `erdos_728_fc`
WORK="$(mktemp -d)"; LOG="$WORK/verify728.log"

echo "[1/4] ensure elan (Lean toolchain manager)"
if ! command -v elan >/dev/null 2>&1 && [ ! -x "$HOME/.elan/bin/elan" ]; then
  curl -sSf https://elan.lean-lang.org/elan-init.sh | sh -s -- -y --default-toolchain none
fi
export PATH="$HOME/.elan/bin:$PATH"

echo "[2/4] clone upstream proof @ $COMMIT"
git clone --quiet "$UPSTREAM" "$WORK/lean-proofs"
git -C "$WORK/lean-proofs" checkout --quiet "$COMMIT"
cd "$WORK/lean-proofs/$PROJECT"

echo "[3/4] fetch mathlib cache + build (kernel check)"
lake exe cache get
lake build "$TARGET" 2>&1 | tee "$LOG"

echo "[4/4] assert success + soundness"
grep -q "Build completed successfully" "$LOG" || { echo "FAIL: build did not complete"; exit 1; }
rc=0
for thm in erdos_728 erdos_728_fc; do
  line="$(grep "\.$thm' depends on axioms" "$LOG" || true)"
  [ -n "$line" ] || { echo "FAIL: no axiom report for $thm"; rc=1; continue; }
  echo "  $line"
  echo "$line" | grep -q "sorryAx" && { echo "FAIL: $thm depends on sorryAx"; rc=1; }
  echo "$line" | grep -q "propext, Classical.choice, Quot.sound" \
    || { echo "FAIL: unexpected axioms for $thm"; rc=1; }
done
[ "$rc" -eq 0 ] && echo "VERIFIED: Erdős #728 proof kernel-checks, sorry-free." || echo "VERIFICATION FAILED."
exit "$rc"
