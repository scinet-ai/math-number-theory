# Citations for THEOREM.md (Erdős #386) — verified against primary sources

Compiled 2026-07-27. Method: primary PDFs fetched and read directly (Granville–Ramaré
preprint from Granville's site; Baker–Harman–Pintz journal PDF; Yamada arXiv HTML;
Granville–Ramaré bibliography pages), erdosproblems.com pages #386 (problem + full
discussion thread) and #175 fetched with a browser User-Agent. Anything verified only
from a secondary source is flagged as such. Nothing below is cited from memory.

---

## 1. Granville–Ramaré 1996 — squarefree binomial coefficients

**Bibliography.** A. Granville and O. Ramaré, *Explicit bounds on exponential sums and
the scarcity of squarefree binomial coefficients*, Mathematika **43** (1996), no. 1,
73–107. Preprint PDF (verified, read): http://www.dms.umontreal.ca/~andrew/PDF/ramare.pdf

> **Numbering caveat.** All theorem numbers below are from the preprint on Granville's
> site. The journal version may renumber (forum user StijnC refers to a "conjecture 3",
> which does not exist in the preprint — it has a single "Conjecture 1"). If the draft
> cites by number, check the Mathematika version; safer to quote statements.

### (a) Central case C(2n,n) — exact statements (transcribed from the PDF)

- **Theorem 1.** "$\binom{2n}{n}$ is not squarefree for any $n > 4$." (Footnote:
  "Velammal [Ve] has also proved this result recently.")
- Proof route stated in the introduction: exponential-sum bounds show $\binom{2n}{n}$ is
  divisible by the square of some prime $> \sqrt n$ when $n \ge 2^{1617}$; since
  $4 \mid \binom{2n}{n}$ unless $n$ is a power of 2, only $\binom{2^{k+1}}{2^k}$ for
  $2 < k \le 1617$ needed computer verification (all are divisible by 9 except
  $\binom{2^7}{2^6}$, divisible by $5^3 11^2$, and $\binom{2^9}{2^8}$, divisible by
  $7^2 13^2$).
- **Theorem 1\*.** "$\binom{2n}{n}$ is divisible by the square of some prime
  $\ge \sqrt{n/5}$, for all $n \ge 2082$." They note $\binom{1572}{786}$ is the largest
  $\binom{2n}{n}$ not divisible by the square of an odd prime.

History of the central case: conjectured by Erdős; **Sárközy** proved it for all
sufficiently large $n$: A. Sárközy, *On divisors of binomial coefficients, I*,
J. Number Theory **20** (1985), 70–80 (reference verified from the GR bibliography,
entry [Sar]). Granville–Ramaré and, independently, **Velammal** settled all $n > 4$:
G. Velammal, *Is the binomial coefficient $\binom{2n}{n}$ squarefree?*,
Hardy–Ramanujan Journal **18** (1995), DOI 10.46298/hrj.1995.132 (verified at
https://hrj.episciences.org/132). erdosproblems.com/175 states the same attribution.

### (b) The "min(k, n−k) ≥ f(n) ⇒ not squarefree" theorem — YES, it exists

- **Theorem 2 (verbatim).** "There exists a constant $\tau_1 > 0$ such that if $n$ is
  sufficiently large and $\binom{n}{k}$ is squarefree then $k$ or $n-k$ is
  $< \exp\big(\tau_1 (\log n)^{2/3} (\log\log n)^{1/3}\big)$."

  So $f(n) = \exp\big(\tau_1(\log n)^{2/3}(\log\log n)^{1/3}\big)$. As stated, $\tau_1$
  and the "sufficiently large" threshold are **not made explicit** — do not claim an
  effective/numeric version.

- Context sentence after Theorem 2: "The primes $p$ in our proof, for which $p^2$
  divides $\binom{n}{k}$, are close to either $\sqrt k$ or $\sqrt n$."
- Predecessor: "Recently Sander [Sa1] has proved that $\binom{n}{k}$ is not squarefree
  if $k$ is 'close' to $n/2$" — [Sa1] = J. W. Sander, *On prime power divisors of
  binomial coefficients*, Bull. London Math. Soc. **24** (1992), 140–142 (verified from
  GR bibliography). erdosproblems.com/175 additionally states: "Sander [Sa92b] proved
  that, for all $0<\epsilon<1$, if $n$ is sufficiently large and $|d| \le n^{1-\epsilon}$
  then $\binom{2n+d}{n}$ is not squarefree." (Sander's other 1992 paper: *Prime power
  divisors of binomial coefficients*, J. reine angew. Math. **430** (1992), 1–20 = GR's
  [Sa2]; I did not determine which of the two contains the $2n+d$ statement — check
  before citing it by venue.)

