# Certified record table for Erdős #51: $f(a)/a$ over all totient values $a\le 3.06\times10^{10}$

Deliverable 3 of this workspace: an **exact, certified** table of the minimal-preimage
ratio $f(a)/a$ ($f(a)=n_a=\min\{n:\varphi(n)=a\}$) for *every* totient value
$a\le A_{\max}=30{,}641{,}761{,}281$ (see below), from a segmented factoring sieve over
$n\in[1,N]$, $N=1.94\times10^{11}$, with (i) a proof that the table is complete and
minimal (Lemma C), (ii) an independent reimplementation cross-check, and (iii)
per-record re-certification by exhaustive inverse-totient enumeration.

## Why a sieve over $[1,N]$ certifies the table

The subtle point is **completeness**: a totient value $a\le A_{\max}$ all of whose
preimages exceed $N$ would be silently *missing* from the table (and would in fact be a
spectacular record). Lemma C rules this out. Minimality is automatic: the first $n$ (in
increasing order) with $\varphi(n)=a$ *is* $f(a)$.

**Lemma C (certification).** Let $R(m)=\prod_{j\le m}\frac{p_j}{p_j-1}$ over the first
$m$ primes, and note $R(10)=\frac{29\#}{\varphi(29\#)}=\frac{6469693230}{1021870080}=6.33122\ldots$
Then for every $n>N$ (any $N\le 31\#=200560490130$):
$$\varphi(n)\;>\;\min\Bigl(\frac{N}{R(10)},\ \varphi(31\#)\Bigr),\qquad
\varphi(31\#)=30656102400 .$$

*Proof.* Two cases on $m=\omega(n)$.
If $m\le10$: by initial-segment domination (Lemma 2 of `proof_obstruction_lemmas.md`:
the $j$-th smallest prime factor of $n$ is $\ge p_j$ and $x/(x-1)$ decreases),
$n/\varphi(n)\le R(10)$, so $\varphi(n)\ge n/R(10)>N/R(10)$.
If $m\ge11$: $\varphi(n)=\prod p^{e-1}(p-1)\ge\prod_{p\mid n}(p-1)\ge\prod_{j\le11}(p_j-1)
=\varphi(31\#)$, again by termwise domination ($q_j\ge p_j\Rightarrow q_j-1\ge p_j-1$).
$\square$

**Choice of $N$.** With $N=1.94\times10^{11}$ (just below the crossing point
$\varphi(31\#)\cdot R(10)\approx1.9409\times10^{11}$), Lemma C gives: every $n>N$ has
$\varphi(n)>\lfloor N/R(10)\rfloor = 30{,}641{,}761{,}281 =: A_{\max}$
(and $\varphi(31\#)=30656102400>A_{\max}$). Hence every totient value
$a\le A_{\max}$ has **all** its preimages $\le N$: the sieve sees the complete fiber,
its first occurrence is exactly $f(a)$, and the census of all $a\le A_{\max}$ with
$f(a)\ge2a$ is complete. (Everything is elementary and checked by `verify.sh` step 5;
no analytic estimates enter the certification.)

## Implementation

`sieve_fmin.c` (this directory): segmented totient sieve, segments of $2^{24}$,
one `uint64` residual + one `uint64` phi accumulator per $n$; $p=2$ extracted by
count-trailing-zeros; odd primes $p\le\sqrt{n}$ extracted with Lemire-style
multiplicative-inverse divisibility tests (no divisions in the hot loop); the largest
prime factor $>\sqrt{n}$ is whatever residual $>1$ survives. First occurrences are
detected with a bitset over $a\le A_{\max}$ (3.8 GB), scanning $n$ in increasing order.
Events emitted: `R a n ratio` (running record of $f(a)/a$), `E a n` ($f(a)\ge 2a$,
exact integer test), `H a n` ($1.9\le f(a)/a<2$, integer test $10n\ge19a$).
Runtime: about 100 minutes wall on one (contended) core of an Apple-silicon
workstation, ~55 min CPU; memory ~4.2 GB.

Reproduce: `cc -O2 -o sieve_fmin sieve_fmin.c -lm && ./sieve_fmin 194000000000 > data/run_full.txt 2> data/run_full.log`

## Results (full run, $N=1.94\times10^{11}$, $A_{\max}=30{,}641{,}761{,}281$)

* Totient values $a\le A_{\max}$: **3,903,102,222** (exact count; for scale,
  $A_{\max}/\ln A_{\max}\approx1.27\times10^9$ — cf. Ford's $V(x)$ asymptotics).
* Values with $f(a)/a\ge2$: **31,043** (complete census, `E` lines of `data/run_full.txt`);
  values with $1.9\le f(a)/a<2$: **3,408,149**.
* **Global record**: $f(a)/a = \mathbf{2.043447}$ at
  $a=387383296=2^{16}\cdot23\cdot257$, with $f(a)=791597265=3\cdot5\cdot17\cdot47\cdot257^2$
  (note the squared Fermat prime; the previous record $a=2037248=2^9\cdot23\cdot173$ has
  $f(a)=3\cdot5\cdot17\cdot47\cdot347$) — full verified factorizations in
  `data/records_analysis.txt`. No totient value $a\le3.06\times10^{10}$ has
  $f(a)/a\ge2.05$.
* Running-record sequence (positions): $2,\ 8,\ 128,\ 5888,\ 2037248,\ 387383296$ —
  **exactly** OEIS A393265 (J. McCranie, Feb 2026), independently reproduced; our run
  *certifies* (with Lemma C) the completeness of this list up to $3.0642\times10^{10}$,
  strengthening the OEIS entry's uncertified "no more terms < 1.2e11" within our range.
  Record ratios: $1.5,\ 1.875,\ 1.9922,\ 2.0355,\ 2.0414,\ 2.0434$.
* Consistency with theory: every $a=2^k\le A_{\max}$ ($k\le34$) has
  $f(2^k)=\prod_{i\in B(k)}F_i$ for $k\le31$ and $f(2^k)=2^{k+1}$ for $k=32,33,34$
  (Theorem 1 dichotomy — the sieve confirms the theorem's instances, and conversely).
* The growth of the record is glacial, as the obstruction pack predicts
  (`proof_obstruction_lemmas.md`): a ratio of just $2.5$ would force
  $v_2(a)\ge$ (elementary bound) $0.28$ — vacuous — but the *exact* Lemma-2 chain
  forces every preimage of a ratio-$K$ value to carry the full Fermat-prime kit;
  empirically all census entries with ratio $>2$ have odd $f(a)$ divisible by
  $3\cdot5$ or $3\cdot5\cdot17$ with Sophie-Germain-type carriers.

## Verification

`./verify.sh` re-checks from scratch (few minutes): (1) build; (2) `invphi.py`
self-test against brute-forced complete fibers; (3) Theorem-1 instance check
(`check_theorems.py`, exhaustive fibers of $2^k$, $k\le40$); (4) independent numpy
reimplementation vs the C table at $N=10^7$ — tables identical; (5) Lemma C constants;
(6) `verify_records.py`: exact inverse-totient re-certification of all running
records, all census entries with $a\le10^8$, the 50 largest, and a deterministic
random sample of 200 (each check enumerates the complete preimage fiber of $a$
independently of the sieve and confirms the minimum).

Partial-run banking: the sieve emits progress checkpoints; if interrupted at
completed prefix $[1,M]$, all claims hold verbatim with $A_{\max}$ replaced by
$\lfloor M/R(10)\rfloor$ (Lemma C only needs the prefix to be complete).
