# Structural lemmas for Erdős problem #411: finite certificates for eventual multiplier relations of $g(n)=n+\varphi(n)$

**Problem** (Erdős–Graham 1980, p. 81; erdosproblems.com/411). Let $g(n)=n+\varphi(n)$,
$g_0(n)=n$, $g_{k}(n)=g(g_{k-1}(n))$. For which $n$ and $r$ is it true that
$g_{k+r}(n)=2g_k(n)$ for all large $k$ — and, more generally, for which $(n,r,c)$ does

$$E(n,r,c):\qquad \exists K\ \forall k\ge K:\ g_{k+r}(n)=c\cdot g_k(n)$$

hold, where $c\ge 2$ is an integer?

Throughout, $\operatorname{rad}(c)=\prod_{p\mid c}p$ denotes the radical (squarefree kernel)
of $c$, with $\operatorname{rad}(1)=1$. All variables are positive integers.

This note proves, with all steps included:

* **Lemma 1** ($\varphi$-scaling): $\varphi(cm)=c\,\varphi(m)\iff \operatorname{rad}(c)\mid m$.
* **Theorem 2** (finite-certificate equivalence): $E(n,r,c)$ holds **iff** some orbit point
  $x=g_K(n)$ carries the finite certificate
  $$C(x,r,c):\qquad g_r(x)=c\,x\quad\text{and}\quad \operatorname{rad}(c)\mid g_j(x)\ \ (0\le j<r),$$
  and in that case the relation holds for **all** $k\ge K$ (not merely large $k$).
* **Theorem 3** (parity): orbit parity is constant from the moment the orbit is $\ge 3$;
  consequently every $n$ satisfying $E(n,r,c)$ with $c$ even — in particular the literal
  Erdős–Graham equation $c=2$ — is even with an all-even orbit, and odd starts
  $n\ge 3$ admit only odd multipliers $c$.
* **Lemma 4** (witness scaling) and **Lemma 5** (power relations): the two operations that
  generate derived witnesses from primitive ones, used by the catalogue in
  `proof_catalogue.md`.
* **Lemma 6** (growth bound): a certificate at an even $x$ forces $c\le (3/2)^r$; at any
  $x$, $c<2^r$.

Steinerberger [St25] proves the special case $(r,c)=(2,2)$ of the forward direction of
Theorem 2 in the course of his equivalence ($g_{k+2}(n)=2g_k(n)$ for some $k$ iff
$\varphi(m)+\varphi(m+\varphi(m))=m$ for $m=g_k(n)$), using $\varphi(2m)=2\varphi(m)$ for
even $m$; the case distinction "$\operatorname{rad}(c)\mid m$" for general $c$, the converse
bookkeeping, and the parity statement for general $c$ do not appear there, nor on the
problem page. Cambie's examples on the problem page implicitly use the forward direction
for $c=3,4$; no proof is recorded there.

---

## Preliminaries

**Fact 0.1.** $\varphi(m)\ge 1$ for all $m\ge 1$, hence $g(m)>m$ and every orbit
$(g_k(n))_{k\ge 0}$ is strictly increasing. In particular, if $g_r(x)=cx$ with $r\ge1$ and
$c$ a positive integer, then $c\ge 2$.

**Fact 0.2.** $\varphi(1)=\varphi(2)=1$, and $\varphi(m)$ is even for every $m\ge 3$.
*Proof.* If $m\ge 3$ has an odd prime divisor $p$, then $p-1\mid$ … more precisely
$\varphi(m)$ is divisible by the even number $p-1$ times a positive integer, hence even;
if $m=2^a$ with $a\ge 2$, then $\varphi(m)=2^{a-1}$ is even. $\square$

**Fact 0.3** (Euler product). $\varphi(m)=m\prod_{p\mid m}\left(1-\tfrac1p\right)$,
the product over distinct primes dividing $m$.

---

## Lemma 1 ($\varphi$-scaling)

**Lemma 1.** *For all positive integers $c,m$:*
$$\varphi(cm)=c\,\varphi(m)\quad\Longleftrightarrow\quad \operatorname{rad}(c)\mid m,$$
*i.e. iff every prime dividing $c$ also divides $m$. Moreover, if
$\operatorname{rad}(c)\nmid m$ then $\varphi(cm)<c\,\varphi(m)$.*

*Proof.* The set of primes dividing $cm$ is the union of those dividing $c$ and those
dividing $m$. By Fact 0.3,

$$\varphi(cm)=cm\prod_{p\mid cm}\Bigl(1-\frac1p\Bigr),\qquad
c\,\varphi(m)=cm\prod_{p\mid m}\Bigl(1-\frac1p\Bigr).$$

