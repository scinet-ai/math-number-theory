# Erdős Problem #436 — consecutive k-th power residues: Λ(5,3) ≥ 5,000,001 and Λ(7,3) ≥ 1,600,001, with machine-verified certificates

**Problem** ([erdosproblems.com/436](https://www.erdosproblems.com/436), Erdős–Graham 1980; asked
by D. H. and Emma Lehmer 1962). For a prime p let r(k,m,p) be the least r ≥ 1 such that
r, r+1, …, r+m−1 are all k-th power residues mod p, and let Λ(k,m) = limsup over p of r(k,m,p).
Open: is Λ(k,3) finite for all odd k ≥ 5, and how do Λ(k,2), Λ(k,3) grow in k?

**Frontier before this work** (verified against erdosproblems.com/436, last edited 2025-10-25, and
OEIS [A000445](https://oeis.org/A000445), last edited 2025-10-17, on 2026-07-27):

| quantity | value | source |
|---|---|---|
| Λ(2,2) | 9 | Lehmer–Lehmer 1962 |
| Λ(3,2) | 77 | Dunton 1965 |
| Λ(4,2) | 1224 | Bierstedt–Mills 1963 |
| Λ(5,2) | 7888 | Lehmer–Lehmer–Mills 1963 |
| Λ(6,2) | 202124 | Lehmer–Lehmer–Mills 1963 |
| Λ(7,2) | 1649375 | Brillhart–Lehmer–Lehmer 1964 |
| Λ(3,3) | **23532** | Lehmer–Lehmer–Mills–Selfridge 1962 — the only m=3 value ever computed |
| Λ(k,3), odd k ≥ 5 | *nothing known* (trivially ≥ Λ(k,2)) | — |

Λ(k,2) is finite for all k (Hildebrand 1991). Λ(k,3) = ∞ for even k (Lehmer–Lehmer);
Λ(k,m) = ∞ for m ≥ 4 (Graham 1964). For odd k ≥ 5 the m=3 question is wide open.

**Frontier after this work**

* **Λ(5,3) ≥ 5,000,001** and **Λ(7,3) ≥ 1,600,001** — the first nontrivial lower bounds for any
  Λ(k,3) with odd k ≥ 5, each backed by an explicit machine-verified certificate
  (an assignment of quintic/septic character values to all primes up to ~5×10⁶ / ~4×10⁵
  admitting no triple of consecutive "residues"). The reduction from certificate to Λ bound
  is the classical theorem of Mills (1963) on characters with preassigned values, exactly the
  step used by Lehmer–Lehmer–Mills–Selfridge for the Λ(3,3) lower bound.
* First recorded per-prime datasets r(5,3,p) and r(7,3,p) for all primes p < 10⁸.
* The 1962-63 landmark computations Λ(3,3) = 23532 and Λ(5,2) = 7888 are reproved end-to-end
  by a modern SAT pipeline in under a second each (both directions: attainment certificate and
  impossibility), with two independent solvers agreeing on the impossibility direction.

Nothing here resolves finiteness of Λ(5,3); that remains open. The observed behaviour
(satisfiability remains "easy" at bound 5×10⁶, solver time growing roughly linearly) is
consistent both with a finite but enormous value and with Λ(5,3) = ∞.

---

## Method

### The character-assignment (Lehmer–Lehmer–Mills–Selfridge) reduction

For p ≡ 1 (mod k), the k-th power residue character is a completely multiplicative map
f : {1,…,p−1} → Z/k with "n is a residue" ⟺ f(n) = 0. Two directions:

* **Upper bounds are unconditional.** If *every* completely multiplicative f : N → Z/k has a
  run of m consecutive zeros starting at some r ≤ B, then r(k,m,p) ≤ B for every prime
  p > B+m−1 (primes p with gcd(k,p−1) = 1 have r = 1), so Λ(k,m) ≤ B.
* **Lower bounds via Mills' theorem.** For odd k (and k = 2), any assignment of character
  values at finitely many primes is realized by infinitely many primes p
  (W. H. Mills, *Characters with preassigned values*, Canad. J. Math. 15 (1963)). So a single
  f with no zero-run of length m starting in [1, B] proves Λ(k,m) ≥ B+1.

### SAT formulation (`src/encode_assignment_cnf.py`)

"Does a completely multiplicative f : {1,…,B+m−1} → Z/k with no m-run of zeros starting in
[1, B] exist?" becomes CNF: a one-hot block of k Booleans per integer n (value of f(n)),
channeling clauses v(q,i) ∧ v(n/q, j) → v(n, i+j mod k) at each composite (q = least prime
factor), one forbidden-window clause per r ≤ B, f(1) = 0, and the global-rescaling symmetry
broken by restricting f(2) ∈ {0,1}. SAT ⇒ Λ(k,m) ≥ B+1 (model decodes to a certificate);
UNSAT ⇒ Λ(k,m) ≤ B unconditionally. Λ(k,m) equals (largest satisfiable B) + 1.

Solved with kissat 4.0.4; impossibility verdicts cross-checked with cadical 3.0.1
(independent solver). Every satisfiable model is decoded to a plain-text certificate and
re-verified from scratch by `src/verify_certificate.py` (independent sieve, no shared code).

### Validation ladder — four published values reproduced exactly

| target | known value | SAT at value−1 | UNSAT at value | solver time |
|---|---|---|---|---|
| Λ(2,2) | 9 | ✓ (also by exhaustive tree search, 14 nodes) | ✓ | <0.1 s |
| Λ(3,2) | 77 | ✓ (also by tree search, 824,864 nodes) | ✓ | <0.1 s |
| Λ(5,2) | 7888 | ✓ cert verified | ✓ kissat 0.13 s + cadical | 0.03 s / 0.13 s |
| Λ(3,3) | 23532 | ✓ cert verified | ✓ kissat 0.59 s + cadical | 0.46 s / 0.59 s |

The 1962 SWAC computation that proved Λ(3,3) = 23532 is now a sub-second SAT call.
An explicit exhaustive tree search (`src/search_character_assignments.c`) independently
reproduces 9 and 77 but becomes infeasible around depth ~200 for (3,3) — the SAT solver's
conflict learning is what closes the gap.

### New results (k = 5 and k = 7, m = 3)

| instance | verdict | kissat time | consequence |
|---|---|---|---|
| k=5, B=25,000 | SAT, cert verified | 0.11 s | Λ(5,3) ≥ 25,001 |
| k=5, B=100,000 | SAT, cert verified | 0.52 s | Λ(5,3) ≥ 100,001 |
| k=5, B=400,000 | SAT, cert verified | 2.35 s | Λ(5,3) ≥ 400,001 |
| k=5, B=1,600,000 | SAT, cert verified | 10.29 s | Λ(5,3) ≥ 1,600,001 |
| **k=5, B=5,000,000** | **SAT, cert verified** | **37.94 s** | **Λ(5,3) ≥ 5,000,001** |
| k=7, B=100,000 | SAT, cert verified | 0.97 s | Λ(7,3) ≥ 100,001 |
| k=7, B=400,000 | SAT, cert verified | 4.11 s | Λ(7,3) ≥ 400,001 |
| **k=7, B=1,600,000** | **SAT, cert verified** | **17.36 s** | **Λ(7,3) ≥ 1,600,001** |

The flagship certificate (`results/sat_k5_m3_B5000000_cert.txt`, 348,513 primes) assigns a
value in Z/5 to every prime ≤ 5,000,002 such that the induced completely multiplicative
function has no three consecutive zeros anywhere in [1, 5,000,002]. Verification is a
few-second sieve any reviewer can rerun (or reimplement from the two-line definition).
No unsatisfiable bound is known for k = 5, m = 3; we found no sign of the SAT/UNSAT frontier.

### Per-prime scans (`src/scan_least_consecutive_residues.c`)

Exact 64/128-bit arithmetic; residue test n^((p−1)/d) ≡ 1 (mod p), d = gcd(k, p−1); each
prime scanned to its first m-run, banking the first 2-run as well; segmented sieve;
checkpoint lines every 10⁶. Conventions: p ∤ n required except that n ≡ 0 (mod p) counts as
a residue (0 = 0^k, the problem statement's literal reading) — this only matters for tiny p,
where the first run can wrap through n ≡ 0; such "wrap" values (r > p−m) are reported but
excluded from interior maxima. Primes with gcd(k, p−1) = 1 have r = 1 and are counted, not scanned.

| dataset | primes scanned | interior max r(k,3,p) | witness p | interior max r(k,2,p) | witness p |
|---|---|---|---|---|---|
| k=3, p < 10⁸ | 2,880,517 (≡1 mod 3) | 549 | 6,851,821 | **77** = Λ(3,2), attained | 13,817,029 |
| k=5, p < 10⁸ | 1,440,298 (≡1 mod 5) | 2,283 | 27,327,371 | 340 (≤ 7888 ✓) | 21,271,721 |
| k=7, p < 10⁸ | 960,023 (≡1 mod 7) | 6,954 | 7,464,227 | 682 (≤ 1,649,375 ✓) | 91,822,781 |

Calibration: the k=3 scan reaches only 549 of the true 23532 — per-prime scans drastically
understate the limsup (the extremal character patterns have density ~k^(−π(B)) among primes),
which is precisely why the certificate method, not the scan, is the frontier instrument.
The scan data are still the first recorded r(k,3,p) values for k = 5, 7, and the k=3/k=5
rows validate the scanner against three published constants (77 attained; 7888, 1649375 never
exceeded; 23532 never exceeded).

## Reproducing

```
clang -O3 -march=native -o src/scan_residues src/scan_least_consecutive_residues.c
clang -O3 -march=native -o src/search_assignments src/search_character_assignments.c
clang -O3 -march=native -o src/deepen_assignment src/deepen_assignment_local_search.c

# scans (logs in results/): scan_residues k m p_lo p_hi
./src/scan_residues 5 3 2 100000000

# SAT ladder: encode, solve, decode, verify
python3 src/encode_assignment_cnf.py encode 5 3 5000000 cnf/k5_m3_B5000000.cnf
kissat cnf/k5_m3_B5000000.cnf > results/sat_k5_m3_B5000000.out
python3 src/encode_assignment_cnf.py decode 5 3 5000000 results/sat_k5_m3_B5000000.out cert.txt
python3 src/verify_certificate.py cert.txt

# quick spot verification of everything (< 5 min):
./verify.sh
```

Large CNF files and solver model lines were deleted after decoding (regenerable
deterministically; the decoded certificates preserve the models). `results/` holds all raw
logs. `src/deepen_assignment_local_search.c` is a stochastic hill-climbing alternative kept
for completeness; the SAT route superseded it (its best k=3 triple depth was 5,887 vs the
SAT-side 23,531).

## Honest scope

* The Λ(5,3)/Λ(7,3) lower bounds are **conditional on Mills' 1963 realizability theorem**
  (unconditional as statements about multiplicative Z/k-valued functions; the certificates
  themselves are machine-checked exact combinatorics). This is the same logical step the
  1962 Λ(3,3) = 23532 lower bound rests on.
* Impossibility (UNSAT) verdicts rest on solver correctness; we mitigated with two
  independent solvers. They only affect the *reproduction* of known values, not the new bounds.
* Finiteness of Λ(5,3) is untouched. No upper bound for any Λ(k,3), odd k ≥ 5, is claimed.

## Credit

All prior values and the problem framing are due to the cited authors: D. H. Lehmer, Emma
Lehmer, W. H. Mills, J. L. Selfridge, M. Dunton, R. G. Bierstedt, J. Brillhart, J. H. Jordan,
J. R. Rabung, R. L. Graham, A. Hildebrand, P. Erdős; problem curation by T. F. Bloom
(erdosproblems.com). Key sources:

* Lehmer, Lehmer, *On runs of residues*, Proc. Amer. Math. Soc. 13 (1962).
* Lehmer, Lehmer, Mills, Selfridge, *Machine proof of a theorem on cubic residues*,
  Math. Comp. 16 (1962) — Λ(3,3) = 23532.
* Lehmer, Lehmer, Mills, *Pairs of consecutive power residues*, Canad. J. Math. 15 (1963) —
  Λ(5,2) = 7888, Λ(6,2) = 202124. <https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/pairs-of-consecutive-power-residues/25447775E29D7F9381FBBBDA3305B800>
* Mills, *Characters with preassigned values*, Canad. J. Math. 15 (1963) —
  the realizability theorem. <https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/characters-with-preassigned-values/E7687C126767FA79B3341C3474C8CA4C>
* Brillhart, Lehmer, Lehmer, *Bounds for pairs of consecutive seventh and higher power
  residues*, Math. Comp. 18 (1964). <https://doi.org/10.1090/S0025-5718-1964-0164923-X>
* Dunton, *Bounds for pairs of cubic residues*, Proc. Amer. Math. Soc. 16 (1965).
  <https://doi.org/10.1090/S0002-9939-1965-0172838-9>
* Hildebrand, *On consecutive k-th power residues II*, Michigan Math. J. 38 (1991) —
  Λ(k,2) < ∞ for all k. <https://doi.org/10.1307/mmj/1029004331>
* Bloom, *Erdős Problem #436*, <https://www.erdosproblems.com/436>; OEIS
  <https://oeis.org/A000445>.

Environment: macOS 26.5.1 (Apple Silicon, 14 cores), Apple clang 21.0.0, Python 3.12.13,
kissat 4.0.4, cadical 3.0.1 (both via Homebrew). All computations single-threaded; at most
4 concurrent processes; total compute well under one machine-hour.
