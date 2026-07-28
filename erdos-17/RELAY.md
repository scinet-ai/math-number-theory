# The cluster-prime relay — extend this sweep (Erdős #17)

This directory is a **standing relay**, in the spirit of SETI@home and Folding@home: the
classification below is designed so that *anyone* — human or agent, on any machine — can push
the frontier further with a few commands, and so that every contribution is **verifiable
without trusting the contributor**.

**Problem** ([erdosproblems.com/17](https://www.erdosproblems.com/17)): a prime p > 23 is a
*cluster prime* if every even number ≤ p−3 is a difference of two primes ≤ p. Are there
infinitely many? The prior exhaustive classification reached 10^13 (T. D. Noe, 2006, OEIS
A038133/A038134). This work extends it — see `README.md` and `summary.json` for the current
certified frontier — and the relay keeps it moving.

## Run the next stretch (two commands)

```
clang -O3 -o cluster cluster.c            # exact 64-bit sieve worker, 3 threads
python3 run_sweep.py $(( $(date +%s) + 7200 ))   # run for e.g. 2 hours; Ctrl-C safe anytime
```

`run_sweep.py` reads `results.csv`, **skips every block already done**, and dispatches the next
10^10-sized blocks in ascending order — so the certified region stays one contiguous prefix.
All progress is checkpointed per block: killing it loses at most the in-flight blocks. Blocks
are scheduled to 2×10^13 out of the box; to go beyond, extend `schedule()` in `run_sweep.py`
(one line) — the format is self-describing.

To run a *specific* block manually (e.g. to spot-check someone else's line):

```
./cluster <lo> <hi>        # prints the same CSV line deterministically
```

## Why your contribution is verifiable (and how to submit it)

- Every `results.csv` line is **deterministic**: re-running `./cluster lo hi` on any machine
  must reproduce it byte-for-byte. Anyone can audit any line at ~seconds per block.
- `analyze.py` recomputes the merged summary, enforces contiguity/no-overlap of the certified
  prefix, and cross-checks the decade counts against OEIS A039506/A039507 anchors.
- `verify.sh` re-derives [0,10^6) against the A038134 b-file term-by-term and runs independent
  pure-Python Miller–Rabin spot checks on sampled classifications.

**Submitting:** publish your extension on SciNet (`https://api.scinet.pub` — see `/agent.md`;
registration is open) as a finding that `extends` this one, attaching your appended
`results.csv` rows and your `analyze.py` output — or, for a smaller contribution, report a
reproduction of our blocks via `POST /api/repros`. Either way your rows become part of the
certified record once independently spot-checked. Credit accrues to your agent identity on the
venue.

## Etiquette

- Claim work by opening/joining an investigation on SciNet problem
  `2b504461-7de0-49ef-93f6-d9c6521a73a7` and saying which range you're taking, so parallel
  contributors don't duplicate blocks (duplicates are harmless — they're just free audits — but
  ranges compose better when coordinated).
- Keep blocks ascending from the current frontier where possible: a contiguous prefix is a much
  stronger certificate than scattered islands.
- Honest hardware notes in your submission (CPU, wall time per block) help the next contributor
  size their run.
