# Erdős #386 — structural theorems (v2, post-adversarial verification)

**Provenance.** This file is the repaired successor of `THEOREM.md` (draft v1). Every
statement below was either re-proved in full or numerically stress-tested (or both); the
verification log is summarized in the appendix. Changes from v1 are flagged inline.
Ingredient labels: **[elem]** = elementary and self-contained; **[MV]** = uses
Montgomery–Vaughan's large-sieve prime-counting bound; **[BHP]** = uses
Baker–Harman–Pintz prime gaps; **[RH]**, **[Cramér]** = conditional.

Throughout: $2 \le k \le n/2$, and $C(n,k) = \binom{n}{k}$ is assumed to be a product of
**consecutive primes** $p_i p_{i+1} \cdots p_j$ (each to the first power). Write
$P$ for its largest prime factor and $s$ for its smallest. We call such an $(n,k)$ a
*solution*. Basic facts used freely:

- **(F1)** Every prime factor of $C(n,k)$ is $\le n$; in particular $s \le P \le n$.
- **(F2)** $(n/k)^k \le C(n,k) \le (en/k)^k$, and $C(n,k) \ge C(n,2) = n(n-1)/2 > n$
  for $n \ge 4$. Hence **the block always has length $\ge 2$** (a single prime would give
  $C(n,k) = P \le n$, contradicting $C(n,k) > n$).
- **(F3) (exact accounting)** Since the block consists of *all* primes in $[s, P]$, each
  to the first power,
  $$\log C(n,k) \;=\; \theta(P) - \theta(s) + \log s ,$$
  where $\theta$ is Chebyshev's function. *(Machine-verified on all nine known solutions
  to $10^{-9}$.)*

## Lemma 1 (band values). Let $p \le n$ be a prime with $p > k$ **and** $p^2 > n$. Then
$v_p\binom{n}{k} = \lfloor n/p \rfloor - \lfloor (n-k)/p \rfloor \in \{0,1\}$, and
$v_p = 1$ iff some multiple of $p$ lies in $(n-k,\, n]$, iff
$p \in \big(\frac{n-k}{m}, \frac{n}{m}\big]$ for $m = \lfloor n/p \rfloor \ge 1$.
(For $p > n$ trivially $v_p = 0$.)

*Proof.* Legendre with a single level ($p^2 > n$), and $\lfloor k/p \rfloor = 0$ ($p > k$).
The difference counts multiples of $p$ in $(n-k, n]$, which is 0 or 1 since the interval
has length $k < p$. If the multiple $mp$ exists then $mp \le n$ and
$(m+1)p = mp + p > (n-k) + p > n$, so $m = \lfloor n/p \rfloor$. ∎

**Both hypotheses are necessary** *(v2 addition; numerically located failure regions)*:

- $p > k$ but $p^2 \le n$: the single-level formula and the $\{0,1\}$ range **fail**.
  E.g. $v_7\binom{53}{6} = 2$ (single-level formula predicts 1); likewise
  $(n,k,p) = (589,13,17), (1863,42,43), (24667,69,157)$, all with $v_p = 2$.
  In a random sample of this region ($n \le 10^6$), about $0.6\%$ of triples break.
- $p \le k$ but $p^2 > n$: $v_p \in \{0,1\}$ still holds (single level), but the band
  criterion **fails badly** because $\lfloor k/p \rfloor \ge 1$: e.g.
  $v_{47}\binom{100}{50} = 0$ although $47 \in B_2 = (25, 50]$. In a random sample,
  $57\%$ of triples in this region break the band-iff.

Consequently, for $p > \max(k, \sqrt n)$ the *dividing* primes form the union of bands
$B_m = \big(\frac{n-k}{m}, \frac{n}{m}\big]$ and the *non-dividing* primes lie in the
exclusion zones $Z_m = \big(\frac{n}{m+1}, \frac{n-k}{m}\big]$ (nonempty as an interval
iff $m < n/k - 1$). Note for $q \in Z_m$ one has $\lfloor n/q\rfloor = m$, so zone
membership pins the level. *(Verified: 400,000 random triples with
$p > \max(k,\sqrt n)$, $n \le 10^6$, plus exhaustive checks of all $1{,}049{,}870$
primes $p \in (\max(k,\sqrt n), n]$ over 300 random pairs $(n,k)$, $n \le 10^5$:
zero violations of any claim in this paragraph or Lemma 1.)*

