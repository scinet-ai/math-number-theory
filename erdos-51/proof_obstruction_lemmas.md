# Obstruction lemmas for Erdős #51: what a large ratio $n_a/a$ forces

Setting as in `proof_ratio2_family.md`: $V=\varphi(\mathbb{N})$, and for $a\in V$,
$f(a)=n_a=\min\varphi^{-1}(a)$. Throughout, $p_j$ is the $j$-th prime,
$R(m)=\prod_{j\le m}\frac{p_j}{p_j-1}$, $\omega_{\mathrm{odd}}(n)$ is the number of
distinct odd prime divisors of $n$, and $v_2$ is the 2-adic valuation.

These lemmas quantify *why* the ratio grows glacially in the data (certified max $2.0434$
over all totient values $a\le3.06\times10^{10}$, `computation.md`): a totient value with
ratio $\ge K$ is forced to have huge 2-adic valuation and all its preimages must be
divisible by many odd primes.

---

## Lemma 1 (transfer to every preimage)

If $a\in V$ and $f(a)\ge Ka$, then **every** $n$ with $\varphi(n)=a$ satisfies
$$\frac{n}{\varphi(n)}\;=\;\prod_{p\mid n}\frac{p}{p-1}\;\ge\;K .$$

*Proof.* $n\ge f(a)\ge Ka=K\varphi(n)$, and $n/\varphi(n)=\prod_{p\mid n}\frac{p}{p-1}$
by the product formula $\varphi(n)=n\prod_{p\mid n}(1-1/p)$. $\square$

(So obstructions proved for "every preimage" below follow from a lower bound on the
*minimal* one — the ratio $f(a)/a$ is inherited, as a lower bound, by the whole fiber.)

## Lemma 2 (initial-segment domination)

For every $n\ge1$ with $\omega(n)=m$ distinct prime factors,
$$\frac{n}{\varphi(n)}\;\le\;R(m)\;=\;\prod_{j\le m}\frac{p_j}{p_j-1}.$$

*Proof.* If $q_1<\dots<q_m$ are the primes dividing $n$ then $q_j\ge p_j$, and
$x\mapsto x/(x-1)$ is decreasing, so termwise $\frac{q_j}{q_j-1}\le\frac{p_j}{p_j-1}$.
$\square$

Numerically $R(1),R(2),\dots=2,\ 3,\ 3.75,\ 4.375,\ 4.8125,\ 5.2135,\ 5.5394,\ 5.8471,\
6.1129,\ 6.3312,\ 6.5423,\dots$ Consequently, e.g.: a totient value with ratio
$K>R(10)=6.3313$ would need every preimage to have $\ge11$ distinct primes, hence every
preimage $\ge 31\#=200560490130$.

## Lemma 3 (2-adic valuation)

For every $n$, $\;v_2(\varphi(n))\;\ge\;\omega_{\mathrm{odd}}(n)+\bigl(v_2(n)-1\bigr)^+\;\ge\;\omega_{\mathrm{odd}}(n)$.

*Proof.* $\varphi$ is multiplicative; each odd prime power $p^e\Vert n$ contributes
$p^{e-1}(p-1)$ with $v_2(p-1)\ge1$; the factor $2^{v_2(n)}$ contributes $v_2(n)-1$ when
$v_2(n)\ge1$. $\square$

## Theorem 4 (elementary explicit obstruction — fully self-contained)

Let $a\in V$ with $f(a)/a\ge K$. Then every preimage $n$ of $a$ satisfies
$$\omega_{\mathrm{odd}}(n)\;\ge\;\frac{K^2-4}{8},\qquad\text{and hence}\qquad
v_2(a)\;\ge\;\frac{K^2-4}{8}.$$
Equivalently, for **every** totient value $a$:
$$\boxed{\ \frac{f(a)}{a}\;\le\;2\sqrt{2\,v_2(a)+1}\ }$$

