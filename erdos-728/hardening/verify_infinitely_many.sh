#!/usr/bin/env bash
# Deeper faithfulness analysis of Erdős #728 (the "infinitely many" reading).
#
# An INDEPENDENT blind formalization of #728's "infinitely many triples" reading
# (Erdos728InfinitelyMany.Statement — "infinitely many" encoded as `Set.Infinite`, two-sided window,
# a,b ∈ [εn,(1−ε)n]) is proven to IMPLY the resolved proof's (one-sided) infinite theorem's conclusion
# (`good_triples C₁ ε).Infinite`, kernel-checked & sorry-free. This is the clean provable direction.
# NOTE (documented in the finding): the intended two-sided infinitude is captured by NEITHER single
# stated theorem of the resolved proof — `erdos_728_fc` is ∃/two-sided, `erdos_728` is infinite/one-sided
# — so the converse is a genuine residual, not closed here.
set -euo pipefail

PLBY_COMMIT="97957fb9083d6b321843fbb3c1cbff82e076aa66"
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"; LOG="$WORK/infmap.log"

command -v elan >/dev/null 2>&1 || [ -x "$HOME/.elan/bin/elan" ] || \
  curl -sSf https://elan.lean-lang.org/elan-init.sh | sh -s -- -y --default-toolchain none
export PATH="$HOME/.elan/bin:$PATH"

git clone --quiet https://github.com/plby/lean-proofs.git "$WORK/lp"
git -C "$WORK/lp" checkout --quiet "$PLBY_COMMIT"
cd "$WORK/lp/src/latest"
cp "$HERE/Erdos728InfinitelyMany.lean" "$HERE/Erdos728InfMap.lean" ErdosProblems/
lake exe cache get
lake build ErdosProblems.Erdos728InfMap 2>&1 | tee "$LOG"

grep -q "Build completed successfully" "$LOG" || { echo "FAIL: build did not complete"; exit 1; }
line="$(grep "'Erdos728InfMap.infMany_imp_goodTriplesInfinite' depends on axioms" "$LOG" || true)"
[ -n "$line" ] || { echo "FAIL: no axiom report"; exit 1; }
echo "  $line"
echo "$line" | grep -q "sorryAx" && { echo "FAIL: depends on sorryAx"; exit 1; }
echo "$line" | grep -q "propext, Classical.choice, Quot.sound" || { echo "FAIL: unexpected axioms"; exit 1; }
echo "VERIFIED: the independent 'infinitely many' (Set.Infinite, two-sided) reading of #728 implies the"
echo "         resolved proof's one-sided infinite theorem (good_triples.Infinite) — kernel-checked, pure-kernel."