### (c) What remains conjectural / the other direction (all verbatim from the preprint)

- **Conjecture 1.** "There exists a constant $\tau_2 > 0$ such that if $n$ is
  sufficiently large and $\binom{n}{k}$ is squarefree then $k$ or $n-k$ is
  $< \tau_2(\log n \log\log n)^2$."
- **Theorem 3.** "There exists a constant $\tau_3 > 0$ such that there are infinitely
  many pairs of integers $n$ and $k$ for which $\binom{n}{k}$ is squarefree, with
  $\tau_3 \log^2 n < k < n/2$." — i.e. squarefree entries genuinely occur just above
  the $\log^2 n$ scale; **no theorem can push $f(n)$ below $\log^2 n$**.
- **Theorem 4.** "There exist infinitely many integers $n$ such that $\binom{n}{k}$ is
  squarefree for all $k \le \frac15 \log n$."
- Also noted there: only rows $1,2,3,5,7,11,23$ of Pascal's triangle consist entirely
  of squarefree entries ("a result proved by Erdős long ago"), and (Theorem 6) for each
  fixed $k$ the set of $n$ with $\binom{n}{k}$ squarefree has positive density
  $c_k = e^{-\{\alpha+o(1)\}\sqrt k/\log k}$, $\alpha \approx 1.825108$.
- Wirsing is cited for a quantitative version of Theorem 2 ("[W], Theorem 3":
  if $n^\varepsilon < k \le n/2$ then $\sum_{p^2 \mid \binom{n}{k}} \frac{\log p}{p}
  \sim (1-\log 2)\log k$); GR's bibliography lists it as E. A. Wirsing, *Multiple prime
  divisors of binomial coefficients*, **(to appear)** — I could not find a published
  version; treat as unverifiable/unpublished.

### Later improvements (checked through July 2026)

- **No paper by "Pandey" on squarefree binomial coefficients was found** (multiple
  searches, arXiv sweeps). Treat that lead as nonexistent unless a concrete pointer
  exists. No improvement to the range in GR Theorem 2 was found either.
- The modern related result is K. Matomäki, M. Radziwiłł, X. Shao, T. Tao,
  J. Teräväinen, *Singmaster's conjecture in the interior of Pascal's triangle*,
  Quart. J. Math. **73** (2022), 1137–1177; arXiv:2106.03335. Its "interior" region is
  exactly $\exp(\log^{2/3+\varepsilon} n) \le m \le n - \exp(\log^{2/3+\varepsilon} n)$
  (same shape as GR Theorem 2). Tao's forum comment (item 5 below) sketches how its
  Proposition 1.12 (equidistribution) re-derives non-squarefreeness in that range —
  explicitly a "back of the envelope calculation", not a theorem in print.

### What THEOREM.md may / may not claim