*Proof.* Let $r=\omega_{\mathrm{odd}}(n)$ with odd prime divisors $q_1<\dots<q_r$. Since
the $t$-th smallest odd prime is at least the $t$-th odd number $\ge3$, $q_t\ge 2t+1$, so
$\frac{q_t}{q_t-1}=1+\frac{1}{q_t-1}\le1+\frac{1}{2t}$. Hence
$$\frac{n}{\varphi(n)}\;\le\;2\prod_{t=1}^{r}\Bigl(1+\frac1{2t}\Bigr)
\;=\;2\,\frac{(2r+1)!!}{(2r)!!}\;\le\;2\sqrt{2r+1},$$
where the last inequality is proved by induction: it holds at $r=0$ ($1\le1$), and
$\sqrt{2r+1}\cdot\frac{2r+3}{2r+2}\le\sqrt{2r+3}$ amounts to
$(2r+1)(2r+3)=(2r+2)^2-1\le(2r+2)^2$. By Lemma 1, $K\le 2\sqrt{2r+1}$, i.e.
$r\ge(K^2-4)/8$. Lemma 3 transfers this to $v_2(a)$ (taking $n=f(a)$, or any preimage).
Solving $K\le2\sqrt{2v_2(a)+1}$ for $K=f(a)/a$ gives the boxed bound. (For $v_2(a)=0$,
i.e. $a=1$, $f(1)=1$ and the bound reads $1\le2$.) $\square$