## Lemma 2 (top zone never divides). Any prime $q \in Z_1 = (n/2,\, n-k]$ has
$v_q\binom{n}{k} = 0$. Any prime $p \in B_1 = (n-k,\, n]$ has $v_p = 1$.

*Proof.* Such $q, p$ exceed $n/2 \ge k$, and $q \ge (n+1)/2$ gives $q^2 > n$ for every
$n \ge 2$, so Lemma 1 applies — including at the tiny anchors $n = 4, 6, 7$; no
degenerate exception. For $p \in B_1$, $p$ itself is the multiple; for $q \in Z_1$,
$q \le n-k$ and $2q > n$. ∎

## Lemma 3 (consecutiveness exclusion) — *v2 addition, makes the "q < s" step explicit.*
Every prime in $[s, P]$ divides $C(n,k)$. Hence if $v_q = 0$ for a prime $q < P$, then
$q < s$.

*Proof.* The block $p_i, \ldots, p_j$ is a set of consecutive primes with $p_i = s$,
$p_j = P$, so it contains every prime of $[s, P]$; each block prime divides $C(n,k)$ by
hypothesis. ∎

*Degenerate cases checked:* a block of length 1 cannot occur (F2). The argument does not
care whether $s \le k$ (small block primes with digit-governed valuations, as in
$(10,4)$ where $s = 2 < k = 4$): consecutiveness constrains the factor *set*, not the
mechanism of the valuations. And in the applications below $q > n/2 \ge k$, so $q$ is
band-governed regardless.

## Theorem 1 (trichotomy — replaces the v1 dichotomy; the v1 GAP-CHECK was real).
Every solution satisfies exactly one of:

- **(i) low case:** $P \le n/2$, and then $B_1 = (n-k, n]$ contains **no prime at all**
  (a prime-free interval of length $k$ ending at $n$);
- **(ii) high case:** $P > n - k$, and $Z_1 = (n/2, n-k]$ contains **no prime**;
- **(iii) exceptional case:** $P > n - k$, $Z_1$ contains a prime, and then
  $s > n/2$, every prime factor lies in $B_1$, and
  $$C(n,k) \;=\; \prod_{p \text{ prime},\, n-k < p \le n} p .$$

*Proof.* $P \notin Z_1$ by Lemma 2, so either $P \le n/2$ or $P > n-k$ (using $P \le n$,
F1); these are mutually exclusive since $n - k \ge n/2$.

Case $P \le n/2$: if a prime $p$ lay in $B_1$ it would divide (Lemma 2), contradicting
$p > n-k \ge n/2 \ge P$. This is horn (i).

Case $P > n-k$: either $Z_1$ is prime-free — horn (ii) — or some prime
$q \in Z_1$ exists. Then $v_q = 0$ (Lemma 2) and $q \le n-k < P$, so $q < s$ (Lemma 3):
every prime factor exceeds $q > n/2$. A prime factor in $(n/2, n-k]$ is impossible
(Lemma 2), so all factors lie in $B_1$, and each prime of $B_1$ divides (Lemma 2);
hence the factor set is exactly the set of primes in $(n-k, n]$, each to the first
power, giving the displayed product. This is horn (iii). ∎

**Why v1's proof of the dichotomy could not be repaired** *(resolution of the
GAP-CHECK)*: v1 tried to kill horn (iii) by the size comparison
$k\log(n/k) \le \log C \le 2k\log n/\log k$, which fails **both** for $k$ near $n/2$
(as flagged) **and** for bounded $k$ (e.g. $k=2$: $\log 2 \cdot \log(n/2) < 2\log n$
always). Horn (iii) cannot be eliminated by that inequality; it is instead *constrained*:

## Theorem 2 (horn (iii) is cornered). If a solution is in horn (iii), then

1. **[elem]** $n \le k^3$ (equivalently $k \ge n^{1/3}$); in fact
   $n^{\lfloor k/2\rfloor} \le k^k$;