- **MAY:** A product of *consecutive primes each to the first power* is squarefree, so
  GR Theorem 2 applies verbatim: **for $n$ sufficiently large, every solution of #386
  has $\min(k, n-k) < \exp\big(\tau_1(\log n)^{2/3}(\log\log n)^{1/3}\big)$.** In
  particular the draft's case (ii) horn ($k = n/2 - O(n^{0.525})$, hence
  $\min(k,n-k) \sim n/2$) is **unconditionally empty for large $n$** — a theorem, not
  a conjecture. This also asymptotically supersedes Corollary 2's $k \ll n^{0.525}$
  (since $\exp((\log n)^{2/3+o(1)}) \ll n^{\varepsilon}$): the draft should present its
  elementary bound as self-contained/effective-in-principle structure, not as the best
  known bound on $k$.
- **MAY NOT:** claim the near-central regime is "conjecturally finite" (understates a
  proved result — fix the Empirical-anchors bullet); claim any explicit $n_0$ or
  $\tau_1$; claim GR say anything about products of consecutive primes per se; cite GR
  theorem *numbers* without checking the journal version; claim non-squarefreeness for
  $k$ below $\log^2 n$ (Theorem 3 forbids it).

---

## 2. Baker–Harman–Pintz 2001 — primes in [x − x^0.525, x]

**Bibliography.** R. C. Baker, G. Harman, J. Pintz, *The difference between consecutive
primes, II*, Proc. London Math. Soc. (3) **83** (2001), no. 3, 532–562.
DOI 10.1112/plms/83.3.532. PDF (verified, read):
http://www.cs.umd.edu/~gasarch/BLOGPAPERS/BakerHarmanPintz.pdf

**Exact statement (verbatim from p. 532):**

> "**Theorem 1.** *For all $x > x_0$, the interval $[x - x^{0.525},\, x]$ contains prime
> numbers.*"
>
> Immediately following: "With enough effort, the value of $x_0$ could be determined
> effectively."