Since $\{p:p\mid m\}\subseteq\{p:p\mid cm\}$,

$$\frac{\varphi(cm)}{c\,\varphi(m)}=\prod_{\substack{p\mid c\\ p\nmid m}}\Bigl(1-\frac1p\Bigr).$$

Every factor lies in $(0,1)$, so the product equals $1$ iff it is empty, i.e. iff every
prime of $c$ divides $m$; otherwise it is $<1$. $\square$

---

## Theorem 2 (finite-certificate equivalence)

**Definition.** For positive integers $x$, $r\ge 1$, $c\ge 2$, say $x$ *carries the
certificate* $C(x,r,c)$ if

1. $g_r(x)=c\,x$, and
2. $\operatorname{rad}(c)\mid g_j(x)$ for every $0\le j<r$.

Note $C(x,r,c)$ is decidable by computing the $r+1$ numbers $g_0(x),\dots,g_r(x)$.

**Theorem 2.** *Let $n,r\ge1$, $c\ge2$ be integers. The following are equivalent:*

*(i) $E(n,r,c)$: there is $K\ge 0$ with $g_{k+r}(n)=c\,g_k(n)$ for all $k\ge K$;*

*(ii) some orbit point $x=g_K(n)$ ($K\ge 0$) carries $C(x,r,c)$.*

*Moreover, if $x=g_K(n)$ carries $C(x,r,c)$, then $g_{k+r}(n)=c\,g_k(n)$ holds for every
$k\ge K$, and every later orbit point $g_{k}(n)$, $k\ge K$, also carries $C(\cdot,r,c)$.*

*Proof.*

**(ii) $\Rightarrow$ (i), with the "moreover" clause.** Suppose $x$ carries $C(x,r,c)$.
Write $y_i=g_i(x)$ for $i\ge0$, so $y_{i+1}=y_i+\varphi(y_i)$. We prove by strong
induction on $i\ge 0$ the two statements

$$S(i):\ y_{i+r}=c\,y_i,\qquad\qquad D(i):\ \operatorname{rad}(c)\mid y_i.$$

*$D(i)$ for $0\le i<r$* is certificate condition 2. *$S(0)$* is certificate condition 1.

*$D(i)$ for $i\ge r$, given $S(i-r)$:* $y_i=c\,y_{i-r}$ by $S(i-r)$, and
$\operatorname{rad}(c)\mid c\mid c\,y_{i-r}$.

*$S(i)$ for $i\ge 1$, given $S(i-1)$ and $D(i-1)$:*
$$y_{i+r}=g(y_{i+r-1})=g(c\,y_{i-1})=c\,y_{i-1}+\varphi(c\,y_{i-1})
 =c\,y_{i-1}+c\,\varphi(y_{i-1})=c\,\bigl(y_{i-1}+\varphi(y_{i-1})\bigr)=c\,y_i,$$
where the second equality is $S(i-1)$, and the fourth is Lemma 1 applied with $m=y_{i-1}$,
legitimate because $D(i-1)$ says $\operatorname{rad}(c)\mid y_{i-1}$.

The induction is well-founded: $S(i)$ uses $S(i-1),D(i-1)$; $D(i-1)$ is either a
hypothesis ($i-1<r$) or uses $S(i-1-r)$; all indices strictly decrease. Hence $S(i)$ and
$D(i)$ hold for all $i\ge0$.