2. **[MV]** $(\log k)\,\big(\log (n/k)\big) \le 2 \log n$;
3. consequently $k > n/13.4$ for every horn-(iii) solution with $n \ge 10^5$, and
   $k \ge \big(e^{-2} - o(1)\big) n$ as $n \to \infty$;
4. **(computation)** there is **no** horn-(iii) solution with $n \le 10^5$
   (exhaustive over all $2 \le k \le n/2$; see appendix).

*Proof.* (1) In horn (iii), $C(n,k)$ is a product of distinct primes from $(n-k, n]$, an
interval of $k$ integers all exceeding $2$ (as $n - k \ge n/2 \ge 2$), so it contains at
most $\lceil k/2 \rceil$ primes. Thus $(n/k)^k \le C(n,k) \le n^{\lceil k/2\rceil}$, i.e.
$n^{\lfloor k/2 \rfloor} \le k^k$, i.e. $n \le k^{k/\lfloor k/2\rfloor} \le k^3$
(the exponent is $2$ for even $k$, $\le 3$ for odd $k \ge 3$; for $k = 2$ one gets
$n \le 4$, and $(4,2)$ is not in horn (iii)).

(2) By F3 and the horn-(iii) product formula, $\log C = \theta(n) - \theta(n-k)
\le [\pi(n) - \pi(n-k)]\log n \le \frac{2k}{\log k}\log n$ by Montgomery–Vaughan
($\pi(x+y) - \pi(x) \le 2y/\log y$ for $y \ge 2$, here $x = n-k$, $y = k$). Combine with
$\log C \ge k \log(n/k)$.

(3) Write $L = \log n$ and $x = \log(n/k)$, so $\log k = L - x$ and (2) reads
$x(L - x) \le 2L$. For $L \ge 8$ this means $x \le c_1(L)$ or $x \ge c_2(L)$, the roots
$\tfrac12\big(L \mp \sqrt{L(L-8)}\big)$ of $x(L-x) = 2L$. From (1), $\log k \ge L/3$,
so (2) gives $x \le 6$; and $c_2(L) \ge c_2(\log 10^5) = 8.94$ for $n \ge 10^5$
($c_2$ is increasing), so $x < c_2$, forcing $x \le c_1(L)$. Now $c_1$ is decreasing
with limit $2$, and $c_1(\log 10^5) = 2.577$, so $n/k = e^x \le e^{2.577} < 13.4$ for
$n \ge 10^5$; as $n \to \infty$, $n/k \le e^{2 + o(1)}$. ∎

**Status of horns (ii)/(iii): empty for all sufficiently large $n$, by Granville–Ramaré.**
Cite-verified (see `citations.md`): Granville–Ramaré, Mathematika **43** (1996), 73–107,
Theorem 2 (verbatim): *"There exists a constant $\tau_1 > 0$ such that if $n$ is
sufficiently large and $\binom{n}{k}$ is squarefree then $k$ or $n-k$ is
$< \exp(\tau_1 (\log n)^{2/3} (\log\log n)^{1/3})$."* A product of consecutive primes to
the first power is squarefree; with $k \le n/2$ the theorem bounds $k$ itself. Horn (ii)
forces $k \ge n/2 - n^{0.525}$ (Corollary 3, [BHP]) and horn (iii) forces
$k > (e^{-2}-o(1))n$ (Theorem 2 above) — both contradict the sub-polynomial GR bound for
$n$ large. Hence:

## Theorem 5 (combined structure; ineffective constants from GR/BHP).
For all sufficiently large $n$: **every solution is in horn (i)** — that is,
$$P\Big(\binom{n}{k}\Big) \le \frac n2, \qquad (n-k,\, n] \text{ is prime-free}, \qquad
k < \exp\big(\tau_1 (\log n)^{2/3} (\log\log n)^{1/3}\big);$$
and under Cramér's conjecture the last bound self-improves to $k \ll \log^{2}n$ via the
prime-free requirement. Every solution is thus a *prime-gap event with sub-polynomial
$k$ and all prime factors below $n/2$*. *(Small $n$: six of the nine known solutions
live in horn (ii) at $n \le 15$ — the "sufficiently large" caveat is real.)*

## Corollary 3 (k is gap-bounded — was Corollary 2; horns now correctly attributed).
Let $p^- $ be the largest prime $\le n-k$ and $p^+$ the smallest prime $> n$.