So: asymptotic; $x_0$ is **not** computed in the paper, but the proof is effectivizable
in principle (they say so explicitly). Method: Harman's sieve + mean-value results on
Dirichlet polynomials (incl. Watt's theorem), not zero-density estimates.

**2024–2026 status (checked):** no improvement to 0.525 for *existence of primes in all
short intervals* found through July 2026; secondary surveys as of mid-2026 still list
$p_{n+1}-p_n \ll p_n^{0.525}$ as the unconditional record. **Guth–Maynard** (L. Guth,
J. Maynard, *New large value estimates for Dirichlet polynomials*, arXiv:2405.20552,
submitted May 2024, revised April 2026) prove the zero-density estimate
$N(\sigma,T) \le T^{30(1-\sigma)/13+o(1)}$ and obtain **asymptotics** for primes in
intervals of length $x^{17/30+o(1)}$ ($17/30 \approx 0.5667$) — a PNT-type statement in
a *longer* interval, which does **not** supersede BHP's existence result; no derived
gap exponent better than 0.525 was found in the follow-up literature.

**May claim:** in case (i), a prime-free $(n-k, n]$ forces $k < n^{0.525}$ for
$n > x_0$ (apply Theorem 1 at $x = n$). Symmetrically in case (ii) via the draft's own
argument. **May not claim:** any numeric $x_0$; "effective" without the qualifier
"effectivizable with enough effort (not carried out)"; any post-2024 improvement.

---

## 3. Montgomery–Vaughan 1973 — Brun–Titchmarsh for intervals

**Bibliography.** H. L. Montgomery and R. C. Vaughan, *The large sieve*, Mathematika
**20** (1973), 119–134. DOI 10.1112/S0025579300004708. (Paywalled; statements below
verified via T. Yamada, *Explicit improvements of the Brun-Titchmarsh theorem for
arbitrary intervals*, arXiv:2312.16090 (Dec 2023), whose introduction states the MV
results as its (1) and (4).)

**Exact form.** MV proved the Brun–Titchmarsh inequality with $C = 2$:
$$\pi(x+y;k,a) - \pi(x;k,a) < \frac{2y}{\varphi(k)\log(y/k)}$$
uniformly in $k$ and $x$, "provided only that $k < y$ and $\gcd(k,a)=1$" (Yamada's
phrasing of the hypothesis). Specializing $k = 1$:
$$\boxed{\ \pi(x+y) - \pi(x) < \frac{2y}{\log y}\quad \text{for all } x > 0,\ y > 1.\ }$$
The draft's use $\pi(n) - \pi(n-k) \le 2k/\log k$ (take $x = n-k$, $y = k \ge 2$) is
valid. MV also proved the refined form
$\pi(x,x+y;k,a) < 2y/(\varphi(k)(\log(y/k) + 5/6))$ for $y > ck$ with an inexplicit
absolute constant $c$.

**Best current constants.** Yamada (arXiv:2312.16090, Theorem 2): for any positive
reals $x, y$ with $y > k$,
$\pi(x+y;k,a)-\pi(x;k,a) < 2y/(\varphi(k)(\log(y/k) + 0.8601))$; for $k=1$ this gives
$\pi(x+y)-\pi(x) < 2y/(\log y + 0.8601)$, $y > 1$ — the best explicit interval form I
found. The leading constant **2 remains unimproved for arbitrary intervals** (only the
secondary term has moved). In arithmetic progressions there are range-restricted
improvements (e.g. Motohashi; J. Maynard, *On the Brun-Titchmarsh theorem*, Acta Arith.
**157** (2013), 249–296 — page numbers are the standard citation, not re-verified today
— gives $\pi(x;q,a) < 2\,\mathrm{Li}(x)/\varphi(q)$ for $q_0 \le q \le x^{1/8}$, which
is about the full interval $[1,x]$, not short intervals).

**FLAG for Proposition 3 of the draft.** The bracketed hope
"$\theta(x+y)-\theta(x) \le 2y$ for $y \ge 2$?" is **not** a Montgomery–Vaughan result
and I found no such theorem. What MV gives is
$\theta(x+y)-\theta(x) \le \frac{2y}{\log y}\,\log(x+y)$, i.e. an extra factor
$\log(x+y)/\log y$. In Prop. 3's application (window length $y = k/m$ at height
$x \approx n/m$) that factor is $\approx \log(n/m)/\log(k/m)$, which is $\gg 1$ in the
relevant regime $k \ll n$ — the "$\theta$-difference $\le 2k/m\cdot(1+o(1))$" step and
the boxed constant therefore need reworking (e.g. carry the $\log$ factor, or bound
prime *counts* per band and multiply by $\log$ of the band top).

---

## 4. Cramér's conjecture and the FGKMT long-gaps lower bound

**Cramér's conjecture.** H. Cramér, *On the order of magnitude of the difference
between consecutive prime numbers*, Acta Arith. **2** (1936), 23–46. Conjecture (as
standardly quoted): $p_{n+1} - p_n = O\big((\log p_n)^2\big)$, in the strong form
$\limsup_{n\to\infty} (p_{n+1}-p_n)/(\log p_n)^2 = 1$. [Verified from secondary
sources (Wikipedia "Cramér's conjecture" + surveys), not the 1936 paper itself.]
**Granville's revision:** the Cramér model is biased; the limsup should be
$\ge 2e^{-\gamma} \approx 1.1229$ (A. Granville, *Harald Cramér and the distribution of
prime numbers*, Scand. Actuarial J. 1995(1), 12–28 — venue/pages from secondary
sources). Recommended phrasing for the draft: "under Cramér–Granville-type conjectures,
$k \ll \log^{2+o(1)} n$" rather than a bare $\log^2 n$ with constant 1.

