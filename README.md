# math-number-theory

Verified artifacts backing SciNet findings in **mathematics / number theory**.
One directory per finding: each contains a reproducible verification (`verify.sh`), the
evidence it produced, and a README that credits the original authors and states plainly what
SciNet independently checked.

SciNet's role for externally-established results is **independent verification**, not
discovery. Where a result was found and/or formalized elsewhere, the directory cites and links
those authors; the artifact here re-runs their proof/computation and records the outcome.

## Findings

| dir | result | verification | trusted base |
|-----|--------|--------------|--------------|
| [`erdos-728/`](erdos-728/) | Erdős #728 — factorial divisibility $a!\,b! \mid n!\,(a{+}b{-}n)!$ in the $n+\Theta(\log n)$ window | Lean 4 kernel check of the formal proof, **sorry-free** | **pure-kernel** `[propext, Classical.choice, Quot.sound]` |
| [`erdos-728/hardening/`](erdos-728/hardening/) | #728 faithfulness hardening: an independent blind re-formalization proven `↔` the resolved statement (kernel-checked), plus a deeper "infinitely-many" (`Set.Infinite`) analysis | Lean 4, sorry-free; `example : FC728 := erdos_728_fc` anchors it to the real theorem | pure-kernel |
| [`erdos-340/`](erdos-340/) | Erdős #340 — growth of the Mian–Chowla (greedy Sidon) sequence; numerical evidence that $A(N)/N^{1/2}\to0$ | Python (stdlib), deterministic; OEIS A005282 anchor + `verify.sh` | n/a (computational finding, not a formal proof) |
| [`erdos-347/`](erdos-347/) | Erdős #347 — a sequence with $a_{n+1}/a_n \to 2$ whose every cofinite subsequence has an element dividing another | Lean 4 build + `#print axioms`, sorry-free | **native_decide** — enlarged TCB (`Lean.ofReduceBool`, `Lean.trustCompiler`), **disclosed** |
| [`erdos-273/`](erdos-273/) | Erdős #273 (OPEN) — covering systems with all moduli of the form $p-1$ ($p\ge5$): **bounded non-existence**, no covering exists using admissible moduli $\le 276$ | Python (`sympy`/`numpy`/`python-sat`), deterministic; local-density removal lemma validated + Cadical UNSAT on small cores + `verify.sh` | n/a (computational finding, not a formal proof) |
| [`erdos-373/`](erdos-373/) | Erdős #373 (OPEN) — $n! = a_1!\cdots a_k!$ with $a_1 \le n-2$: exhaustive search to $n \le 10^7$ finds only the three known solutions $\{9, 10, 16\}$ (honest negative — no new witness) | Python (stdlib), exact Legendre-valuation arithmetic; known-solution anchor + `verify.sh` | n/a (computational finding, not a formal proof) |
| [`erdos-276/`](erdos-276/) | Erdős #276 (OPEN) — Ismailescu–Son all-composite Lucas sequence: **certified no covering obstruction with primes $\le 10^{11}$** (their unpublished 803-survivor count reproduced bit-for-bit; excluded-prime bound raised 50,000×, $2{\cdot}10^6 \to 10^{11}$) | period/zero-set sieve + libprimesieve, two independent verification paths, $\pi(10^{11})$ reconciliation + `verify.sh` | n/a (computational; BPSW probable-primality on 4 auxiliary factors disclosed, headline independent of it) |
| [`erdos-160/`](erdos-160/) | Erdős #160 (OPEN) — fewest colours so every 4-AP in $\{1..N\}$ sees $\ge3$ colours: **first certified exact $h(N)$ table for $N\le51$** with witness colourings + DRAT-verified infeasibility | CP-SAT/kissat + drat-trim, independent witness checker + `verify.sh` | n/a (computational finding) |
| [`erdos-693/`](erdos-693/) | Erdős #693 (OPEN) — max gap $G(n,k)$ between integers in $[n,n^k]$ with a divisor in $(n,2n)$: **first computational record** — exact $k=2$ values for all $n\in[3,2000]$ (+ grids/landmarks to $10^6$, $G(10^6,2)=77$), $k=3$ to $10^4$; OEIS A391118 extended 81 → 1998 terms; growth fits $(\log n)^{\sim1.65}$ | C segmented bitset sieve, full-interval sweeps, per-entry witnesses + `verify.sh` (OEIS anchor 81/81, cross-algorithm recompute) | n/a (computational finding) |
| [`erdos-1020/`](erdos-1020/) | Erdős #1020 (OPEN, matching conjecture) — **40 new certified exact values** of $f(n;r,k)$ closing all five reachable open windows (r=4: k=3,4,5; r=5: k=3; r=6: k=3); conjecture confirmed in each, incl. $f(21;4,5)=3876$ | CP-SAT certified optimality + shifting WLOG (Frankl 1987) + partition-canonicalization lemma (README); lower bounds solver-independent (edge-verified families); HiGHS independent re-derivation on 11 cells + `verify.sh` | n/a (computational; shifting lemma proved in README, disclosed) |
| [`erdos-773/`](erdos-773/) | Erdős #773 (OPEN) — largest Sidon subset of $\{1^2,\dots,N^2\}$: **first machine-checkable certificate chain for $S(1..59)$** (kissat DRAT, matches OEIS A390813) + new certified lower bounds $S(200)\ge65$, $S(300)\ge80$; exact frontier $n=68$ not extended (hardness data logged) | kissat + DRAT (drat-trim), witnesses re-verified in exact integer arithmetic + `verify.sh` | n/a (computational; UNSAT lemmas above level 53 conditional on certified prefix, disclosed) |
| [`erdos-436-r2/`](erdos-436-r2/) | Erdős #436 round 2 — **$\Lambda(8,2)\ge1{,}501{,}284$, strictly improving Reble's 2019 lower bound** on the last open $\Lambda(k,2)$ entry (upper bound 1,508,324 reconfirmed by an independent method); even-$k$ encoding validated on $\Lambda(2,2),\Lambda(4,2),\Lambda(6,2)$; **$\Lambda(5,3)\ge10{,}000{,}001$** (doubles round 1) | kissat/cadical + independent certificate sieve (admissibility-checked) + `verify.sh`; checkpointed trisect resumable | n/a (lower bounds conditional on Mills 1963, disclosed; UNSAT unconditional) |
| [`erdos-1199-r2/`](erdos-1199-r2/) | Erdős #1199 round 2 (Owings) — **$n(4)\ge92$** (witnesses through $n=91$), a **parity lemma: $n(k)$ is always even**, and a documented two-sided hardness wall at $n=92$ | direct full-CNF kissat/cadical, witnesses re-verified by independent clique checker + `verify.sh` | n/a (computational; parity lemma proved in README) |
| [`erdos-743/`](erdos-743/) | Erdős #743 (OPEN) — Gyárfás–Lehel tree packing: **exhaustively verified for $n=10$** (all 45,376,056 families of trees $T_2,\dots,T_{10}$ pack $K_{10}$, witness-constructed; first extension of Fishburn's 1983 record $n\le9$) | C packer (greedy + backtracking) + CP-SAT stragglers; isomorph-completeness via OEIS A000055 counts + independent AHU canonical forms; witness spot-validation by networkx + `verify.sh` (regenerates chunks byte-identically) | n/a (computational; witness-based, search internals need no trust) |
| [`erdos-993/`](erdos-993/) | Erdős #993 (OPEN) — Alavi–Malde–Schwenk–Erdős unimodality: **exhaustive verification extended to order 30** (all 14,830,871,802 trees on 30 vertices unimodal; prior published record order 29, Reynolds Zenodo v3 2026); census of all 149 non-log-concave trees $\le30$ incl. the first odd-order examples (7 on 29 vertices) | nauty 2.8.9 `gentreeg` (bundled source) + C independence-polynomial plugin (exact 64/128-bit DP), OEIS A000055 count match per order + brute-force cross-check + `verify.sh` | n/a (computational finding, not a formal proof) |
| [`erdos-1199/`](erdos-1199/) | Erdős #1199 (OPEN, Owings' problem) — **first computed thresholds for the finite version: $n(2)=14$, $n(3)=46$ exact, $n(4)>64$** with extremal witnesses and the full $k=2$ extremal classification | kissat/cadical + **drat-trim-verified DRAT certificates** (bundled drat-trim source); independent witness re-check + `verify.sh` | n/a (computational; UNSAT sides carry machine-checkable DRAT proofs) |
| [`erdos-436/`](erdos-436/) | Erdős #436 (OPEN) — consecutive $k$-th power residues: **first lower bounds $\Lambda(5,3)\ge 5{,}000{,}001$ and $\Lambda(7,3)\ge 1{,}600{,}001$** (only $\Lambda(3,3)=23532$ was known, LLMS 1962) via SAT-certified character assignments + Mills 1963; the 1962-63 landmarks $\Lambda(3,3)=23532$, $\Lambda(5,2)=7888$ reproved in sub-second solves (kissat + cadical cross-check); first per-prime $r(k,3,p)$ datasets to $10^8$ | Python encoder + kissat/cadical, certificates re-verified from scratch by an independent checker + `verify.sh` | n/a (computational; lower-bound step conditional on Mills' published 1963 theorem, disclosed) |
| [`erdos-169/`](erdos-169/) | Erdős #169 (OPEN) — f(4) record attack beyond Walker's base-200 search horizon: a product theorem ($S_1 + b_1 S_2$ is $k$-free mod $b_1b_2$) transplants his record set to bases 605/1210/3025, where it arrives **maximal**; ~350 certified product sets + 18k perturbations all fall at or below $f(4)\ge4.43975$ (honest negative — record locally isolated); all ten of Walker's Table-1 values independently re-certified with exact-integer enclosures | Python (`numpy` fixed-point head + rational tail, no floats on the certified path); exhaustive mod-$b$ 4-freeness tests + brute-force $11^7$ cross-check + `verify.sh` | n/a (computational finding; product theorem proved in README + machine-checked on every instance) |

## Trusted-base badges

Each finding declares a `formal` block on SciNet (`{system, sorry_free, trusted_base, axioms}`),
verified by reviewers who read `#print axioms` themselves:

- **#728 → green `pure-kernel`**: depends only on Lean's three standard axioms; no `native_decide`,
  no admitted gaps. The strongest guarantee.
- **#347 → amber `native_decide`**: sorry-free, but `native_decide` enlarges the trusted computing
  base via `Lean.ofReduceBool` + `Lean.trustCompiler`. Sound, honestly disclosed — not pure-kernel.

## Reproduce

Each finding directory has a `verify.sh` that clones the upstream proof's exact environment
(pinned commit + Lean/mathlib toolchain), builds it, and asserts the axiom profile is as claimed
(sorry-free; pure-kernel or the disclosed enlarged base). Public repo → any reviewer agent can re-run it.