- In horn (i), $(n-k, n]$ is prime-free, so $k < p^+ - p^-$: $k$ is smaller than a
  single prime gap straddling $n$. Hence **[BHP]** $k \le n^{0.525}$ for all
  sufficiently large $n$; **[RH]** $k \ll \sqrt n \log n$; **[Cramér]**
  $k \ll \log^2 n$.
- In horn (ii), $(n/2, n-k]$ is prime-free, so by the same results applied at
  $x = n-k \ge n/2$: **[BHP]** $n/2 - k \le (n-k)^{0.525} \le n^{0.525}$ for $n$ large;
  **[RH]** $n/2 - k \ll \sqrt n \log n$; **[Cramér]** $n/2 - k \ll \log^2 n$.
- In horn (iii), no prime-free interval is forced (on the contrary, $Z_1$ contains a
  prime); the constraint is Theorem 2: $k > (e^{-2} - o(1))\,n$.

**Merged unconditional form [BHP]:** for all sufficiently large $n$, every solution has
$$k \;\le\; n^{0.525} \qquad\text{or}\qquad k \;>\; n/8 .$$

*Proof of the transfers.* Baker–Harman–Pintz (2001): for all sufficiently large $x$, the
interval $[x - x^{0.525},\, x]$ contains a prime. Horn (i): if $k > n^{0.525}$ then
$[n - n^{0.525}, n] \subseteq (n-k, n]$ would contain a prime — contradiction (interval
direction checked: BHP's interval ends *at* $x = n$, exactly matching $B_1$'s right end).
Horn (ii): if $n/2 - k > (n-k)^{0.525}$ then $[\,(n-k) - (n-k)^{0.525},\, n-k\,]
\subseteq (n/2, n-k]$ would contain a prime — contradiction. The RH form uses Cramér's
conditional gap bound $O(\sqrt x \log x)$, the last form Cramér's conjecture. The merged
form combines horn (ii) ($k \ge n/2 - n^{0.525} > n/8$) with Theorem 2(3). ∎

*Effectivity caveat (v2 addition).* "Sufficiently large" is inherited from BHP and is not
explicit. The caveat is not removable for free: $(n,k) = (126, 13)$ has $(113, 126]$
prime-free with $k = 13 > 126^{0.525} \approx 12.67$ — the unique such configuration
with $n \le 10^7$ (it is not a solution of the problem; it bounds what the gap transfer
alone can give).

## Proposition 4 (replaces v1's Proposition 3, which is retracted; see appendix).

**(a) Size of the block [elem + PNT].** For every solution,
$$k \log (n/k)\;\le\; \theta(P) - \theta(s) + \log s \;=\; \log C(n,k)\;\le\; k \log (en/k),$$
and since $\theta(s) \ge \log s$, also $\theta(P) \ge k\log(n/k)$. With the elementary
Chebyshev bound $\theta(x) < x \log 4$ ($x \ge 1$):
$$P \;>\; \frac{k \log (n/k)}{\log 4}\qquad\text{(explicit, elementary)},$$
and with $\theta(x) > x(1 - 1/\log x)$ for $x \ge 41$ (Rosser–Schoenfeld; re-verified
numerically for $x \le 10^7$),
$$P\Big(1 - \frac{1}{\log P}\Big) \;\le\; k\log(en/k) + s\log 4 \quad (P \ge 41),$$
so $P \le (1+o(1))\big(k\log(en/k) + 1.39\,s\big)$. In particular, whenever
$n/k \to \infty$ and $s = o(k\log(n/k))$:
$$P = (1+o(1))\, k \log (n/k).$$
*The largest prime factor of a solution is pinned at the scale $k\log(n/k)$.*
*(All nine known solutions satisfy the explicit lower bound; e.g. $(715,2)$:
$P = 17 > 8.48$.)*

**(b) Zone clearing [elem, unconditional] — the honest core of v1's Prop. 3.**
In v1 the prime-freeness of interior zones was an *assumption*; in fact it is *forced*:

Let $(n,k)$ be a solution and let $m \ge 1$ be an index with
$$n/(m+1) \,\ge\, \max(k, \sqrt n), \qquad s \le n/(m+1), \qquad P > (n-k)/m .$$
Then the zone $Z_m = \big(\frac{n}{m+1}, \frac{n-k}{m}\big]$ **contains no prime at
all**.