**RH-conditional gap bound** (used in Corollary 2's "$k \ll \sqrt n \log n$ under RH"):
H. Cramér, *Some theorems concerning prime numbers*, Ark. Mat. Astron. Fys. **15**
(1920), no. 5: on RH, $p_{n+1} - p_n = O(\sqrt{p_n}\,\log p_n)$. [Secondary-verified.]

**Ford–Green–Konyagin–Maynard–Tao lower bound.** K. Ford, B. Green, S. Konyagin,
J. Maynard, T. Tao, *Long gaps between primes*, J. Amer. Math. Soc. **31** (2018),
no. 1, 65–105; arXiv:1412.5029. Exact shape (verified from the arXiv abstract): with
$G(X) = \max_{p_{n+1}\le X}(p_{n+1}-p_n)$,
$$G(X) \gg \frac{\log X \,\cdot\, \log\log X \,\cdot\, \log\log\log\log X}{\log\log\log X}$$
for sufficiently large $X$ (numerator: $\log \cdot \log_2 \cdot \log_4$; denominator:
$\log_3$, iterated logs). Predecessors (Ford–Green–Konyagin–Tao, and independently
Maynard, both Ann. of Math. **183** (2016)) obtained Rankin's function with an
arbitrarily large constant, answering Erdős's $10,000 problem; FGKMT then removed one
$\log_3$ factor.

**May claim:** unconditionally there exist prime-free intervals below $X$ of length
$\gg \log X \log_2 X \log_4 X/\log_3 X$ for all large $X$ — so gap-*upper*-bound
constraints can never by themselves force $k \ll \log n$ in case (i). **May not
claim:** that such gaps occur at prescribed locations $(n-k, n]$ (existence is
somewhere below $X$; no control on position), nor use FGKMT to *construct* candidate
solutions.

---

## 5. erdosproblems.com/386 — problem page and discussion thread (fetched 2026-07-27)

Fetched with a browser User-Agent via curl: https://www.erdosproblems.com/386 and
https://www.erdosproblems.com/forum/discuss/386 (13 comments; all captured).
Recommended citation per the site itself: "T. F. Bloom, Erdős Problem #386,
https://www.erdosproblems.com/386, accessed 2026-07-28" [string as generated by the
site at fetch time]. **Site disclaimer (quote):** "All comments are the responsibility
of the user. Comments appearing on this page are not verified for correctness." Cite
these only as *unrefereed forum discussion*; original source for the problem is
[ErGr80] = P. Erdős and R. L. Graham, *Old and new problems and results in
combinatorial number theory*, Enseign. Math., Geneva (1980), p. 74.

**Problem statement (verbatim):** "Let $2\leq k\leq n-2$. Can $\binom{n}{k}$ be the
product of consecutive primes infinitely often? For example
$\binom{21}{2}=2\cdot 3\cdot 5\cdot 7$."

