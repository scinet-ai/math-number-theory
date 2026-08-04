#!/bin/sh
# Re-verify all computational claims for the Erdős #616 small-r theorem pack
# from scratch. Exit code 0 iff everything passes.
#
#   sh verify.sh
#
# Requirements: python3 (stdlib only) for verify_616.py;
#               scipy + numpy for the optional LP cross-check
#               (verify_atoms_lp.py is skipped with a warning if scipy is absent).
set -e
cd "$(dirname "$0")"

echo "### verify_616.py (stdlib only: gadget, direct window enumeration,"
echo "###   tau, pendant extension, negative controls)"
python3 code/verify_616.py

echo
if python3 -c "import scipy, numpy" 2>/dev/null; then
    echo "### verify_atoms_lp.py (scipy LP cross-check of the span lemma)"
    python3 code/verify_atoms_lp.py
else
    echo "WARNING: scipy not available; skipping LP cross-check (not required"
    echo "for the main certificates)."
fi

echo
echo "ALL VERIFICATIONS COMPLETE"
