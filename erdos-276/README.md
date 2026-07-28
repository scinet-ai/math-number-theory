# Erdős #276 — certified bounded-obstruction exclusion for the Ismailescu–Son sequence

**Problem** (Erdős–Graham [ErGr80, p.27]; erdosproblems.com/276, open): is there a Lucas
sequence a_{n+2} = a_{n+1} + a_n with every term composite, yet such that no integer
m > 1 shares a common factor with every term (i.e., compositeness NOT explained by a
finite covering set of primes)?

**Candidate** (Ismailescu–Son 2014, J. Integer Seq. 17, Article 14.8.2 [IsSo14]): p = 1,
q = the 129-digit CRT solution of their Table 3; x0 = 1 + q², x1 = 2q + q² (257 digits
each). Even-indexed terms are covered by the 30 primes of their Table 2; odd-indexed
terms are composite by the identity x_{2n+1} = (F_n + qF_{n+1})(L_n + qL_{n+1}).
The open part is property (ii): no single integer m > 1 hits *every* term. IsSo14
supported this with an *unpublished, uncertified* computation ("803 values of
0 ≤ n ≤ 200000 with no prime factor ≤ 2·10⁶ or among the Table-2 primes, pairwise
coprime") — no code, no reproduction until now (van Doorn's Nov 2025 comment on
erdosproblems.com/276 confirms the state of the art).

## What this workspace certifies (frontier before → after)

Before: IsSo14's stated-but-uncertified 2·10⁶ verification; nothing since (checked
erdosproblems.com/276 + forum, OEIS, literature to 2026-07-27).

After (all with published code, deterministic, independently cross-checked paths):

1. **Transcription certificate** (Stage A): the 129-digit q equals the smallest
   positive CRT solution of Table 3 exactly; all 30 moduli prime; gcd(x0,x1)=1;
   the even-index covering is *proved* (covering of all even residues mod 5040 +
   p_i | F_{m_i} + eq. (10) congruences all verified); the odd-index factorization
   identity verified exactly for n = 0..60.
2. **Bilateral reproduction of IsSo14's computation** (Stage B): sieving x_n mod p
   for ALL primes p ≤ 2·10⁶ plus the 5 Table-2 primes above that bound, over
   n ∈ [0, 10⁶]: exactly **803 escape indices in [0, 200000]** — matching IsSo14's
   unpublished count — and 3944 in [0, 10⁶] (density ≈ 0.394%, stable per 10⁵ block;
   all escape indices are odd, as forced by the proven even-index covering).
3. **Independent re-verification** (Stage C3): every one of the 803 escape terms,
   computed as an exact integer and trial-divided (GMP) by every prime ≤ 2·10⁶ and
   the 5 large Table-2 primes — a code path disjoint from the sieve (bignum division
   vs uint64 recurrence). Plus pairwise coprimality of all 803 terms (322,003 GCDs)
   (Stage C4).
4. **New, far stronger escape certificates** (Stage C1/C2): smallest prime factors of
   the ten smallest escape indices determined (seven exact values, three bounded
   below by 10¹¹); three of them (n = 719, 1799, 1815)
   have **no prime factor ≤ 10⁹**, and the certified bound for n = 719, 1799, 1815,
   1827, 1887 is pushed to **10¹¹** (trial division by all 4,118,054,813 primes
   ≤ 10¹¹, prime counts cross-checked against π(10⁹) = 50,847,534 and
   π(10¹¹) = 4,118,054,813). x_719 = A·B with both algebraic factors *composite*
   (203 and 204 digits), so x_719 has at least four prime factors, all > 10¹¹ — an
   escape not implied by IsSo14's semiprime observations at n = 1827, 1887 (whose
   factors we confirm to be BPSW/MR probable primes of 319/320/326/326 digits, as
   the paper states).

**Certified theorem (bounded-obstruction exclusion).** For the Ismailescu–Son
sequence: any integer m > 1 having a common factor with every term must have a prime
factor exceeding 10¹¹; equivalently, no covering system whose primes are all ≤ 10¹¹
explains its compositeness. Moreover any finite prime set covering the sequence must
contain at least 803 distinct primes larger than 2·10⁶ (one per pairwise-coprime
escape term in [0, 200000]), of which at least three exceed 10¹¹ (for the pairwise
coprime x_719, x_1799, x_1815). This is a 50,000-fold extension of the bound stated
(without code) in IsSo14, and exactly the kind of partial the problem's success
criteria bless ("certified computation ... excluding every covering-system
obstruction with moduli (or prime set) up to an explicit stated bound").

What this does NOT do: it does not prove property (ii) (that would need every finite
prime set, unbounded), and does not touch the FULLY RESOLVES bar. The problem page
itself notes it "cannot be resolved with a finite computation".

## Reproduction

```
python3 src/stage_a_transcription_check.py          # ~30 s, exit 0 iff all pass
python3 src/gen_residues.py                          # sieve input (primes ≤ 2e6 + 5)
clang -O3 -o src/sieve src/sieve.c
src/sieve data/sieve_input.bin results/bitmap_i.bin 1000000 lo hi   # 3-way split
python3 src/merge_and_report.py                      # 803 / 3944, profile
python3 src/gen_xvals.py --survivors ; python3 src/gen_xvals.py 1827 1887
clang -O3 -I/opt/homebrew/include -L/opt/homebrew/lib -o src/certify src/certify.c -lprimesieve -lgmp
bash src/run_certify_1e9.sh                          # 10 smallest escapes vs primes ≤ 1e9
bash src/run_certify_1e11.sh                         # 5 key escapes vs primes ≤ 1e11
bash src/run_reverify_803.sh                         # independent 803 re-verification
python3 src/gen_algebraic_factors.py 1827 1887 719 1799 1815
clang -O3 -I/opt/homebrew/include -L/opt/homebrew/lib -o src/pp src/pp.c -lgmp
src/pp results/factors/{A,B}_{1827,1887,719,1799,1815}.txt
clang -O3 -I/opt/homebrew/include -L/opt/homebrew/lib -o src/pairgcd src/pairgcd.c -lgmp
src/pairgcd k 3 <803 xval files>                     # k = 0,1,2
./verify.sh                                          # ≤5 min spot-verification
```

Environment: macOS arm64 (Darwin 25.5.0), Apple clang, Homebrew gmp + primesieve,
Python 3 (stdlib only). All arithmetic exact (Python bigints / GMP / uint64 < 2⁶³
with explicit reduction). Deterministic; the only randomness is the fixed-seed
(seed 276) spot-check A8 and GMP's internal MR bases in the *reported-only*
probable-prime classifications.

## Credit

The sequence and the entire construction are due to Dan Ismailescu and Jaesung Son,
"A New Kind of Fibonacci-Like Sequence of Composite Numbers", J. Integer Seq. 17
(2014), Article 14.8.2 — including the original (uncertified) 803-count. Problem
statement: Erdős–Graham 1980; curated by T. F. Bloom (erdosproblems.com/276), with
key context from Wouter van Doorn's forum comment (24 Nov 2025). Prior covering-based
constructions: Graham 1964, Knuth 1990, Wilf 1990, Nicol 1999, Vsemirnov 2004.