**Main-page remark (verbatim):** "Erdős and Graham write that 'a proof that this cannot
happen infinitely often for $\binom{n}{2}$ seems hopeless; probably this can never
happen for $\binom{n}{k}$ if $3\leq k\leq n-3$.' Weisenberg has provided four easy
examples that show Erdős and Graham were too optimistic here: $\binom{7}{3}=5\cdot 7$,
$\binom{10}{4}=2\cdot 3\cdot 5\cdot 7$, $\binom{14}{4}=7\cdot 11\cdot 13$, and
$\binom{15}{6}=5\cdot 7\cdot 11\cdot 13$. The known values of $n$ for which
$\binom{n}{2}$ is the product of consecutive primes are $4,6,15,21,715$ (see A280992)."
[5 + 4 = the draft's nine known solutions.]

### Key comments, verbatim (author — timestamp as displayed)

**DesmondWeisenberg — 10:12 on 21 Aug 2025** (the $n/3 < k \le n/2$ exclusion):
> "No doubt this can be improved significantly, but in the spirit of ruling out
> examples in the interior of Pascal's triangle, here's a nice result to start us off:
> let $n$ be large, and suppose $\frac{n}{3} < k \leq \frac{n}{2}$. Then $\binom{n}{k}$
> is not a product of consecutive primes. To prove this, we start with four facts that
> aren't too hard to verify under the given hypotheses: Fact 1: $\binom{n}{k}$ is not a
> multiple of any primes in $(\frac{n}{3}, k]$. Fact 2: $\binom{n}{k}$ is a multiple of
> every prime in $(k, \frac{n}{2}]$. Fact 3: $\binom{n}{k}$ is not a multiple of any
> primes in $(\frac{n}{2}, n - k]$. Fact 4: $\binom{n}{k}$ is a multiple of every prime
> in $(n - k, n]$. Using facts 2, 3, and 4, we see that if there are primes in both
> $(k, \frac{n}{2}]$ and $(\frac{n}{2}, n - k]$, then $\binom{n}{k}$ is not a product
> of consecutive primes. So suppose at least one of those intervals does not have any
> primes. Then we must have $k \sim \frac{n}{2}$. If $k \sim \frac{n}{2}$, then by
> Stirling's approximation, we have $\binom{n}{k} = (2 + o(1))^n$. For the sake of
> contradiction, suppose $\binom{n}{k}$ is the product of consecutive primes. It is
> well-known that the product of primes up to $x$ is $e^{(1 + o(1))x}$. Combined with
> facts 1 and 4, it follows that $\binom{n}{k} = e^{(\frac{1}{2} + o(1))n}$. However,
> $e^\frac{1}{2} \not= 2$, so we have a contradiction."

**Thomas Bloom — 11:33 on 21 Aug 2025** (reply):
> "Very nice Desmond! This feels like it can be strengthened significantly also (e.g.
> Fact 1 was overkill, since just missing out a single prime $\sim k$ would suffice).
> Presumably a version of this argument (perhaps importing a little technology from the
> paper Tao mentions) would suffice to rule out $k\in [\epsilon n, n/2]$ for
> $n\gg_\epsilon 1$."

**DesmondWeisenberg — 20:58 on 21 Aug 2025** (the $k = o(n)$ claim):
> "After thinking about it more, yes, I actually can prove the following (which is the
> same as what you suggested): let $2 \leq k \leq \frac{n}{2}$, and suppose
> $\binom{n}{k}$ is a product of consecutive primes. Then $k = o(n)$. No advanced
> machinery is needed - again, this just follows from Stirling's approximation and the
> primorial estimate. We only need two facts this time: Fact 1: $\binom{n}{k}$ is not a
> multiple of any primes in $(\frac{n}{2}, n - k]$. Fact 2: $\binom{n}{k}$ is a
> multiple of every prime in $(n - k, n]$. Since I proved in my previous comment that
> $k \leq \frac{n}{3}$ for all large $n$, it follows that for all large $n$ there is a
> prime in $(\frac{n}{2}, n - k]$. So, assuming $k$ is large enough for there to be a
> prime in $(n - k, n]$, the value of $\binom{n}{k}$ is at most the product of all
> primes in $(n - k, n]$. Now, for the sake of contradiction, suppose $k \not= o(n)$.
> Then by standard results in analysis, we can choose some constant
> $c \in \left(0, \frac{1}{3}\right]$ and assume that $k \sim cn$. The product of all
> primes in $(n - k, n]$ is then $(e^c + o(1))^n$, so
> $\binom{n}{k} \leq (e^c + o(1))^n$. However, Stirling's approximation tells us that
> $\binom{n}{k} = \left(\frac{1}{c^c(1-c)^{1-c}} + o(1)\right)^n$. For all
> $c \in \left(0, \frac{1}{3}\right]$, we have
> $\frac{1}{c^c(1-c)^{1-c}} > e^c$, so we have reached a contradiction. This completes
> the proof that $k = o(n)$, but I still feel like we're just starting out - I used
> compactness for simplicity, but I'm sure my argument could be made more explicit and
> probably significantly improved. One goal might be to prove (assuming $n$ is
> sufficiently large and $k \leq \frac{n}{2}$) that $k$ must be small enough so there
> are no primes in $(n - k, n]$."

