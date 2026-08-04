# A rigid family for Erdős #51: infinitely many totient values with $n_a/a$ exactly $2$

**Problem context (Erdős #51).** For a totient value $a$ (an element of $V=\varphi(\mathbb{N})$)
let $f(a)=n_a=\min\{n:\varphi(n)=a\}$. Erdős asks whether there is an infinite set
$A\subseteq V$ along which $n_a/a\to\infty$. This note proves an unconditional structural
result in the *positive* direction, far short of the problem itself but pinning the first
proved constant:

> **Corollary A.** There are infinitely many $a\in V$ with $n_a/a$ **exactly** $2$; hence
> $\limsup_{a\in V} n_a/a\ \ge\ 2$.

The family is $a=2^k$ for suitable $k$, and the full statement (Theorem 1) is an exact
dichotomy governed by the primality of Fermat numbers.

**What this does and does not say.** The problem wants $n_a/a\to\infty$ along a family; our
family has *constant* ratio $2$, and Tao's heuristic (forum comment on #51, 10 Aug 2025)
predicts the true answer is likely negative (bounded ratio). This note is a structural first
step: it shows the extremal question "does $a$ have a small preimage?" is, for $a=2^k$,
*exactly equivalent* to Fermat-number compositeness — a rigid miniature of the general
obstruction (small preimages of $a$ require primes of the form $d+1$, $d\mid a$), which is
the exact point where the January 2026 ChatGPT attempt on #51 collapsed.

**Notation.** $F_i=2^{2^i}+1$ ($i\ge 0$) is the $i$-th Fermat number. $B(k)\subseteq\mathbb{Z}_{\ge0}$
is the set of positions of $1$-bits in the binary expansion $k=\sum_{i\in B(k)}2^i$. For a
finite $S\subseteq\mathbb{Z}_{\ge0}$ write $\sigma(S)=\sum_{i\in S}2^i$ (so $\sigma(\emptyset)=0$,
and $S\mapsto\sigma(S)$ is injective). $x^+ = \max(x,0)$.

---

## Theorem 1 (exact dichotomy for $a=2^k$)

Let $k\ge 1$. Then $a=2^k$ is a totient value (e.g. $\varphi(2^{k+1})=2^k$), and:

1. **(Classification of preimages.)** $\varphi(n)=2^k$ if and only if
   $$n \;=\; 2^{\,k+1-\sigma(S)}\prod_{i\in S}F_i \quad\text{for some } S \text{ with all } F_i \ (i \in S) \text{ prime and } \sigma(S)\le k,$$
   or
   $$n \;=\; \prod_{i\in B(k)}F_i \quad\text{(odd preimage), possible if and only if } F_i \text{ is prime for every } i\in B(k).$$

2. **(Sizes.)** Every even preimage is $\ge 2^{k+1}$, with equality only for $S=\emptyset$
   (i.e. $n=2^{k+1}$). The odd preimage, when it exists, is unique and lies strictly
   between $2^k$ and $2^{k+1}$.

3. **(Dichotomy.)** Consequently
   $$
   n_{2^k} \;=\;
   \begin{cases}
   \displaystyle\prod_{i\in B(k)}F_i, & \text{if } F_i \text{ is prime for all } i\in B(k),
     \quad\text{with } \dfrac{n_{2^k}}{2^k}=\prod_{i\in B(k)}\bigl(1+2^{-2^i}\bigr)<2,\\[2ex]
   2^{k+1}, & \text{if } F_i \text{ is composite for some } i\in B(k),
     \quad\text{with } \dfrac{n_{2^k}}{2^k}=2 \text{ exactly.}
   \end{cases}
   $$

### Proof

**Lemma 1.1 (shape of preimages).** If $\varphi(n)=2^k$ then $n=2^e\prod_{i\in S}F_i$ with
$e\ge0$ and $S$ a finite set of indices with each $F_i$ prime (each Fermat prime to the
first power).

*Proof.* Let $p$ be an odd prime with $p\mid n$. If $p^2\mid n$ then $p\mid\varphi(n)=2^k$,
impossible; so $p\Vert n$. Also $(p-1)\mid\varphi(n)=2^k$ (as $\varphi(p)=p-1$ divides
$\varphi(n)$ by multiplicativity), hence $p=2^j+1$ for some $j\ge1$. If $j$ had an odd
divisor $t>1$, write $j=ut$; then $2^u+1$ divides $(2^u)^t+1=p$ (since $x+1\mid x^t+1$ for
odd $t$) and $1<2^u+1<p$, contradicting primality. So $j$ is a power of $2$, say $j=2^i$,
i.e. $p=F_i$ is a Fermat prime. Distinct odd primes give distinct indices $i$ because
$i\mapsto F_i$ is strictly increasing. $\square$

**Lemma 1.2 (value of $\varphi$).** For $n=2^e\prod_{i\in S}F_i$ as in Lemma 1.1,
$$\varphi(n)\;=\;2^{(e-1)^+}\prod_{i\in S}2^{2^i}\;=\;2^{(e-1)^++\sigma(S)}.$$

*Proof.* Multiplicativity; $\varphi(2^e)=2^{e-1}$ for $e\ge1$, $\varphi(1)=1$;
$\varphi(F_i)=F_i-1=2^{2^i}$. $\square$

**Lemma 1.3 (binary rigidity).** $\varphi(n)=2^k$ with $n$ **odd** forces $S=B(k)$.

*Proof.* By Lemma 1.2 with $e=0$: $\sigma(S)=k$. By uniqueness of binary representation,
$S=B(k)$. In particular an odd preimage exists iff all $F_i$, $i\in B(k)$, are prime, and
it is then unique. $\square$

**Lemma 1.4 (size bounds).** For any finite set $S$ of indices,
$$2^{\sigma(S)}\;<\;\prod_{i\in S}F_i\;<\;2^{\sigma(S)+1}.$$

*Proof.* The left inequality is $F_i>2^{2^i}$ termwise. For the right, put $m=\max S$ and
use the telescoping identity (difference of squares, $(2-1)\prod_{i=0}^{m}(2^{2^i}+1)=2^{2^{m+1}}-1$):
$$\prod_{i=0}^{m}\bigl(1+2^{-2^i}\bigr)\;=\;\frac{2^{2^{m+1}}-1}{2^{2^{m+1}-1}}\;=\;2\bigl(1-2^{-2^{m+1}}\bigr)\;<\;2 .$$
Since every factor $1+2^{-2^i}$ exceeds $1$, the sub-product over $S\subseteq\{0,\dots,m\}$
is also $<2$, i.e. $\prod_{i\in S}F_i<2\cdot2^{\sigma(S)}$. $\square$

**Assembly.** Let $\varphi(n)=2^k$, $n=2^e\prod_{i\in S}F_i$.

*Even preimages* ($e\ge1$): Lemma 1.2 gives $e-1+\sigma(S)=k$, so $\sigma(S)\le k$ and
$n=2^{k+1-\sigma(S)}\prod_{i\in S}F_i$. By Lemma 1.4 (left), $n>2^{k+1-\sigma(S)}\cdot2^{\sigma(S)}=2^{k+1}$
unless $S=\emptyset$, in which case $n=2^{k+1}$ exactly. Conversely every such $n$ has
$\varphi(n)=2^k$ by Lemma 1.2.

*Odd preimages* ($e=0$): by Lemma 1.3, $n=\prod_{i\in B(k)}F_i$ (needs all these $F_i$
prime), and by Lemma 1.4, $2^k<n<2^{k+1}$.

So: if the odd preimage exists it is the unique preimage below $2^{k+1}$ and hence is
$n_{2^k}$, with ratio $\prod_{i\in B(k)}(1+2^{-2^i})<2$; if it does not exist (some
$F_i$, $i\in B(k)$, composite), the minimum over even preimages is $2^{k+1}$, giving ratio
exactly $2$. $\blacksquare$

---

## Corollary A (unconditional infinite family)

Euler (1732) factored $F_5=2^{32}+1=4294967297=641\cdot 6700417$; in particular $F_5$ is
composite (check: $641\cdot 6700417=4294967297$). Hence for **every** $k$ with bit $5$ set
(i.e. $\lfloor k/32\rfloor$ odd — an infinite set, e.g. all $k\equiv 32 \pmod{64}$),
Theorem 1 gives
$$n_{2^k}\;=\;2^{k+1},\qquad \frac{n_{2^k}}{2^k}\;=\;2 .$$
Therefore $\{2^k:\ \lfloor k/32\rfloor \text{ odd}\}$ is an infinite set of totient values
with ratio exactly $2$, and $\limsup_{a\in V}n_a/a\ge 2$. $\blacksquare$

**Remark A.1 (an explicit unbroken range).** All of $F_5,F_6,\dots,F_{32}$ are known to be
composite (see W. Keller's status tables, *Prime factors of Fermat numbers*,
www.prothsearch.com/fermat.html; the smallest Fermat number of unknown character is
currently $F_{33}$). Since every $k$ with $32\le k<2^{33}$ has a bit in $\{5,6,\dots,32\}$
(its bits all lie below position $33$, and $k\ge32$ forces a bit $\ge5$), Theorem 1 gives
unconditionally
$$n_{2^k}=2^{k+1}\ \text{ (ratio exactly 2)}\qquad\text{for **every** } k \text{ with } 32\le k<2^{33},$$
and $n_{2^k}/2^k<2$ for every $k\le31$. (Only the infinitude claim of Corollary A is
needed downstream, and that uses nothing beyond Euler's factorization of $F_5$.)

**Remark A.2 (extreme rigidity at the boundary).** For $k=31=11111_2$ the odd preimage is
$F_0F_1F_2F_3F_4=3\cdot5\cdot17\cdot257\cdot65537=4294967295=2^{32}-1$, giving
$n_{2^{31}}/2^{31}=2-2^{-31}$ — the ratio creeps to within $2^{-31}$ of $2$ and then, at
$k=32$, snaps to exactly $2$.

**Remark A.3 (Gauss–Wantzel).** By Lemma 1.1, an odd $n$ has $\varphi(n)$ a power of $2$
iff $n$ is a product of distinct Fermat primes, i.e. iff the regular $n$-gon is
constructible with ruler and compass (Gauss–Wantzel, odd part). So the dichotomy reads:
$n_{2^k}/2^k=2$ exactly iff no odd constructible-polygon order $n$ has $\varphi(n)=2^k$.

**Remark A.4 (prior art; honesty about novelty).** The classification in Lemma 1.1–1.3 is
classical. The phenomenon "least $x$ with $\varphi(x)=m$ can be even, first at
$m=2^{16}\cdot257$, and (if there are only five Fermat primes) $\varphi(x)=2^r$ has even
least solution for all $r>31$" was discussed in Amer. Math. Monthly Problem E3361
(W. P. Wardlaw, proposer; solution L. L. Foster and R. J. Simpson, AMM 98 (1991), no. 5,
443–444), as recorded in T. D. Noe's comment on OEIS A002181; the even least-preimages are
now cataloged in OEIS A387221 (J. McCranie, Nov 2025), whose data contains the instances
$n_{2^{32}}=2^{33},\dots,n_{2^{36}}=2^{37}$ of Theorem 1. What we could not find recorded
anywhere (OEIS, erdosproblems.com \#51 page and forum thread, arXiv/web searches — see
`novelty.md`): (i) the *unconditional* infinitude (via a single composite Fermat number)
of totient values with ratio **exactly** $2$, and (ii) its consequence
$\limsup_{a\in V}n_a/a\ge2$ for Erdős \#51. Both are elementary; we claim only that this
packaging appears to be unrecorded, not that it is deep.

**Remark A.5 (why ratio exactly 2 is a natural barrier).** Any even $n$ has
$n/\varphi(n)=\prod_{p\mid n}\frac{p}{p-1}\ge2$, so a totient value whose least preimage
is even automatically has ratio $\ge2$ (this is why OEIS A387221, the even least-preimages,
sits inside our ratio-$\ge2$ census). An **odd** minimal preimage with ratio $\ge2$ must
satisfy $\prod_{p\mid n}\frac{p}{p-1}\ge2$ over odd primes only, which forces at least
three odd prime factors ($\frac32\cdot\frac54=1.875<2\le\frac32\cdot\frac54\cdot\frac76$),
and such cases do occur — e.g. $a=5888$, $n_a=11985=3\cdot5\cdot17\cdot47$, ratio
$2.0355$. All ratios $>2$ observed in the certified census (`computation.md`; max found
$2.0434$) come from odd minimal preimages built from Fermat primes and Sophie-Germain-type
carriers. Proving that any infinite family stays $\ge2+\delta$ is open (and Erdős \#51
itself demands $\to\infty$).

---

## Sharpest correct form, stated for the record

**Theorem 1'** (complete answer for $a=2^k$, $k\ge1$): $n_{2^k}=2^{k+1}$ **iff** some
$i\in B(k)$ has $F_i$ composite; otherwise $n_{2^k}=\prod_{i\in B(k)}F_i$. In all cases
$$1\;<\;\frac{n_{2^k}}{2^k}\;\le\;2,$$
with the value $2$ attained exactly on the composite-bit set, and
$\sup_{k:\ B(k)\subseteq P}\ \prod_{i\in B(k)}(1+2^{-2^i})=2-2^{-2^{m^*+1}}$ over the prime-bit
set, where $P=\{i:F_i \text{ prime}\}$ and $m^*=\max P$ if $P$ is finite (with the sup equal
to $2$, unattained, if $P$ were infinite). Determining the dichotomy for a *specific* $k$ is
exactly the question of Fermat-number primality for the bits of $k$ — e.g. the status of
$n_{2^k}$ for $k=2^{33}$ (single bit $33$) is equivalent to the primality of $F_{33}$,
which is open.

*Verification of instances*: `check_theorems.py` (this workspace) verifies, by exhaustive
inverse-totient enumeration (independent of the sieve), that the preimage sets of $2^k$
for all $1\le k\le 40$ are exactly as classified above, in particular
$n_{2^{15}}=65535=3\cdot5\cdot17\cdot257$ (ratio $1.99997$), $n_{2^{31}}=2^{32}-1$,
$n_{2^{32}}=2^{33}$, $n_{2^{37}}=2^{38}$. The sieve of `computation.md` independently
confirms all cases with $2^k\le A_{\max}$.