**Corollary 4.1 (a YES-family needs exploding 2-adic valuation).** If $A\subseteq V$ is
any family along which $n_a/a\to\infty$ (what Erdős \#51 asks for), then $v_2(a)\to\infty$
along $A$, at rate at least $v_2(a)\ge\bigl((n_a/a)^2-4\bigr)/8$. In particular:

* totient values $a\equiv 2\pmod 4$ have $f(a)/a\le 2\sqrt3<3.47$;
* more generally any subfamily of $V$ with bounded $v_2$ has bounded ratio, so \#51
  cannot be witnessed there. (Compare: the exact-ratio-2 family of
  `proof_ratio2_family.md` has $a=2^k$, $v_2(a)=k\to\infty$ — necessary, by this
  corollary, for its ratio even to approach the *constant* 2... consistent, since
  $2\sqrt{2k+1}\gg2$.)

**Remark.** Theorem 4 is deliberately proved from nothing (no prime number theorem, no
Mertens). Its $K^2$ growth is far from optimal; the true forcing is exponential —
Theorem 5 — but that needs prime-counting input.

## Theorem 5 (sharp obstruction: exponential forcing)

Let $a\in V$ with $f(a)/a\ge K$ and let $n$ be any preimage of $a$.

**(i) Asymptotic form (Mertens).** As $K\to\infty$,
$$\omega_{\mathrm{odd}}(n)\;\ge\;\exp\Bigl(\bigl(e^{-\gamma}-o(1)\bigr)K\Bigr),
\qquad e^{-\gamma}=0.56145\ldots$$
and the same lower bound holds for $v_2(a)$.

**(ii) Explicit form (Rosser–Schoenfeld).** If $K>10.226$ then, with $r=\omega_{\mathrm{odd}}(n)$,
$$r\;\ge\;\frac{e^{0.5526\,K}}{0.5526\,K}\;-\;1,$$
and hence the same for $v_2(a)$.

*Proof.* Let $m=\omega(n)\le r+1$. By Lemmas 1–2, $K\le R(r+1)=\prod_{p\le p_{r+1}}\frac{p}{p-1}$.

(i) Mertens' third theorem gives $R(r+1)=e^{\gamma}\ln(p_{r+1})(1+o(1))$, so
$\ln p_{r+1}\ge(e^{-\gamma}-o(1))K$. By Chebyshev, $r+1=\pi(p_{r+1})\gg p_{r+1}/\ln p_{r+1}$,
so $r\ge\exp((e^{-\gamma}-o(1))K)$ after absorbing the polynomial factors into the $o(1)$.
Lemma 3 transfers to $v_2(a)$.

(ii) We use the explicit Mertens-product bound of Rosser and Schoenfeld [RS62, §3,
formulas (3.29)–(3.30)]: for $x\ge285$,
$$\prod_{p\le x}\Bigl(1-\frac1p\Bigr)^{-1}\;<\;\frac{e^{\gamma}\ln x}{1-\frac{1}{2\ln^2x}}\,.$$
A direct computation gives $\prod_{p\le283}\frac{p}{p-1}=10.2257\ldots$; so $K>10.226$
forces $p_{r+1}\ge293>285$. Then
$$K\;\le\;\prod_{p\le p_{r+1}}\frac{p}{p-1}\;<\;\frac{e^{\gamma}}{1-\frac{1}{2\ln^2 285}}\,\ln p_{r+1}
\;=\;1.80939\ldots\cdot\ln p_{r+1},$$
(the prefactor is decreasing in $x$, so its value at $285$ is an upper bound), giving
$\ln p_{r+1}>K/1.8094>0.5526\,K$. Finally $\pi(x)>x/\ln x$ for $x\ge17$ [RS62, (3.5)],
and $x\mapsto x/\ln x$ is increasing for $x\ge e$, so
$$r+1\;=\;\pi(p_{r+1})\;>\;\frac{p_{r+1}}{\ln p_{r+1}}\;>\;\frac{e^{0.5526K}}{0.5526\,K}. \qquad\square$$

**FIXME-grade caveat, disclosed.** The exact numbered form of the [RS62] product
inequality was checked against secondary sources (the statement above matches the form
quoted in the literature, e.g. Integers 20 (2020) \#A103, "An improved inequality of
Rosser and Schoenfeld", and arXiv:1703.08032), but we did not re-derive it; the validity
threshold $x\ge285$ for the upper-bound direction is taken on citation. Theorem 4 and
Theorem 5(i) are independent of this and fully safe; only the specific constants
$(0.5526,\ 10.226)$ in 5(ii) lean on [RS62].

## Proposition 6 (upper bound: the ratio can't exceed $\sim e^{\gamma}\log\log a$ — known)

For $a\in V$,
$$\frac{f(a)}{a}\;\le\;\bigl(e^{\gamma}+o(1)\bigr)\ln\ln a .$$
This is the trivial upper bound for \#51 (no novelty claimed; it is the same mechanism as
the upper bound in the solved neighbour problem \#694), recorded here with proof for
completeness.

*Proof.* Write $n=f(a)$, $m=\omega(n)$. Then $n\ge\prod_{j\le m}p_j$, so by Chebyshev
($\theta(x)\gg x$, indeed $\theta(p_m)=\sum_{j\le m}\ln p_j\le\ln n$ and
$\theta(x)>cx$ for $x\ge2$ with an absolute $c>0$), $p_m\le c^{-1}\ln n$. By Lemma 2 and
Mertens, $$\frac{f(a)}{a}=\frac{n}{\varphi(n)}\le R(m)=e^{\gamma}(1+o(1))\ln p_m\le
(e^{\gamma}+o(1))\ln\ln n .$$
It remains to replace $n$ by $a$: since $\varphi(n)\ge\sqrt{n/2}$ for all $n$ (check on
prime powers: $\varphi(p^e)=p^{e-1}(p-1)\ge p^{e/2}$ for $p$ odd and for $p=2,e\ge2$,
with a single factor $\sqrt2$ lost at $p^e=2$), $n\le 2a^2$, so
$\ln\ln n\le\ln(2\ln a+\ln 2)=\ln\ln a+O(1)$, absorbed into $o(1)\ln\ln a$. $\square$

**Corollary 6.1 (shape of any hypothetical YES-family, and why the chain is tight).**
Along any family with $n_a/a\to\infty$, combine Theorem 5(ii) with the trivial
$v_2(a)\le\log_2 a$: from $e^{0.5526K}/(0.5526K)-1\le v_2(a)\le\log_2 a$ (with
$K=n_a/a$) one gets, after taking logarithms,
$$\frac{n_a}{a}\;\le\;1.8094\,\ln\ln a\;+\;O(\ln\ln\ln a).$$
So the $v_2$-obstruction *alone* already recovers the doubly-logarithmic upper bound of
Proposition 6 with constant $1.8094$ instead of the optimal $e^{\gamma}=1.7811$ — the
obstruction chain is tight against the trivial upper bound to within $1.6\%$. This makes
precise why \#51 resists elementary attacks from this direction: any YES-family must ride
the extreme edge $v_2(a)=(\log a)^{1-o(1)}$ (nearly all of $a$ a power of $2$), exactly
the regime of the rigid families in `proof_ratio2_family.md`, where ratios are capped at
$2$ by Fermat-number compositeness.

## References

* [RS62] J. B. Rosser, L. Schoenfeld, *Approximate formulas for some functions of prime
  numbers*, Illinois J. Math. 6 (1962), 64–94. (Explicit Mertens product bounds, (3.29)–(3.30);
  $\pi(x)>x/\ln x$ for $x\ge17$, (3.5).)
* C. Axler, *New estimates for some functions defined over primes*, arXiv:1703.08032
  (secondary confirmation of the [RS62] product inequality).
* *An improved inequality of Rosser and Schoenfeld*, Integers 20 (2020), \#A103,
  math.colgate.edu/~integers/u103/u103.pdf (secondary confirmation; cited by title and
  report number — author name not copied because it was not legible in the retrieved copy).
* Mertens' third theorem and Chebyshev bounds: any standard text (e.g. Hardy–Wright).
