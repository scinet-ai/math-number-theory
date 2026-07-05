#!/usr/bin/env bash
# Independent formal verification of the Lean 4 proof of Erdős Problem #347.
#
# The proof (E. Barschkis, formalized with Aristotle; construction idea due to Terence Tao and
# Wouter van Doorn) was generated against Lean v4.24.0 + mathlib@f897ebcf. We reuse plby/lean-proofs'
# pinned `src/v4.24.0` project PURELY as that mathlib environment (it happens to pin the exact same
# mathlib commit), drop in the ebarschkis proof at a pinned commit, build it, and check the axiom set.
#
# HONESTY NOTE: this proof is sorry-free (no admitted gaps) BUT uses `native_decide` (two finite
# base-case evaluations), so its trusted computing base includes `Lean.ofReduceBool` +
# `Lean.trustCompiler` on top of the standard `[propext, Classical.choice, Quot.sound]`. That means
# part of the trust rests on the Lean COMPILER's native evaluation, not the kernel alone — a strictly
# larger trusted base than a pure-kernel proof (cf. erdos-728, which uses only the standard trio).
# We assert NO `sorryAx` (no gaps) and report the FULL axiom set; we do NOT claim a pure-kernel proof.
set -euo pipefail

PLBY_COMMIT="97957fb9083d6b321843fbb3c1cbff82e076aa66"   # provides the pinned v4.24.0 + mathlib@f897ebcf env
EB_COMMIT="20afb2b3e34eecd7c64807a7e2f64e0057a36e35"      # the ebarschkis/Aristotle #347 proof
MATHLIB_PIN="f897ebcf72cd16f89ab4577d0c826cd14afaafc7"
WORK="$(mktemp -d)"; LOG="$WORK/verify347.log"

echo "[1/5] ensure elan"
command -v elan >/dev/null 2>&1 || [ -x "$HOME/.elan/bin/elan" ] || \
  curl -sSf https://elan.lean-lang.org/elan-init.sh | sh -s -- -y --default-toolchain none
export PATH="$HOME/.elan/bin:$PATH"

echo "[2/5] clone the pinned Lean v4.24.0 + mathlib@$MATHLIB_PIN environment"
git clone --quiet https://github.com/plby/lean-proofs.git "$WORK/lp"
git -C "$WORK/lp" checkout --quiet "$PLBY_COMMIT"
cd "$WORK/lp/src/v4.24.0"
grep -q "$MATHLIB_PIN" lake-manifest.json \
  || { echo "FAIL: env not pinned to mathlib $MATHLIB_PIN"; exit 1; }

echo "[3/5] fetch the ebarschkis/Aristotle proof @ $EB_COMMIT"
curl -sL "https://raw.githubusercontent.com/ebarschkis/ErdosProblem/$EB_COMMIT/Problem347/Formalization.lean" \
  -o ErdosProblems/Erdos347.lean
printf '\n\n#print axioms answer_is_yes\n#print axioms main_theorem\n' >> ErdosProblems/Erdos347.lean

echo "[4/5] mathlib cache + build (kernel check)"
lake exe cache get
lake build ErdosProblems.Erdos347 2>&1 | tee "$LOG"

echo "[5/5] assert no admitted gaps + report the full trusted base"
grep -q "Build completed successfully" "$LOG" || { echo "FAIL: build did not complete"; exit 1; }
rc=0
for thm in answer_is_yes main_theorem; do
  line="$(grep "'$thm' depends on axioms" "$LOG" || true)"
  [ -n "$line" ] || { echo "FAIL: no axiom report for $thm"; rc=1; continue; }
  echo "  $line"
  echo "$line" | grep -q "sorryAx" && { echo "FAIL: $thm depends on sorryAx (admitted gap)"; rc=1; }
done
if [ "$rc" -eq 0 ]; then
  echo "VERIFIED: Erdős #347 proof builds and is sorry-free (no admitted gaps)."
  echo "CAVEAT: trusted base includes Lean.ofReduceBool + Lean.trustCompiler (native_decide) — NOT a pure-kernel proof."
else
  echo "VERIFICATION FAILED."
fi
exit "$rc"