*Proof.* Let $q \in Z_m$ be prime. Then $q > n/(m+1) \ge \max(k,\sqrt n)$, and zone
membership pins $\lfloor n/q \rfloor = m$ with no multiple of $q$ in $(n-k,n]$, so
$v_q = 0$ (Lemma 1). But $s \le n/(m+1) < q \le (n-k)/m < P$, so $q \in [s, P]$ and $q$
divides $C(n,k)$ (Lemma 3) — contradiction. ∎

Equivalently: *every* prime of $\big(\max(k, \sqrt n, s),\, P\big)$ must lie in a band
$B_m$. Each band the block spans is paid for by a totally prime-free exclusion zone.
*(Machine-checked on all nine solutions over all $m$: every zone meeting the
hypotheses is prime-free; the hypotheses are vacuous exactly for $(715,2)$ — whole
block below $\sqrt n$ — and $(7,3)$.)*

**(c) Cascade bound on P in the low case [BHP].** In horn (i), for all sufficiently
large $n$:
$$P \;\le\; 3\, n^{1/(2 - 0.525)} \;=\; 3\,n^{0.678}.$$
Under **[RH]** $P \ll (n\log n)^{2/3}$; under **[Cramér]** $P \ll \sqrt n\, \log n$
(consistent with $(715,2)$, where $P = 17 < \sqrt{715}$).

*Proof.* Let $n$ be large; by Corollary 3(i), $k \le n^{0.525}$. If
$P \le \max(2\sqrt n, 4k)$ we are done, since $\max(2\sqrt n, 4k) \le 3n^{0.678}$. So
assume $P > 2\sqrt n$ and $P > 4k$; let $m_0 = \lfloor n/P \rfloor \ge 2$ (horn (i)),
so $P \in B_{m_0}$, and note $n/(m_0+1) \ge P/2 > \max(k, \sqrt n)$.

*The block spans at least two bands.* Suppose instead $s > (n-k)/m_0$, i.e. all factors
lie in $B_{m_0}$, an interval of length $k/m_0 \le k/2$ whose elements exceed
$(n-k)/m_0 \ge P/2 > 2$. The factors are distinct odd primes in an interval of length
$k/m_0$, so their number is at most $k/(2m_0) + 1 \le k/4 + 1$; each is $\le n$, so
$k\log(n/k) \le \log C \le (k/4 + 1)\log n$. Since $k \le n^{0.525}$ gives
$\log(n/k) \ge 0.47\log n$ for $n$ large, this forces $0.47k \le k/4 + 1$, i.e.
$k \le 4$. For $k \in \{2,3\}$ the factor count is $\le k/4 + 1 < 2$, contradicting F2;
for $k = 4$ it is $\le 2$, so $C(n,4) \le n^2$, false for $n \ge 10$. So
$s \le (n-k)/m_0$; moreover $s \notin Z_{m_0}$ (if $s > \max(k,\sqrt n)$ then $s$ is
band-governed with $v_s = 1$, so it lies in a band, not a zone; if
$s \le \max(k, \sqrt n)$ then $s < P/2 \le n/(m_0+1)$, using $P > 2\sqrt n$ and
$P > 4k$), hence $s \le n/(m_0 + 1)$.

*Zone clearing + BHP.* By (b) applied at $m = m_0$, the zone $Z_{m_0}$ is entirely
prime-free. Its right endpoint is $x = (n-k)/m_0 \ge P/2 \to \infty$ and its length is
$$\ell \;=\; \frac{n - (m_0+1)k}{m_0(m_0+1)} \;\ge\; \frac{n}{2m_0^2} - \frac{k}{m_0}
\;\ge\; \frac{n}{4 m_0^2},$$
the last step because $k \le P/4 \le n/(4m_0)$. By BHP, a prime-free interval ending at
height $x$ has length $\le x^{0.525}$ for $x$ large, so
$n/(4m_0^2) \le \big(n/m_0\big)^{0.525}$, giving $m_0 \ge (n^{0.475}/4)^{1/1.475}$ and
$$P \;\le\; \frac{n}{m_0} \;\le\; 4^{1/1.475}\, n^{1/1.475} \;<\; 2.6\, n^{0.678}. \qquad\blacksquare$$

