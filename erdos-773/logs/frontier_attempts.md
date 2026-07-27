# Frontier attempts that did NOT resolve (assembled from run outputs, 2026-07-27)

All instances are profile-strengthened decisions (code/cnf.py build_cnf_profile).

## Level 60 (self-certified chain), target t=30 (published a(60)=29 => expect UNSAT)
- chain3 single instance: TIMEOUT at 110 s cap (early call, cap misconfigured)
- cube.py --split 59 --cap-s 520: cube [59] TIMEOUT, cube [-59] TIMEOUT
  (2 x 520 s in parallel)
Chain therefore certified only to N=59.

## Level 69 (anchored track: profile = own S(1..59) + published a(60..68)),
## target t=33 (a(69) unknown; this is NEW territory)
- anchored.py single instance: TIMEOUT at 400 s
- kissat --sat --time=150 probe (SAT-tuned): no witness found (rc 0)
- cube.py --anchored --split 68 --cap-s 520: cube [68] TIMEOUT,
  cube [-68] TIMEOUT (2 x 520 s in parallel)
Weak evidence (not a result): the SAT side has always been fast in this
family (<6 s whenever a witness existed, incl. size-32@N=68 in 4.1 s with
--sat in the prior run); ~25 min of aggregate core time with no size-33
witness at N=69 hints S(69)=32, i.e. a(69)=32. UNPROVEN.

Total aggregate core time spent on unresolved frontier instances: ~45 min.

## Prior-attempt long "bet" runs (surfaced at 15:46 as prior-attempt/bets.jsonl;
## launched by the earlier partial run before this session)
- N=68, t=33 (i.e. "is S(68) >= 33?"): kissat -q --time=2700 -> UNKNOWN
  after 2700 s (45 min, plain v1 encoding, no profile)
- N=100, t=43 (i.e. "is S(100) >= 43?"): kissat -q --time=2700 -> UNKNOWN
  after 2700 s
Both corroborate frontier hardness: even 45-minute single instances do not
resolve t=33@68 or t=43@100. (Side effect: those two background processes
were still running until 15:46, competing with this session's early chain
levels for cores.)
