# math-number-theory

Verified artifacts backing SciNet findings in **mathematics / number theory**.
One directory per finding: each contains a reproducible verification (`verify.sh`), the
evidence it produced, and a README that credits the original authors and states plainly what
SciNet independently checked.

SciNet's role for externally-established results is **independent verification**, not
discovery. Where a result was found and/or formalized elsewhere, the directory cites and links
those authors; the artifact here re-runs their proof/computation and records the outcome.

| dir | result | verification |
|-----|--------|--------------|
| [`erdos-728/`](erdos-728/) | Erdős Problem #728 (factorial divisibility beyond the log barrier) | Lean 4 kernel check of the formal proof (sorry-free) |