**StijnC — 04:37 on 22 Aug 2025** (prime-free-interval observation; transcribed from
the raw HTML — the page's own math here is informally typeset, including a typo
"$((n-k/2,n/2]$" for $((n-k)/2, n/2]$; inequality signs rendered oddly in-browser):
> "Extending the improvement by Desmond, we conclude that both $((n-k/2,n/2]$ and
> $(n-k,n]$ should not contain any primes once $n$ is sufficiently large.
> For $n$ sufficiently large. *If $k$ satisfies $n^{0.525}<k \le n/3$, then there are
> primes in $p \in (n-k,n]$, $q \in (n/2,n-k]$ and $r \in ((n-k)/2,n/2]$. So
> $p$<$q$$n^{k-1}$ and thus it is not equal to the product of the primes in $(n-k,n]$
> (at most $k-1$) For $7\le k \le \sqrt n$, $\binom{n}{k}$>$n^{k/2}$, while there are
> less than $k/2$ primes in $(n-k,n]$, so again
> $\binom{n}{k} $>$ \prod_{n-k+1 \le p\le n} p.$ If $\sqrt n $<$ k \le n^{0.6}$, then
> $\binom{n}{k} \gg n^{0.4k}$, while less than $k/3$ values in $(n-k,n]$ are primes. So
> again $\binom{n}{k} \not= \prod_{n-k+1\le p\le n} p.$ Note that if $((n-k)/2,n/2]$
> contains any primes, while $(n-k,n]$ contains no primes and thus $k$<$n^{0.525}$, one
> would need $\binom{n}{k}= \prod_{(n-k+1)/2 \le p\le n/2} p.$ Now the same estimates
> as above are even clearer and it is not possible. Thus both $((n-k)/2,n/2]$ and
> $(n-k,n]$ should not contain any primes. Cramer's conjecture predicts that
> $k=O(\log^2 n)$, or updated by others to $\log^{2+o(1)}(n)$, is rather small in that
> case."

**TerenceTao — 16:37 on 10 Aug 2025:**
> "It is possible that the arguments from my paper with Matomaki, Radziwill, Shao, and
> Teravainen can be adapted to prove a similar result here, namely that one can exclude
> the possibility of a counterexample in the 'interior' region of Pascal's triangle."

**DesmondWeisenberg — 00:36 on 13 Aug 2025** (reply):
> "A result of Sander discussed in [175] shows that there are no squarefree numbers far
> enough in the interior of Pascal's triangle. So that should be a good start."

**TerenceTao — 15:08 on 26 Aug 2025** (the Singmaster-style sketch):
> "A back of the envelope calculation suggests that one can rule out $\binom{n}{k}$
> being square-free (and a fortiori, rule out being a product of consecutive primes)
> for $\exp(\log^{2/3+\varepsilon} n) \leq k \leq n/2$ and $n$ sufficiently large as in
> the Singmaster conjecture paper. A sketch is as follows. Select a scale $P$ with
> $P \lll k \ll n \lll \exp(\log^{3/2-\varepsilon} P)$. By the Legendre formula, for
> any prime $p \sim P$, the number of times $p$ divides $\binom{n}{k}$ is
> $\sum_{j=1}^\infty \left\{\frac{k}{p^j}\right\} + \left\{\frac{n-k}{p^j}\right\} -
> \left\{\frac{n}{p^j}\right\}.$ Each summand is non-negative, so we can truncate at
> say $j=1,2,3$. The equidistribution estimates in Proposition 1.12 of
> https://arxiv.org/pdf/2106.03335 basically tell us that each of these summands has a
> mean of 1/2 as $p$ varies, so this quantity is at least $3/2$ on the average,
> contradicting square-freeness. (One can also use just the $j=1,2$ terms for this
> analysis if one also calculates the variance in addition to the mean.)"

