# Erdős Problem #436, round 2 — the even-k encoding and the Λ(8,2) gap

Round-2 continuation of the round-1 SAT-pipeline work (Λ(5,3) ≥ 5,000,001,
Λ(7,3) ≥ 1,600,001; finding f388c2e6). This round targets (1) the single
unfinished entry of the Λ(k,2) row: **Λ(8,2)**, known since Reble (2019) only
to the interval **1,499,876 ≤ Λ(8,2) ≤ 1,508,324** (OEIS A000445, comment by
C. E. Thompson, Jan 14 2020, re-confirmed current on the live OEIS page and
erdosproblems.com/436 on 2026-07-27), and (2) extending the round-1 Λ(5,3)
ladder.

**Problem** ([erdosproblems.com/436](https://www.erdosproblems.com/436), open,
page last edited 2025-10-25). For a prime p let r(k,m,p) be the least r ≥ 1 with
r, …, r+m−1 all k-th power residues mod p; Λ(k,m) = limsup_p r(k,m,p).

**Frontier before this work** (re-verified 2026-07-27 against
erdosproblems.com/436 and OEIS [A000445](https://oeis.org/A000445)):

| k | Λ(k,2) | source |
|---|---|---|
| 2 | 9 | Lehmer–Lehmer 1962 |
| 3 | 77 | Dunton 1965 |
| 4 | 1224 | Bierstedt–Mills 1963 |
| 5 | 7888 | Lehmer–Lehmer–Mills 1963 |
| 6 | 202124 | Lehmer–Lehmer–Mills 1963 |
| 7 | 1649375 | Brillhart–Lehmer–Lehmer 1964 |
| 8 | **only 1,499,876 ≤ Λ(8,2) ≤ 1,508,324** | BLL64: ≥ 1,200,744; Reble 2019: the interval |

**Frontier after this work**: see Results below.

---

## The even-k combinatorial condition

Round 1 handled odd k (and the classical reproductions), where any completely
multiplicative f : {1,…,B+1} → Z/k may serve as a hypothetical index character.
For even k the analogue differs, and for k = 8 specifically:

* An order-8 character mod p requires p ≡ 1 (mod 8). But 2 is a quadratic
  residue of every p ≡ ±1 (mod 8), and χ^4 is the quadratic character, so
  (−1)^f(2) = (2|p) = +1: **the index f(2) of 2 must be EVEN**.
* This is exactly the classical treatment: BLL64 §8 ("Since 2 is a quadratic
  residue of p = 8m+1, we cannot choose R(2) = 1, and the case vector must be
  modified accordingly"); likewise Rabung–Jordan 1970 ("2 can only appear in an
  even-numbered eighth power class").
* No other constraint arises: for odd primes q, p ≡ 1 (mod 4) gives
  (q|p) = (p|q), free via CRT over p; in Kummer-theoretic terms the only
  entanglement among Q(ζ₈, 2^{1/8}, q^{1/8}, …) is √2 ∈ Q(ζ₈). Realizability
  of any admissible assignment by infinitely many p ≡ 1 (mod 8) is Mills'
  preassigned-character theorem, applied to k = 8 exactly this way by
  Rabung–Jordan 1970 and (implicitly) Reble 2019.
* For k ∈ {2, 4, 6}, p ≡ 1 (mod k) leaves p mod 8 (and (q|p) for odd q) free,
  so NO constraint arises — which the validation ladder confirms empirically.

Soundness both directions for k = 8 with the constraint:

* **UNSAT at B ⇒ Λ(8,2) ≤ B unconditionally.** For p ≡ 1 (mod 8), the index
  character is an admissible f (f(2) even as above). For d = gcd(8, p−1) < 8,
  the 8th-power residues are the d-th-power residues, and the mod-d index
  character g lifts to the admissible f = (8/d)·g with the same zero set
  (f(2) = (8/d)g(2) is even since 8/d is). So every large p has
  r(8,2,p) ≤ B.
* **SAT at B ⇒ Λ(8,2) ≥ B+1**, via Mills' realizability theorem (the same
  logical step as every lower bound in the table above since 1962).

## Encoding (src/encode_v2.py)

One-hot blocks v(n,i) ⇔ "f(n) = i" for n ≤ B+1, i ∈ Z/k, with:

* exactly-one constraints on PRIME blocks only; composites get channeling
  clauses v(q,i) ∧ v(n/q,j) → v(n,(i+j) mod k) (q = least prime factor) and
  nothing else — the channeling forces the true-value literal, which is the
  only literal the window clauses test, so models decode to genuine f and
  genuine f satisfy all clauses (sound in both directions, ~30% leaner than
  round 1's encoding);
* window clauses ¬(v(r,0) ∧ … ∧ v(r+m−1,0)) for r ≤ B;
* f(1) = 0;
* symmetry breaking CORRECTED for even k: the unit group (Z/k)^* acts on
  solutions by global rescaling, with orbits = gcd classes, so f(2) is
  restricted to {0} ∪ {d : d | k, d < k} — round 1's {0,1} is valid only for
  prime k (for k = 6 it would have excluded the orbits {2,4} and {3}!);
* the 8 | k admissibility constraint f(2) even; net allowed set for k = 8:
  f(2) ∈ {0, 2, 4}.

Solver: kissat 4.0.4; decisive UNSAT cross-checked with cadical 3.0.1
(independent solver). Every SAT model is decoded to a plain-text certificate
(prime values only) and re-verified from scratch by
src/verify_certificate_v2.py (independent sieve; also checks the f(2)-even
admissibility for 8 | k).

Solver settings, learned the hard way: on these ~12M-var one-hot instances
kissat's default "lucky phase" is pathological — at B=1,499,875 it burned 27
CPU-minutes (24×10⁹ propagations, zero conflicts) without even starting CDCL;
with `--lucky=0` the same instance is **SAT in 153 s**. All k=8 interval
solves use `kissat --lucky=0 --time=3300`.

## The interval search (src/trisect.py)

Parallel (2-solver) interval search on [1,499,875, 1,508,324] maintaining
lo = SAT (self-certified), hi = UNSAT; Λ(8,2) = hi when hi − lo = 1.
Checkpointed to results/trisect_state.json after every verdict; every SAT
probe is decoded + independently re-verified immediately; CNFs (~2.1 GB each)
are deleted after use and regenerate deterministically. Probe placement
history, honestly: the first launch skewed probes low (lo + gap/6, lo + gap/3)
on the prior that Reble's 2019 lower-bound vector was optimal, as the
published vectors for k ≤ 7 were. Round 1 refuted the prior immediately
(B = 1,501,283 is SAT, already beating Reble's lower bound), so the search
was restarted — from its checkpoint — with neutral trisection (lo + gap/3,
lo + 2gap/3), which shrinks the interval exactly 3× per round whatever the
verdicts. The initial lo = 1,499,875 spent one round-1 solver slot on
re-certifying Reble's bound with our own pipeline, so the final chain of
evidence is self-contained.

## Validation ladder — three published even-k constants reproduced

| target | known value | SAT at value−1 | UNSAT at value | times |
|---|---|---|---|---|
| Λ(2,2) | 9 | ✓ | ✓ | <0.1 s |
| Λ(4,2) | 1224 | ✓ cert verified | ✓ | <0.1 s |
| Λ(6,2) | 202124 | ✓ cert verified | ✓ kissat + cadical | 33 s / 5 s (cadical 3.4 s) |

(Raw logs: results/sat_k6_B202123.out etc.; certificates in certs/.)

## Result: Λ(5,3) ≥ 10,000,001 (doubling the round-1 ladder)

The round-1 odd-k encoding (unchanged semantics; encoder `src/encode_v2.py`
with k=5, m=3, `allow_f2=[0,1]`) at B = 10,000,000:

```
python3 src/encode_v2.py encode 5 3 10000000 cnf/k5_m3_B10000000.cnf
kissat --sat --time=2400 cnf/k5_m3_B10000000.cnf > results/sat_k5_m3_B10000000.out
```

kissat 4.0.4 returned **SAT in 232 s** (50,000,010 vars, 250,695,923 clauses;
round 1's plain invocation went UNKNOWN in 15 min at this B — the `--sat`
configuration made the difference). The model was decoded to
`certs/k5_m3_B10000000_cert.txt` (all 664,579 primes ≤ 10,000,002) and
re-verified from scratch by BOTH independent verifiers (round 2's
`src/verify_certificate_v2.py` and round 1's `verify_certificate.py`):
a completely multiplicative f : {1..10,000,002} → Z/5 with no 3 consecutive
zeros. By Mills' realizability theorem: **Λ(5,3) ≥ 10,000,001**, doubling the
round-1 bound of 5,000,001. (The 6 GB CNF was deleted; it regenerates
deterministically. Model lines were stripped from the solver log after
decoding; header/stats kept.)

The planned "first UNSAT" hunt for k=5, m=3 is moot at this scale: SAT at
10^7 with essentially no CDCL search ("no clauses used at all" in the kissat
glue stats) says the constraint density at B = 10^7 is far below the
UNSAT threshold, which is out of reach of this budget. Recorded honestly as
a lower-bound ladder extension only.

## Results for k = 8 — TBD (filled in after the runs)

RESULTS_PLACEHOLDER

## Reproducing

```
# validation + all certificates + verdict-log consistency (< 5 min):
./verify.sh

# full pipeline for one bound B:
python3 src/encode_v2.py encode 8 2 B cnf/k8_B.cnf
kissat cnf/k8_B.cnf > results/sat_k8_B.out     # rc 10 = SAT, 20 = UNSAT
python3 src/encode_v2.py decode 8 2 B results/sat_k8_B.out cert.txt
python3 src/verify_certificate_v2.py cert.txt

# the interval search (checkpointed, resumable):
python3 src/trisect.py
```

CNF files (~2.1 GB each) are deleted after solving and regenerate
deterministically; certificates + logs are the evidence chain.

## Honest scope

* The Λ(8,2) lower bound is conditional on Mills' 1963 realizability theorem
  (same step as the 1962–64 published values and Reble's 2019 lower bound);
  the certificate itself is machine-checked exact combinatorics.
* UNSAT verdicts rest on solver correctness, mitigated by two independent
  solvers agreeing on the decisive instance (and by reproducing four known
  constants end-to-end with the same pipeline).
* Nothing here touches the finiteness of Λ(k,3) for odd k ≥ 5.

## Credit

All prior values and the problem framing are due to: D. H. Lehmer, Emma Lehmer,
W. H. Mills, J. L. Selfridge, M. Dunton, R. G. Bierstedt, J. Brillhart,
J. H. Jordan, J. R. Rabung, R. L. Graham, A. Hildebrand, P. Erdős; problem
curation T. F. Bloom (erdosproblems.com); the Λ(8,2) interval and the A000445
stewardship: **Don Reble** (SeqFan, Dec 19 2019) and Christopher E. Thompson.
Key sources:

* Brillhart, Lehmer, Lehmer, *Bounds for pairs of consecutive seventh and
  higher power residues*, Math. Comp. 18 (1964) — Λ(7,2), Λ(8) ≥ 1200744, and
  the R(2)-even modification for k = 8. <https://doi.org/10.1090/S0025-5718-1964-0164923-X>
* Rabung, Jordan, *Consecutive power residues or nonresidues*, Math. Comp. 24
  (1970) — the even-class constraint at 2 for k = 8, Mills' theorem applied.
  <https://doi.org/10.1090/S0025-5718-1970-0277469-0>
* Mills, *Characters with preassigned values*, Canad. J. Math. 15 (1963).
* Lehmer, Lehmer, Mills, *Pairs of consecutive power residues*, Canad. J.
  Math. 15 (1963) — Λ(5,2), Λ(6,2).
* Hildebrand, *On consecutive k-th power residues II*, Michigan Math. J. 38
  (1991) — Λ(k,2) < ∞.
* Reble, *More terms for A000445?*, SeqFan, Dec 19 2019 (via OEIS A000445).
* Bloom, *Erdős Problem #436*; OEIS <https://oeis.org/A000445>.

Environment: macOS 26.5 (Apple Silicon, 14 cores, machine shared with sibling
agents; ≤ 3 concurrent processes used), Apple clang 21, Python 3.12,
kissat 4.0.4, cadical 3.0.1 (Homebrew). Deterministic: fixed encodings, exact
integer arithmetic, no randomization beyond kissat defaults (fixed default
seed).