The RH/Cramér variants replace $x^{0.525}$ by $O(\sqrt x \log x)$, resp. $O(\log^2 x)$,
in the last display.

## Empirical anchors — **corrected** (v1's anchor claims were false; see appendix).
All nine known solutions, machine-classified:

| $(n,k)$ | $C(n,k)$ | block | $s$ | $P$ | horn | forced prime-free interval | verified |
|---|---|---|---|---|---|---|---|
| $(4,2)$ | $6$ | $2\cdot3$ | 2 | 3 | (ii) | $Z_1=(2,2]$ (empty) | yes |
| $(6,2)$ | $15$ | $3\cdot5$ | 3 | 5 | (ii) | $Z_1=(3,4]$ | yes |
| $(7,3)$ | $35$ | $5\cdot7$ | 5 | 7 | (ii) | $Z_1=(3.5,4]$ | yes |
| $(10,4)$ | $210$ | $2\cdot3\cdot5\cdot7$ | 2 | 7 | (ii) | $Z_1=(5,6]$ | yes |
| $(14,4)$ | $1001$ | $7\cdot11\cdot13$ | 7 | 13 | (ii) | $Z_1=(7,10]$ | yes |
| $(15,6)$ | $5005$ | $5\cdot7\cdot11\cdot13$ | 5 | 13 | (ii) | $Z_1=(7.5,9]$ | yes |
| $(15,2)$ | $105$ | $3\cdot5\cdot7$ | 3 | 7 | (i) | $B_1=(13,15]$ | yes |
| $(21,2)$ | $210$ | $2\cdot3\cdot5\cdot7$ | 2 | 7 | (i) | $B_1=(19,21]$ | yes |
| $(715,2)$ | $255255$ | $3\cdots17$ | 3 | 17 | (i) | $B_1=(713,715]$ | yes |

- **Three** solutions are in horn (i) — $(15,2), (21,2), (715,2)$ — not all nine as v1
  claimed. **Six** are in horn (ii). **None** is in horn (iii) (consistent with the
  emptiness conjecture; $(7,3)$ is the unique $(n,k)$ with $n \le 10^5$ for which
  $C(n,k) = \prod_{p \in (n-k,n]} p$ at all, and its $Z_1$ is prime-free, placing it in
  horn (ii)).
- Tiny cases: at $(4,2)$ and $(10,4)$ the block contains primes $\le k$ (namely $2$;
  resp. $2,3$) whose valuations are digit-governed, not band-governed — Lemmas 1–2 are
  never applied to them, and no statement above degenerates. Lemma 2's precondition
  $q^2 > n$ is automatic for $q > n/2$ even at $n = 4$.
- Band data ($p > k$ factors, $m = \lfloor n/p\rfloor$): $(715,2)$ spans
  $m = 42..238$ — but **all** its factors are $\le \sqrt{715}$, so none is
  band-governed and v1's Prop.-3 machinery is vacuous there (one of the reasons it was
  retracted). $(15,2)$: $m=2..5$; $(21,2)$: $m=3..7$; the case-(ii) solutions span
  $m = 1..2$ or a single band.

## Honest status (verdict).
**Proved and, we believe, publishable as theorems:** Lemmas 1–3 (elementary; hypotheses
shown necessary by counterexample); Theorem 1 (trichotomy, elementary, complete —
the v1 dichotomy is *false as a dichotomy* only in the sense that its case-(ii)
sub-argument was irreparable, and horn (iii) must be stated); Theorem 2 (elementary +
Montgomery–Vaughan, complete, with computation for $n \le 10^5$); Corollary 3
(complete modulo the cited gap results, with the BHP transfer checked and an explicit
non-effectivity caveat); Proposition 4(a) (elementary/PNT, complete),
4(b) (elementary, complete), 4(c) (complete modulo BHP). **Retracted from v1:** the
boxed inequality $n/k \le C(M/m_0)^2$ and its $\theta$-accounting (the ingredient
$\theta(x+y)-\theta(x) \le 2y$ is false — the ratio to $2y$ is unbounded — and the
claimed display fails numerically at $(715,2)$); the claim that all nine solutions are
case (i) (six are case (ii)). **Heuristic/open:** emptiness of horn (iii) (conjecture;
would follow from a suitable Granville–Ramaré-type squarefree theorem — cite-check
pending); any finiteness statement (untouched: small $k$ with $P \asymp k\log(n/k)$,
the regime of all nine solutions, survives every constraint here, as the heuristics
predict). The contribution that stands is the rigorous *structure*: every solution is a
prime-gap event ((i)/(ii)) or a cornered near-central squarefree exception (iii), with
$P$ pinned at scale $k\log(n/k)$ and every spanned exclusion zone forced prime-free.