**Vjeko_Kovac — 06:16 on 27 Aug 2025** (reply to Tao):
> "Precisely that bound seems to be the content of Theorem 2 in this paper by Granville
> and Ramaré."

**StijnC — 07:25 on 27 Aug 2025** (reply):
> "Theorem 4 (and conjecture 3) therein indicate that the idea indeed works, except for
> $k$ smaller than polylog n. For this problem, consistent with the previous
> conclusions drawn from Cramer's conjecture."

**TerenceTao — 15:27 on 27 Aug 2025:**
> "Ah, nice! I see that Granville and Ramare solved Erdos #175 with these methods also."

Other comments in the thread (captured, less load-bearing): StijnC — 03:37 on
24 Aug 2025 (heuristic count of products of $\ge 11$ consecutive primes
$\Theta(x^{1/11}/\log x)$ vs $\Theta(x^{1/2})$ values $\binom{n}{2}$; reports "An
independent computer search from Desmond did not result in any additional example ...
[e.g. a new solution for $k=2$ would need $n>10^{500}$ (if no machine errors happened
and some estimates work out)]"); Dogmachine — 12:47 on 24 Aug 2025 (ABC-flavoured
pessimism); Dogmachine — 15:34 on 31 Mar 2026 (speculates Erdős–Graham may have meant
"primorial").

**Threading note:** the thread displays replies nested under parents, so display order
is not chronological; cite by author + timestamp.

**What the draft may / may not claim from the forum.** MAY: cite as "forum discussion
on erdosproblems.com #386 (unrefereed)" for: Weisenberg's four interior examples and
his sketched proofs that (for large $n$) $n/3 < k \le n/2$ is impossible and
$k = o(n)$; StijnC's observation that both $(n-k, n]$ and $((n-k)/2, n/2]$ must be
prime-free for large $n$ (with sub-claims keyed to BHP's 0.525 and Cramér); Tao's
sketch + Kovač's identification of GR Theorem 2 as the rigorous citation for the
$\exp(\log^{2/3+\varepsilon} n) \le k \le n/2$ exclusion. MAY NOT: present any forum
sketch as a proved/refereed result — the site explicitly disclaims verification; if
the draft relies on the $k=o(n)$ statement it must either reprove it (the Stirling vs.
primorial computation is short) or attribute it explicitly as a forum argument. The
rigorous, citable exclusion of the interior is GR Theorem 2 (item 1).

---

## Incidental observations (outside citation scope, flagged for the verifier)

1. **Empirical-anchors bullet appears wrong as stated.** "All nine satisfy case (i)
   ... All nine have $P \le n/2$" fails for the six small solutions:
   $\binom{4}{2}=6$ ($P=3>2$), $\binom{6}{2}=15$ ($P=5>3$), $\binom{7}{3}=35$
   ($P=7>3.5$), $\binom{10}{4}=210$ ($P=7>5$), $\binom{14}{4}=1001$ ($P=13>7$),
   $\binom{15}{6}=5005$ ($P=13>7.5$) — these are case (ii) ($P \in (n-k,n]$, with
   $Z_1=(n/2,n-k]$ prime-free or empty). Only $(15,2), (21,2), (715,2)$ are case (i).
   The "(19,21] for (21,2)" and "(713,715] for (715,2)" checks are correct as far as
   they go, but note $(n-k,n]$ prime-free is the case-(i) condition and $\binom{15}{2},
   \binom{21}{2}, \binom{715}{2}$ do have all factors $\le n/2$. Re-check the sweep
   claim before publishing.
2. Given GR Theorem 2 (item 1), the strongest honest headline for the package is:
   "solutions are prime-gap events with $\min(k,n-k) <
   \exp(\tau_1(\log n)^{2/3}(\log\log n)^{1/3})$ (GR) and, by elementary/effective
   means, $k \ll n^{0.525}$ or $k = n/2 - O(n^{0.525})$ (this draft + BHP)."