Now $g_{k+r}(n)=g_{(k-K)+r}(x)=c\,g_{k-K}(x)=c\,g_k(n)$ for every $k\ge K$: this is (i)
with the stated starting index. Finally, for any $K'\ge K$, the point $x'=g_{K'}(n)=y_{K'-K}$
satisfies $g_r(x')=y_{K'-K+r}=c\,y_{K'-K}=c\,x'$ (this is $S(K'-K)$) and
$\operatorname{rad}(c)\mid g_j(x')=y_{K'-K+j}$ for $0\le j<r$ (this is $D$), so $x'$ carries
the certificate as well.

**(i) $\Rightarrow$ (ii).** Suppose $g_{k+r}(n)=c\,g_k(n)$ for all $k\ge K$, and set
$x=g_K(n)$. Certificate condition 1 is the case $k=K$: $g_r(x)=g_{K+r}(n)=c\,g_K(n)=c\,x$.
For condition 2, fix any $k\ge K$ and use the relation at $k$ and at $k+1$:

$$g_{k+r+1}(n)=g\bigl(g_{k+r}(n)\bigr)=g\bigl(c\,g_k(n)\bigr)=c\,g_k(n)+\varphi\bigl(c\,g_k(n)\bigr),$$
$$g_{k+r+1}(n)=c\,g_{k+1}(n)=c\,g_k(n)+c\,\varphi\bigl(g_k(n)\bigr).$$

Subtracting, $\varphi(c\,g_k(n))=c\,\varphi(g_k(n))$, so by Lemma 1 (the "moreover"
direction rules out strict inequality) $\operatorname{rad}(c)\mid g_k(n)$. Taking
$k=K,K+1,\dots,K+r-1$ gives $\operatorname{rad}(c)\mid g_j(x)$ for $0\le j<r$. $\square$

**Remark 2.1 (raw hits are not certificates).** The bare equality $g_r(x)=c\,x$ does
**not** imply $E$: condition 2 has content. Example: $x=3$, $r=2$, $c=3$. The orbit of $3$
is $3,5,9,15,23,\dots$, so $g_2(3)=9=3\cdot 3$ — and even $g_3(3)=15=3\cdot g_1(3)$ — yet
$g_4(3)=23\ne 27=3\cdot g_2(3)$, and indeed $\operatorname{rad}(3)=3\nmid g_1(3)=5$, so no
certificate holds at $x=3$. (In the sweep data at $x\le10^7$, $r\le40$, a substantial
fraction of raw hits — 5825 of 16361 — fail the certificate filter.)

**Remark 2.2 (sharp starting index).** By the "moreover" clause the set of indices $K$
whose orbit point carries the certificate is upward closed; the least such index is
exactly the least $K$ from which the relation holds onward. E.g. for Weintraub's
$g_{k+25}(3114)=729\,g_k(3114)$, recorded on the problem page with "$k\ge 6$": the
certificate already holds at $x=g_5(3114)=12402$, so the relation is valid for all
$k\ge5$; it fails at $k=4$ (computation: $g_{29}(3114)\ne 729\,g_4(3114)$), so $k\ge 5$
is sharp.

---

## Theorem 3 (parity)

**Theorem 3.**
*(a) For every $m\ge 3$, $g(m)\equiv m\pmod 2$. Hence if $n\ge3$, all orbit points
$g_k(n)$, $k\ge0$, have the parity of $n$; and for $n\in\{1,2\}$ the orbit is
$1,2,3,5,\dots$ resp. $2,3,5,\dots$, hence odd from the point $3$ onward.*

*(b) If $E(n,r,c)$ holds with $c$ even, then $n$ is even, $n\ge4$, and every orbit point
$g_k(n)$ is even. In particular this applies to the original Erdős–Graham relation
$g_{k+r}(n)=2g_k(n)$.*

*(c) If $n\ge3$ is odd, then $E(n,r,c)$ can only hold with $c$ odd.*

*Proof.* (a) For $m\ge3$, $\varphi(m)$ is even (Fact 0.2), so $g(m)=m+\varphi(m)\equiv m
\pmod 2$. The orbit is strictly increasing (Fact 0.1), so once $\ge3$ — which holds from
$n$ itself if $n\ge3$, and from the value $3$ onward for $n\in\{1,2\}$ — parity never
changes again.

(b) Suppose $g_{k+r}(n)=c\,g_k(n)$ for all $k\ge K$ with $c$ even. Choose $k\ge K$ large
enough that $g_k(n)\ge 3$ (possible: the orbit is strictly increasing). Then
$g_{k+r}(n)=c\,g_k(n)$ is even, and by (a) the parity of the orbit is constant from
$g_k(n)$ on, so $g_k(n)$ is itself even. By (a) again, constant parity propagates
*backwards* as well for indices whose values are $\ge3$: if $g_{j}(n)\ge 3$ then
$g_{j+1}(n)\equiv g_j(n)$, so all orbit values $\ge3$ are even. The only possible orbit
values $<3$ are $1,2$ at the very start; $n=1$ or $2$ leads (a) to a permanently odd
orbit from $3$ on, contradicting evenness; so $n\ge3$, hence $n$ itself is even, and being
even, $n\ge4$. All orbit points are then even by (a).

(c) Immediate from (b): if $c$ were even, $n$ would be even. $\square$

---

## Lemma 4 (witness scaling)

**Lemma 4.** *Suppose $x$ carries $C(x,r,c)$ and $s\ge1$ satisfies
$\operatorname{rad}(s)\mid g_j(x)$ for $0\le j<r$. Then*
$$g_j(sx)=s\,g_j(x)\quad\text{for all } j\ge 0,$$
*and $sx$ carries $C(sx,r,c)$.*

*Proof.* First, $\operatorname{rad}(s)\mid g_j(x)$ for **all** $j\ge0$: for $j<r$ this is
the hypothesis; for $j\ge r$, induction with Theorem 2's $S(j-r)$ gives
$g_j(x)=c\,g_{j-r}(x)$, and $\operatorname{rad}(s)\mid g_{j-r}(x)\mid c\,g_{j-r}(x)$.

Now induct on $j$: $g_0(sx)=sx=s\,g_0(x)$. If $g_j(sx)=s\,g_j(x)$, then since
$\operatorname{rad}(s)\mid g_j(x)$, Lemma 1 gives
$$g_{j+1}(sx)=s\,g_j(x)+\varphi\bigl(s\,g_j(x)\bigr)=s\,g_j(x)+s\,\varphi\bigl(g_j(x)\bigr)=s\,g_{j+1}(x).$$

Certificate for $sx$: $g_r(sx)=s\,g_r(x)=s\,c\,x=c\,(sx)$, and for $0\le j<r$,
$\operatorname{rad}(c)\mid g_j(x)\mid s\,g_j(x)=g_j(sx)$. $\square$

**Example.** $x=10$ carries $C(10,2,2)$ (orbit $10,14,20$), and $\operatorname{rad}(2)=2$
divides $10$ and $14$; so $C(2^l\cdot10,\,2,\,2)$ for all $l\ge0$ — the classical family
$n=2^l\cdot5$. Likewise $s=3$ applied to the odd witness $13857$ (all of whose certificate
orbit points are divisible by $3$) yields the derived witness $41571=3\cdot13857$.

## Lemma 5 (power relations)

**Lemma 5.** *If $x$ carries $C(x,r,c)$, then $x$ carries $C(x,\,jr,\,c^{\,j})$ for every
$j\ge1$.*

*Proof.* By Theorem 2's induction, $S(i)$ and $D(i)$ hold for all $i$. Applying $S$
repeatedly, $g_{jr}(x)=c\,g_{(j-1)r}(x)=\dots=c^{\,j}x$. And
$\operatorname{rad}(c^{\,j})=\operatorname{rad}(c)$ divides $g_i(x)$ for all $i$, in
particular $0\le i<jr$. $\square$

**Example.** $C(4,2,2)$ (orbit $4,6,8$) yields $C(4,2j,2^j)$ for all $j$; the sweep's
raw hits at $(4,r,c)=(4,4,4),(4,6,8),\dots$ are these derived relations.

## Lemma 6 (growth bound)

**Lemma 6.** *If $x$ carries $C(x,r,c)$ and $x$ is even, then $c\le(3/2)^r$. For every
$x$, $c<2^r$.*

*Proof.* Let $x$ be even. If $x=2$: the orbit of $2$ is $2,3,5,\dots$, odd from index
$1$ on by Theorem 3(a), so $g_r(2)$ is odd for $r\ge1$ and can never equal the even
number $2c$; thus no certificate exists at $x=2$ and the claim is vacuous there. If
$x\ge4$, Theorem 3(a) gives that all orbit points are even. For even $m$, writing $m=2^a u$ with $u$ odd, $a\ge1$:
$\varphi(m)=2^{a-1}\varphi(u)\le 2^{a-1}u=m/2$. Hence $g(m)\le\tfrac32 m$ along the orbit
and $c\,x=g_r(x)\le(3/2)^r x$. For general $x\ge2$, $\varphi(m)\le m-1<m$ for $m\ge2$ gives
$g(m)<2m$ along the orbit and $c<2^r$. ($x=1$ is vacuous: certificate condition 2 at
$j=0$ reads $\operatorname{rad}(c)\mid 1$, forcing $c=1<2$, so $x=1$ carries no
certificate.) $\square$

**Remark 6.1.** The bound is sharp in spirit: odd orbits can sustain growth above
$3/2$ per step — e.g. the odd witnesses with $(r,c)=(14,729)$ have
$c^{1/r}=729^{1/14}\approx1.60$ — which is why odd relations reach large $c$ at
moderate $r$.

---

## References

* [ErGr80] P. Erdős and R. L. Graham, *Old and new problems and results in combinatorial
  number theory*, Monographies de L'Enseignement Mathématique 28, Genève (1980), p. 81.
* [St25] Stefan Steinerberger, *On an iterated arithmetic function problem of Erdos and
  Graham*, arXiv:2504.08023 (2025).
* Erdős problems website, problem 411: https://www.erdosproblems.com/411 (page last
  edited 28 October 2025; examples credited there to Selfridge and Weintraub, Weintraub,
  and Cambie).
* C. Hercher, arXiv:2504.19915 (2025) — bounds on the residual branch
  $\varphi(m)=\tfrac23(m+1)$ of the $r=2$ case (not used above; listed for context).