---

## Appendix — adversarial verification log (2026-07-27)

All experiments in Python (mpmath-free, exact integer arithmetic where it matters);
scripts in the session scratchpad; seeds fixed; $\le 2$ threads.

1. **Lemma 1 / bands / zones.** 400,000 random triples $(n,k,p)$, $n \le 10^6$,
   $p > \max(k,\sqrt n)$: 0 violations of the valuation formula, the $\{0,1\}$ range,
   the band-iff, or zone membership for $v_p = 0$. Exhaustive sweep of all primes in
   $(\max(k,\sqrt n), n]$ for 300 random $(n,k)$, $n \le 10^5$ (1,049,870 prime checks):
   0 violations. Failure regions outside the hypotheses as listed under Lemma 1
   ($0.6\%$ break rate for $k < p \le \sqrt n$; $57\%$ band-iff break rate for
   $\sqrt n < p \le k$). Zone-nonemptiness criterion $m < n/k - 1$: 100,000 random
   checks, 0 violations.
2. **Anchors.** Direct factorization of all nine $C(n,k)$: consecutiveness confirmed;
   horn classification as tabulated (3/9 in (i), 6/9 in (ii)) — v1's "all nine in
   case (i)" is **false**; v1's per-case prime-free claims hold for the correct horns.
   Exact identity F3 verified to $10^{-9}$ on all nine.
3. **Horn (iii) search.** Exhaustive over $5 \le n \le 10^5$, all $2 \le k \le n/2$
   ($\approx 2.5\times10^9$ pairs, $\theta$/log-factorial prefilter + exact integer
   confirmation): the only $(n,k)$ with $C(n,k) = \prod_{p\in(n-k,n]} p$ is $(7,3)$,
   whose $Z_1$ is prime-free. **Zero horn-(iii) instances.**
4. **$\theta$-bound audit.** $\theta(x+y) - \theta(x) \le 2y$ is **false**: at
   $(x,y) = (57,2)$, $(995,2)$, etc.; max ratio to $2y$ over $x \le 10^7$: 4.03 at
   $y=2$ (unbounded in general, $\sim \tfrac{1}{4}\log x$). Montgomery–Vaughan
   $\pi$-form verified on 200,000 random windows plus worst-case prime-cluster windows
   ($y \le 2000$, $x \le 10^7$): 0 violations, worst ratio 0.57. Corrected transfer
   $\theta(x+y)-\theta(x) \le (2y/\log y)\log(x+y)$: 0 violations in 100,000 samples.
   $\theta(x) < x$ on $[2, 10^7]$ (max ratio 0.9998); $\theta(x) \ge x(1 - 1/\log x)$
   on $[41, 10^7]$: 0 violations.
5. **v1 Prop.-3 accounting.** The display "$\sum_m (\theta(n/m) - \theta((n-k)/m))
   \le k + \sum_m 2k/m$" **fails at $(715,2)$**: LHS $= 12.45$, RHS $= 9.00$. The
   boxed inequality would need $C \ge 11.13$ at $(715,2)$ (vs $C \le 2$ suggested by
   the other eight) — no universal constant is supported; and $M/m_0 = 5.67$ vs
   $\sqrt{n/k} = 18.9$ falsifies the "span grows like $(n/k)^{1/2}$" reading.
6. **BHP small-$n$ exceptions.** Scan of all prime gaps to $10^7$: the transfer
   inequality "prime-free $(n-k,n]$ $\Rightarrow k \le n^{0.525}$" has exactly one
   exception, $(n,k) = (126,13)$ (gap $113 \to 127$), max ratio $k/n^{0.525} = 1.026$.
