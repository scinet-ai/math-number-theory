# Novelty search log (Erdős #51 workspace)

Date: 2026-08-04. Everything below was checked before wording the novelty claims in
`proof_ratio2_family.md`, `proof_obstruction_lemmas.md`, `computation.md`,
`finding_draft.json`. Names and sequence data are copied from the primary sources
fetched during this session, not from memory.

## Primary problem sources (cached copies in session scratchpad: e51.html, f51.html)

* erdosproblems.com/51 (page last edited 30 Sep 2025, fetched 2026-08-04): status OPEN,
  "cannot be resolved with a finite computation", 0 claimed proofs, nobody working on it.
  Remarks mention only Carmichael's question, Erdős's theorem on it, problem #694, and
  Guy's B36/B39. **No mention of the ratio-2 family, no limsup constant, no record
  computations.** Related OEIS listed there: A002202, A014197 only.
* Forum thread 51 (fetched 2026-08-04): comments by DanielLarsen, Thomas Bloom,
  Nat Sothanaphan, TerenceTao, Kevin Barreto, Vjeko_Kovac (names as displayed).
  Content: the failed ChatGPT proof (11 Jan 2026) and its refutation; Tao's
  bounded-ratio heuristic; Kovač's Fermat-prime caveat and #203 link. **No positive
  partial results claimed by anyone.**

## OEIS (api queried 2026-08-04 with browser UA; full JSON saved in scratchpad)

* A002202 (totient values), A014197 (preimage counts) — the two sequences on the
  problem page.
* **A002181** (least k with phi(k)=m): T. D. Noe comment (Aug 14 2008): "According to
  Guy, the first even term is for 2m = 16842752 = 257*2^16. If there are only five
  Fermat primes, then terms will be even for 2m = 2^r for all r > 31. This was
  discussed in problem E3361." → prior art for the 2^k/Fermat dichotomy (conditional
  phrasing). Reference: Wardlaw, Foster, Simpson, Problem E3361, Amer. Math. Monthly
  98 (1991) no. 5, 443-444 (JSTOR 2323869; paywalled, not read — cited via the OEIS
  comment and reference list).
* **A387221** (even terms of A002181; Jud McCranie, Nov 23 2025): contains
  2^33, 2^34, 2^35, 2^36, 2^37 as terms — i.e., raw data instances of our Theorem 1
  (f(2^k)=2^(k+1) for k=32..36), with no proof or characterization attached.
* **A393265** (Jud McCranie, Feb 07 2026): totient values k at which
  A002181(x)/k reaches a record: 2, 8, 128, 5888, 2037248, 387383296; comments
  "a(4)-a(6) are all multiples of 2^8*23 = 5888", "No more terms < 1.2*10^11."
  → the record *positions* are known (no b-file of ratios, no certification method
  stated, no census of all ratio>=2 values, no code). Our sieve reproduces exactly
  this sequence and certifies it (with proofs of completeness) for a <= 3.0642e10.
* **A393266** (McCranie, Feb 07 2026): record positions of f_max/f_min — the #694
  quantity, distinct from ours.
* Search "2037248": only A393265. No OEIS sequence gives the ratio->=2 census or the
  certified f(a)/a table.

## Literature

* R. K. Guy, Unsolved Problems in Number Theory, B36/B39 — cited by the problem page
  as the home of this discussion; A002181 lists Guy B39 as its reference. Not re-read
  directly (no copy at hand); prior-art attribution for the even-least-preimage
  phenomenon is made via Guy through the Noe/OEIS comment and E3361.
* K. Ford, The distribution of totients (Ramanujan J. 1998; arXiv:1104.3264): totient
  counting V(x); no smallest-preimage-ratio results of our kind.
* Erdős #694 (solved by GPT-5.5 Pro, May 2026, per the recon brief): concerns
  f_max/f_min — adjacent machinery, does not contain our statements.
* WebSearch 2026-08-04: "Erdos problem 51 totient smallest preimage limsup / ratio 2 /
  Fermat primes 2^k arXiv" and variants — no hit stating limsup n_a/a >= 2, no hit on
  an unconditional exact-ratio-2 family, no certified record tables.
* Rosser–Schoenfeld explicit Mertens bound: statement cross-checked against
  Integers 20 (2020) #A103 and arXiv:1703.08032 (see caveat in
  proof_obstruction_lemmas.md).

## Resulting novelty position (what we claim / don't claim)

1. Theorem 1 classification: **classical** (E3361/Guy territory); we claim only the
   write-up with complete proofs.
2. Unconditional infinitude of totient values with ratio EXACTLY 2 + the consequence
   limsup_{a in V} n_a/a >= 2 for #51: **apparently unrecorded anywhere we searched**;
   elementary; claimed as "new packaging of classical facts, first proved constant
   recorded for #51".
3. Obstruction pack (f(a)/a <= 2*sqrt(2*v_2(a)+1); exponential v_2 forcing;
   loglog upper bound): the loglog upper bound is known folklore (claimed as such);
   the elementary v_2 inequality in this exact form: not found anywhere, but too
   elementary to claim as more than an observation; the exponential forcing is
   assembled from standard explicit estimates.
4. Computation: record POSITIONS already in A393265 (uncertified, to 1.2e11 — beyond
   our certified range). New here: the certification lemma + proofs, the complete
   ratio>=2 census for a <= 3.0642e10, the reproducible open code + independent
   verification pipeline, and independent confirmation of A393265's terms within our
   certified range.
