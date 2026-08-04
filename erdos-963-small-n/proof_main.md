# A verified write-up, with explicit second-order term, of KoishiChan's lower bound for Erdős Problem #963

**Attribution.** The theorem and its method of proof are due to the user **KoishiChan**, who posted
the argument on 05 Dec 2025 in the Erdős Problem #963 forum thread
(https://www.erdosproblems.com/forum/thread/963, capture in `caches/thread963.txt`), incorporating
an off-by-one fix prompted by **Quanyu Tang** (05 Dec 2025) and an optimization suggested in-thread
by **TerenceTao** (05 Dec 2025: "it may be worth removing the hypothesis that $p$ is prime …
making it close to a power of 2 may be more efficient"). Thomas Bloom requested a formal write-up
in-thread on 23 Jan 2026. This document is that write-up (independently produced): our contribution
is verification (see `referee_report.md`), the repairs G1–G3 listed there, the explicit
second-order error term, and one further quantitative refinement (a union bound over only the
needed residue classes, §7), which improves the coefficient of the $(\log_2\log_2 n)^2$ error term
from $\approx 3.99$ (parameters as posted) to $\frac{1}{2\log_2(4/3)} < 1.21$. The asymptotic
result itself is **not** ours.

**Problem** (Erdős #963). Let $f(n)$ be the maximal $k$ such that every $A \subset \mathbb{R}$
with $|A| = n$ contains a *dissociated* subset $B$ of size $k$: all $2^{|B|}$ subset sums
$\sum_{b \in S} b$, $S \subseteq B$, are distinct. Estimate $f(n)$; in particular is
$f(n) \ge \lfloor \log_2 n\rfloor$?

## Main results

**Theorem 1** (KoishiChan, 05 Dec 2025; asymptotic form). $f(n) \ge (1 - o(1))\log_2 n$.

**Theorem 2** (effectivized form). There is a constant $D$, effectively computable from the
implied constant in Montgomery–Vaughan's mean value theorem (Theorem MV below, case $k=2$), such
that for all $n \ge 4$,
$$f(n) \;\ge\; \log_2 n \;-\; 2\,\big(\log_2 \max(\log_2 n, 2)\big)^2 \;-\; D .$$
If the Montgomery–Vaughan constant is $\le 1$ then $D = 362$ suffices.

**Theorem 3** (asymptotically optimal coefficient for this argument). For every $\delta > 0$ there
is $n_0(\delta)$ such that for all $n \ge n_0(\delta)$,
$$f(n) \;\ge\; \log_2 n \;-\; \Big(\tfrac{1}{2\log_2(4/3)} + \delta\Big)(\log_2\log_2 n)^2,
\qquad \tfrac{1}{2\log_2(4/3)} = 1.2047\ldots$$

The only external input is:

**Theorem MV** (H. L. MONTGOMERY AND R. C. VAUGHAN, *Mean values of character sums*, Can. J.
Math. XXXI (1979), no. 3, 476–487, Theorem 1; verified against the paper, `refs/mv1979.pdf`).
*For any real $k > 0$,*
$$\sum_{\chi \ne \chi_0} M(\chi)^{2k} \ll_k \phi(q)\, q^k,$$
*where the summation is over all non-principal characters modulo $q$, and
$M(\chi) = \max_N |\sum_{n=1}^N \chi(n)|$.*
We use only $k = 2$ and write $C_{\mathrm{MV}}$ for an admissible implied constant:
$\sum_{\chi\ne\chi_0} M(\chi)^4 \le C_{\mathrm{MV}}\,\phi(q)\,q^2$. No primality of $q$ is assumed
in Theorem MV (we will use it for prime $q$ only). This is the unique step we take on published
authority rather than reprove.

---

## 1. Preliminaries

All sets are finite. For $B$ a set of reals (or of residues mod $q$), a *signed relation* on $B$
is a vector $\varepsilon \in \{-1, 0, 1\}^B$; it is *nontrivial* if $\varepsilon \ne 0$.

**Lemma 0** (equivalence). $B$ is dissociated (all $2^{|B|}$ subset sums distinct) iff no
nontrivial signed relation satisfies $\sum_{b} \varepsilon_b b = 0$ (in $\mathbb{R}$, resp. in
$\mathbb{Z}/q\mathbb{Z}$).

*Proof.* If $\sigma(S) = \sigma(T)$ with $S \ne T$, then $\varepsilon = \mathbf 1_{S\setminus T} -
\mathbf 1_{T \setminus S}$ is a nontrivial vanishing signed relation ($S\setminus T$ and
$T\setminus S$ are not both empty since $S\neq T$). Conversely if $\sum \varepsilon_b b = 0$
nontrivially, then $S := \{\varepsilon = 1\}$ and $T := \{\varepsilon = -1\}$ are disjoint, not
both empty, with $\sigma(S) = \sigma(T)$, and $S \ne T$. $\blacksquare$

We say $B$ is *dissociated mod $q$* if no nontrivial signed relation vanishes in
$\mathbb{Z}/q\mathbb{Z}$. Write $d(A)$ for the size of the largest dissociated subset of $A$.
Define
$$f_+(N) := \min\{\, d(A) : A \subset \mathbb{Z}_{>0},\ |A| = N \,\}, \qquad
  f_\ne(N) := \min\{\, d(A) : A \subset \mathbb{Z}\setminus\{0\},\ |A| = N \,\}.$$

**Lemma 1** (monotonicity; positivity). $f_+$ and $f_\ne$ are nondecreasing, and
$f_+(N), f_\ne(N) \ge 1$ for $N \ge 1$.

*Proof.* If $|A| = N' \ge N$, any $N$-element subset $A_0 \subseteq A$ satisfies
$d(A) \ge d(A_0) \ge f_+(N)$ (resp. $f_\ne$). Any single nonzero element is dissociated.
$\blacksquare$

## 2. Reduction from $\mathbb{R}$ to nonzero integers

**Lemma 2.** For every $n \ge 2$: $f(n) \ge f_\ne(n-1)$.

*Proof.* Let $A \subset \mathbb{R}$, $|A| = n$. Let $V$ be the $\mathbb{Q}$-span of $A$, a finite
dimensional $\mathbb{Q}$-vector space. For each nontrivial signed relation $\varepsilon$ on $A$
with $v_\varepsilon := \sum_a \varepsilon_a a \ne 0$, the set
$H_\varepsilon := \{T \in V^* : T(v_\varepsilon) = 0\}$ is a proper subspace of the dual $V^*$.
A $\mathbb{Q}$-vector space is never a finite union of proper subspaces, so there is
$T \in V^* \setminus \bigcup_\varepsilon H_\varepsilon$ (a finite union, over
$\varepsilon \in \{-1,0,1\}^A$). Then for every signed relation $\varepsilon$:
$\sum_a \varepsilon_a T(a) = T(v_\varepsilon) = 0 \iff v_\varepsilon = 0$. In particular
(taking $\varepsilon$ supported on two elements) $T$ is injective on $A$, so
$T(A) \subset \mathbb{Q}$ has $n$ elements, and a subset $B \subseteq A$ is dissociated iff
$T(B)$ is. Multiplying by a common denominator (which preserves signed relations) we may take
$T(A) \subset \mathbb{Z}$. At most one element of $T(A)$ is $0$; discard it. The remaining set
$A^\* \subset \mathbb{Z}\setminus\{0\}$ has $\ge n-1$ elements and $d(A) = d(T(A)) \ge d(A^\*)
\ge f_\ne(n-1)$ by Lemma 1 (note $0$ never lies in a dissociated set of size $\ge 1$, so removing
it does not decrease $d$; in any case $d(T(A)) \ge d(A^\*)$ is all we use). $\blacksquare$

*Remark (repairing "WLOG positive").* One cannot in general reduce to **positive** integers:
flipping the sign of one element preserves the family of vanishing signed relations, but if
$\{x, -x\} \subseteq A$ the flipped *set* collapses. The argument below therefore works directly
with nonzero integers; positivity appears only in the recursive calls, where it is automatic.

## 3. Toolbox

Throughout, $q$ denotes an odd prime and elements of $\mathbb{Z}/q\mathbb{Z}$ are identified with
their representatives in $[0, q-1]$.

**Lemma 3** (mod-$q$ transfer). Let $S$ be a set of nonzero integers whose residues mod $q$ are
distinct and nonzero. If the residue set is dissociated mod $q$, then $S$ is dissociated over
$\mathbb{Z}$. *Proof.* A vanishing integer signed relation vanishes mod $q$. $\blacksquare$

**Lemma 4** (small elements: the $\le (q-1)/k$ transport). Let $S \subset [1, \frac{q-1}{k}]$ be a
set of at most $k$ integers, dissociated over $\mathbb{Z}$. Then $S$ is dissociated mod $q$.
*Proof.* For any signed relation, $|\sum_s \varepsilon_s s| \le k \cdot \frac{q-1}{k} = q - 1 < q$,
so vanishing mod $q$ forces vanishing over $\mathbb{Z}$, hence $\varepsilon = 0$. $\blacksquare$

**Lemma 5** (dilation invariance). For $r$ invertible mod $q$, $S$ is dissociated mod $q$ iff
$rS$ is. *Proof.* $\sum \varepsilon_s (rs) = r \sum \varepsilon_s s$ and $r$ is invertible.
$\blacksquare$

**Lemma 6** (splicing). Let $p = 2^m$, $m \ge 1$, and $\Gamma := \{2^0, 2^1, \dots, 2^{m-1}\}$.
Then:
(a) $\Gamma$ is dissociated mod $p$;
(b) if $D'$ is a set of integers all $\equiv 0 \pmod p$, dissociated over $\mathbb{Z}$, and for
each $i \in \Gamma$, $a_i$ is an integer with $a_i \equiv i \pmod p$, then
$D' \cup \{a_i : i \in \Gamma\}$ consists of $|D'| + m$ distinct integers and is dissociated over
$\mathbb{Z}$.

*Proof.* (a) A signed relation on $\Gamma$ has $|\sum_j \varepsilon_j 2^j| \le 2^m - 1 < p$; and a
nonzero signed combination of distinct powers of $2$ is nonzero (its lowest-order nonzero binary
digit survives). So vanishing mod $p$ forces $\varepsilon = 0$.
(b) The elements lie in pairwise distinct residue classes mod $p$ (classes $0$ and the $m$ distinct
classes $i \in \Gamma$, each containing one $a_i$), so they are distinct. Suppose
$\sum_{d \in D'} \varepsilon_d d + \sum_{i\in\Gamma} \varepsilon_i a_i = 0$ over $\mathbb{Z}$.
Reducing mod $p$: $\sum_i \varepsilon_i i \equiv 0 \pmod p$, so $\varepsilon_i = 0$ for all $i$
by (a). Then $\sum_d \varepsilon_d d = 0$ forces $\varepsilon_d = 0$ since $D'$ is dissociated.
$\blacksquare$

## 4. The equidistribution lemma (second moment + Montgomery–Vaughan)

**Lemma 7.** Let $q$ be an odd prime, $\mathcal A \subseteq (\mathbb{Z}/q\mathbb{Z})^*$ with
$|\mathcal A| = N$, and let $B = \{px + u : 1 \le x \le X\} \subseteq (\mathbb{Z}/q\mathbb{Z})^*$
be an arithmetic progression with difference $p$ invertible mod $q$ and length $X \ge 1$. Let $r$
be uniform on $(\mathbb{Z}/q\mathbb{Z})^*$. Then with $C_0 := 48\sqrt{C_{\mathrm{MV}}}$,
$$\mathbb{P}\Big( |r\mathcal A \cap B| \le \tfrac{N X}{2(q-1)} \Big) \;\le\; C_0\, \frac{(q-1)^2}{N^{1/2} X^2}.$$

*Proof.* Write $S_\mathcal{A}(\chi) = \sum_{a \in \mathcal A} \chi(a)$,
$S_B(\chi) = \sum_{b \in B}\chi(b)$, sums over Dirichlet characters mod $q$.

*(i) Mean.* For fixed $a$, $ra$ is uniform on $(\mathbb{Z}/q\mathbb{Z})^*$, so
$\mathbb{E}_r |r\mathcal A \cap B| = \frac{NX}{q-1} =: \mu$.

*(ii) Second moment.* By orthogonality of characters on the group $(\mathbb{Z}/q\mathbb{Z})^*$,
for units $y$: $\mathbf 1_{y = 1} = \frac{1}{q-1}\sum_\chi \chi(y)$. Hence
$|r \mathcal A \cap B| = \frac{1}{q-1} \sum_{a, b} \sum_\chi \chi(r a b^{-1})$, and since
$\mathbb{E}_r\, \chi(r) \chi'(r) = \mathbf 1_{\chi' = \bar\chi}$,
$$\mathbb{E}_r\, |r\mathcal A \cap B|^2
 = \frac{1}{(q-1)^2}\sum_\chi |S_\mathcal{A}(\chi)|^2 |S_B(\chi)|^2
 = \mu^2 + \frac{1}{(q-1)^2}\sum_{\chi \ne \chi_0} |S_\mathcal{A}(\chi)|^2 |S_B(\chi)|^2 .$$
So $\operatorname{Var} = \frac{1}{(q-1)^2}\sum_{\chi\ne\chi_0}|S_\mathcal{A}|^2|S_B|^2$.

*(iii) $B$-sums via $M(\chi)$.* For $\chi \ne \chi_0$, using multiplicativity and
$c := p^{-1} u \bmod q$:
$$S_B(\chi) = \sum_{x=1}^{X} \chi(px + u) = \chi(p) \sum_{x=1}^{X} \chi(x + c)
 = \chi(p)\Big(\sum_{1 \le y \le c + X} \chi(y) - \sum_{1\le y \le c}\chi(y)\Big),$$
where $y$ runs over integers ($\chi$ has period $q$ and $\chi(\text{multiples of } q) = 0$). Each
partial sum has modulus $\le M(\chi)$ — for $\chi \neq \chi_0$ the sum over any complete period
vanishes, so $\max_{R \ge 1}$ equals $\max_{1 \le R < q}$ and is finite. Hence
$|S_B(\chi)| \le 2 M(\chi)$, so by Theorem MV ($k=2$),
$$\sum_{\chi \ne \chi_0} |S_B(\chi)|^4 \le 16 \sum_{\chi\ne\chi_0} M(\chi)^4
 \le 16\, C_{\mathrm{MV}}\, \phi(q)\, q^2 .$$

*(iv) $\mathcal A$-sums.* $\sum_{\text{all } \chi}|S_\mathcal{A}(\chi)|^2 = (q-1) N$ (Parseval /
orthogonality), so
$\sum_{\chi\ne\chi_0}|S_\mathcal{A}(\chi)|^4 \le N^2 \sum_{\chi \neq \chi_0}|S_\mathcal{A}(\chi)|^2 \le (q-1) N^3 \le q N^3$.

*(v) Combine.* By Cauchy–Schwarz,
$$\operatorname{Var} \le \frac{ (q N^3)^{1/2}\,\big(16 C_{\mathrm{MV}} (q-1) q^2\big)^{1/2} }{(q-1)^2}
 = 4 \sqrt{C_{\mathrm{MV}}}\; N^{3/2} \Big(\tfrac{q}{q-1}\Big)^{3/2}
 \le 12 \sqrt{C_{\mathrm{MV}}}\, N^{3/2},$$
using $(q/(q-1))^{3/2} \le (3/2)^{3/2} < 2$ for $q \ge 3$, so in fact
$\operatorname{Var} \le 8\sqrt{C_{\mathrm{MV}}}\, N^{3/2} \le 12\sqrt{C_{\mathrm{MV}}}\,N^{3/2}$.
By Chebyshev,
$$\mathbb{P}(|r\mathcal A\cap B| \le \mu/2) \le \mathbb{P}(\,| |r\mathcal A \cap B| - \mu| \ge \mu/2\,)
 \le \frac{4\operatorname{Var}}{\mu^2}
 \le \frac{48 \sqrt{C_{\mathrm{MV}}}\, N^{3/2} (q-1)^2}{N^2 X^2}
 = C_0 \frac{(q-1)^2}{N^{1/2} X^2}. \;\blacksquare$$

## 5. The dilation step

**Main Lemma.** Let $A$ be a set of $N \ge 256$ distinct **nonzero** integers with
$k := d(A) + 1 \le g := \log_2 N$, and let $m \ge 1$ be an integer satisfying
$$(\star)\qquad (m+1)\, 2^{2m} \;\le\; \frac{N^{1/2}}{8\, C_0\, k^2}, \qquad C_0 = 48\sqrt{C_{\mathrm{MV}}}.$$
Then, with $p := 2^m$ and $N_1 := \lceil N/(4pk) \rceil$,
$$d(A) \;\ge\; m + f_+(N_1).$$

*Proof.* Choose a prime $q \ge \max\big(2\max_{a\in A}|a| + 1,\; 8 p^2 k^2\big)$; $q$ is odd since
$q \ge 32$. Let $\bar A \subset \mathbb{Z}/q\mathbb{Z}$ be the residue set of $A$: its elements
are distinct (differences of elements of $A$ have absolute value $< q$) and nonzero
($0 < |a| < q$), so $\bar A \subseteq (\mathbb{Z}/q\mathbb{Z})^*$ and $|\bar A| = N$.

Set $X := \lfloor \frac{q-1}{pk} \rfloor - 1$ and, for $0 \le i \le p - 1$,
$$B_{p,i} := \{ p x + i \;:\; 1 \le x \le X \}.$$
Since $q - 1 \ge 4pk$ we have $X \ge \frac{q-1}{pk} - 2 \ge \frac{q-1}{2pk} \ge 2$. Every element
of $B_{p, i}$ is an integer in $[1, q-1]$; indeed the largest is
$$pX + i \;\le\; p\Big(\tfrac{q-1}{pk} - 1\Big) + (p - 1) \;=\; \tfrac{q-1}{k} - 1 \;<\; q - 1. \tag{5.1}$$
(This is the off-by-one fix of KoishiChan, prompted by Quanyu Tang: the "$-1$" in the definition
of $X$ is what makes (5.1) hold for every residue $i \le p-1$.) In particular each $B_{p,i}$ is an
AP in $(\mathbb{Z}/q\mathbb{Z})^*$ with difference $p$, invertible mod $q$ (as $q$ is odd).

Let $\Gamma = \{1, 2, \dots, 2^{m-1}\}$ as in Lemma 6 and apply Lemma 7 to each of the $m + 1$
classes $i \in \Gamma \cup \{0\}$, with a union bound: the probability that some such class has
$|r \bar A \cap B_{p,i}| \le \frac{N X}{2(q-1)}$ is at most
$$(m+1)\, C_0 \frac{(q-1)^2}{N^{1/2} X^2}
 \;\le\; (m+1)\, C_0 \frac{4 p^2 k^2}{N^{1/2}}
 \;\le\; \tfrac12 \;<\; 1,$$
using $X \ge \frac{q-1}{2pk}$ and then $(\star)$. Fix an $r \in (\mathbb{Z}/q\mathbb{Z})^*$
for which every class $i \in \Gamma \cup \{0\}$ satisfies
$$|r \bar A \cap B_{p, i}| \;\ge\; \frac{N X}{2(q-1)} \;\ge\; \frac{N}{4 p k} \;\ge\; 1, \tag{5.2}$$
the last inequality because $(\star)$ forces $2^m \le N^{1/4}$, whence
$N / (4pk) \ge N^{3/4}/(4 g) \ge 1$ for $N \ge 256$.

For $i \in \Gamma \cup \{0\}$ let $A'_{p,i} \subset [1, q-1]$ be the set of integer
representatives of $r\bar A \cap B_{p,i}$; these are distinct positive integers, each
$\equiv i \pmod p$ and each $\le \frac{q-1}{k} - 1$ by (5.1). Let $D'$ be a maximum dissociated
subset of $A'_{p, 0}$ and pick $a_i \in A'_{p, i}$ for each $i \in \Gamma$ (possible by (5.2)).

**Claim: $m + |D'| \le d(A)$.** Suppose not: $m + |D'| \ge k = d(A) + 1$. By Lemma 6(b),
$E := D' \cup \{a_i : i \in \Gamma\}$ is dissociated over $\mathbb{Z}$ with $|E| = |D'| + m \ge k$.
Choose $D'' \subseteq E$ with $|D''| = k$. Then:
1. $D''$ is dissociated over $\mathbb{Z}$ (subsets of dissociated sets are dissociated);
2. $D'' \subset [1, \frac{q-1}{k}]$ with $|D''| = k$, so $D''$ is dissociated mod $q$ (Lemma 4);
   its elements are distinct residues (distinct integers in $[1, q-1]$);
3. $r^{-1} D'' \subseteq \bar A$ is dissociated mod $q$ (Lemma 5), so the corresponding
   $k$-element subset $S \subseteq A$ (the residue map is a bijection $A \to \bar A$) is
   dissociated over $\mathbb{Z}$ (Lemma 3).
Thus $d(A) \ge |S| = k = d(A) + 1$, a contradiction; the Claim holds.

Finally, by (5.2), $|A'_{p,0}| \ge N/(4pk)$, so $|A'_{p,0}| \ge N_1$ (an integer at least this
real number is at least its ceiling), and $A'_{p,0} \subset \mathbb{Z}_{>0}$, so Lemma 1 gives
$|D'| = d(A'_{p,0}) \ge f_+(N_1)$. Hence $d(A) \ge m + f_+(N_1)$. $\blacksquare$

## 6. Unrolling: proof of Theorem 2

Let $c_6 := \tfrac12 \log_2(8 C_0)$ and define the threshold
$$g^* := \text{the least } g \ge 205 \text{ such that } \tfrac{g}{20} \ge \tfrac32 \log_2 g + c_6 + 1 .$$
(For $C_{\mathrm{MV}} \le 1$: $C_0 = 48$, $c_6 = \tfrac12\log_2 384 < 4.30$, and $g^* = 361$;
`verify.py --check thresholds` re-computes these numerically.) Set
$$W(g) := 2 \big(\log_2 \max(g, 2)\big)^2, \qquad B(g) := g - W(g) - g^* .$$

**Proposition 6.1.** $f_+(N) \ge B(\log_2 N)$ for every $N \ge 2$.

*Proof.* Strong induction on $N$. Write $g = \log_2 N$.

*Base ($g < g^*$).* $B(g) \le g - g^* < 0 < 1 \le f_+(N)$ by Lemma 1.

*Step ($g \ge g^*$).* Let $A \subset \mathbb{Z}_{>0}$, $|A| = N$, $d(A) = f_+(N)$, and
$k := d(A) + 1$.

Case 1: $k > g$. Then $f_+(N) = k - 1 \ge g - 1 \ge B(g)$ since $W(g) + g^* \ge 1$.

Case 2: $k \le g$. Put
$$m := \Big\lfloor \tfrac{g}{4} - \tfrac32 \log_2 g - c_6 \Big\rfloor .$$
Then $m \ge 1$ (since $\frac{g}{4} - \frac32\log_2 g - c_6 \ge \frac{g}{4} - \frac{g}{20} \cdot
\frac{20}{g}(\frac32\log_2 g + c_6) \ge 1$ by the definition of $g^*$; indeed
$\frac g{20} \ge \frac32\log_2 g + c_6 + 1$ gives $\frac g4 - \frac32 \log_2 g - c_6 \ge
\frac g4 - \frac g{20} + 1 \ge 1$). Condition $(\star)$ holds:
$$(m+1)\,2^{2m} \le g \cdot 2^{\,g/2 - 3\log_2 g - 2c_6} = \frac{g \cdot 2^{g/2}}{g^3\, 8 C_0}
 \le \frac{N^{1/2}}{8 C_0\, g^2} \le \frac{N^{1/2}}{8 C_0 k^2},$$
using $m + 1 \le g$ and $k \le g$. Also $N \ge 2^{g^*} \ge 256$. The Main Lemma yields
$$f_+(N) = d(A) \ge m + f_+(N_1), \qquad N_1 = \lceil N/(4 \cdot 2^m k)\rceil .$$
Bounds on $g_1 := \log_2 N_1$: from $N_1 \ge N/(4\cdot 2^m k)$ and $k \le g$,
$$g_1 \ge g - m - \log_2 k - 2 \ge g - m - \log_2 g - 2 \;(\ge g/2 \ge 2); \tag{6.1}$$
from $N_1 \le N/(4\cdot 2^m k) + 1 \le N/(2^{m+1})$ (as $N/(4\cdot2^mk) \ge 1$ and $4k \ge 4$),
$$g_1 \le g - m - 1 \le \tfrac34 g + \tfrac32 \log_2 g + c_6 \le \tfrac45 g, \tag{6.2}$$
the last step by $\frac{g}{20} \ge \frac32 \log_2 g + c_6$ (definition of $g^*$). Also
$N_1 \le N/2 < N$, so the induction hypothesis applies:
$$f_+(N) \ge m + B(g_1) = m + g_1 - W(g_1) - g^*
 \ge g - (\log_2 g + 2) - W(g_1) - g^*,$$
by (6.1). It remains to check $W(g) \ge W(g_1) + \log_2 g + 2$. Since $W$ is nondecreasing on
$[2, \infty)$ and $2 \le g_1 \le \frac45 g$ by (6.1)–(6.2), it suffices that
$$W(g) - W(\tfrac45 g) = 2\beta\,(2\log_2 g - \beta) \ge \log_2 g + 2, \qquad
 \beta := \log_2 \tfrac54 = 0.32192\ldots$$
i.e. $(4\beta - 1)\log_2 g \ge 2 + 2\beta^2$, i.e. $0.2877\log_2 g \ge 2.2073$, which holds for
$\log_2 g \ge 7.68$, i.e. $g \ge 205$ — true since $g \ge g^\* \ge 205$. (Here we used
$g/2 \ge 2$, so $\log_2 \max(g_1,2)$ is just $\log_2 g_1$, and $W(\frac45 g)$ expands as stated.)
Hence $f_+(N) \ge g - W(g) - g^* = B(g)$. $\blacksquare$

**Proposition 6.2.** $f_\ne(N) \ge B(\log_2 N)$ for every $N \ge 2$.

*Proof.* For $g < g^*$, as before. For $g \ge g^*$: let $A$ be nonzero integers, $|A| = N$,
$d(A) = f_\ne(N)$. Case 1 as before. In Case 2 the Main Lemma applies verbatim to $A$
(it assumes only nonzero integers) and its recursive call is to $f_+$ (the lifted set is
positive), so $f_\ne(N) \ge m + f_+(N_1) \ge m + B(g_1) \ge B(g)$ by Proposition 6.1 and the same
estimates. $\blacksquare$

**Proof of Theorem 2.** Let $n \ge 4$ and $A \subset \mathbb{R}$, $|A| = n$. By Lemma 2 and
Proposition 6.2,
$$d(A) \ge f_\ne(n - 1) \ge \log_2(n-1) - 2\big(\log_2\max(\log_2 (n-1), 2)\big)^2 - g^*
 \ge \log_2 n - 2\big(\log_2\max(\log_2 n, 2)\big)^2 - (g^* + 1),$$
using $\log_2(n-1) \ge \log_2 n - 1$ for $n \ge 2$ and monotonicity of the subtracted terms.
Take $D := g^* + 1$; for $C_{\mathrm{MV}} \le 1$, $D = 362$. $\blacksquare$

**Proof of Theorem 1 and Theorem 3.** Theorem 1 is immediate from Theorem 2. For Theorem 3, rerun
§6 with $W(g) = C (\log_2 g)^2$: (6.2) gives $g_1 \le (\frac34 + \delta') g$ for any fixed
$\delta' > 0$ once $g \ge g^*(\delta')$, and the step inequality becomes
$C\,\beta_{\delta'}(2 \log_2 g - \beta_{\delta'}) \ge \log_2 g + 2$ with
$\beta_{\delta'} = \log_2 \frac{1}{3/4 + \delta'}$, which holds for large $g$ whenever
$2C\beta_{\delta'} > 1$, i.e. $C > \frac{1}{2\beta_{\delta'}} = \frac{1}{2\log_2(1/(3/4+\delta'))}$. As
$\delta' \to 0$ this tends to $\frac{1}{2\log_2(4/3)}$. Choosing $\delta'$ small enough that
$\frac{1}{2\log_2(1/(3/4+\delta'))} \le \frac{1}{2\log_2(4/3)} + \delta/2$, and absorbing the
additive constant $g^*(\delta') + 1$ into the $(\log_2\log_2 n)^2$ term for
$n \ge n_0(\delta)$, we conclude. $\blacksquare$

## 7. Remarks on the constants and on the original argument

1. **What the post proves as posted.** KoishiChan's parameters ($p$ prime in
   $[n^{1/12}/2, n^{1/12}]$, the lemma packaged with $|\mathcal A| \ge L^{10}$,
   $|B| \ge q/L$, $L = pk+1$, and a union bound over **all** $p$ residue classes) give the
   recursion ratio $\frac{11}{12}$ and hence, by the computation of §6 with
   $\beta = \log_2\frac{12}{11}$, the explicit form
   $f(n) \ge \log_2 n - (\frac{1}{2\log_2(12/11)} + o(1))(\log_2\log_2 n)^2$ with
   $\frac{1}{2\log_2(12/11)} = 3.9827\ldots$ — already $\log_2 n - O((\log\log n)^2)$. Nothing in
   our sharpening changes the skeleton.
2. **Where the improvement to $1.2047\ldots$ comes from.** Two changes: (i) Tao's in-thread
   suggestion $p = 2^m$ (primality of $p$ is nowhere used; a power of two makes
   $|\Gamma| = \log_2 p$ exactly); (ii) the union bound is needed only over the $m + 1$ classes
   $\Gamma \cup \{0\}$ actually consumed by the splicing — not all $p$ classes. With the
   second-moment lemma stated tightly (Lemma 7), the binding constraint becomes
   $(m+1) p^2 k^2 \lesssim N^{1/2}$, allowing $p \approx N^{1/4 - o(1)}$ and ratio
   $\frac34 + o(1)$. (With all-$p$-classes union bounding one gets $p^3 k^2 \lesssim N^{1/2}$,
   ratio $\frac56$, constant $\frac{1}{2\log_2(6/5)} = 1.9004\ldots$ — still better than
   $n^{1/12}$, which the $L^{10}$ packaging forces.)
3. **Limit of the method.** Chebyshev with the MV fourth moment caps $p$ near $N^{1/4}$. Higher
   moments of $M(\chi)$ (Theorem MV holds for all $k$) with higher-moment bounds for
   $S_{\mathcal A}$ would push $p$ toward $N^{1/2 - \varepsilon}$ and the constant toward
   $\frac{1}{2\log_2 2} = \frac12$, at the price of messier bookkeeping; and any argument giving
   $p = N^{1 - o(1)}$ would make the error term $O(\log\log n \cdot \log\log\log n)$-ish. We have
   not pursued this. The floor conjecture $f(n) \ge \lfloor \log_2 n \rfloor$ for **all** $n$
   remains open: this argument's error term has the wrong sign, and for it one needs a loss-free
   recursion or a different idea.
4. **Effectivity.** The only ineffective-as-quoted constant is $C_{\mathrm{MV}}$; the
   Montgomery–Vaughan proof is elementary Fourier analysis (Pólya's expansion) plus finite
   lemmata and is effective in principle, so $D$ in Theorem 2 is effectively computable. Every
   other constant above is explicit.
5. **$q$ need not be almost anything.** Tao also suggested relaxing $q$ to almost-primes; since
   $q$ is a free auxiliary parameter with no upper constraint, primality of $q$ costs nothing
   here, and we keep it (it makes $(\mathbb{Z}/q\mathbb{Z})^*$ cyclic of order $q-1$ and every
   nonzero residue invertible — used in Lemmas 3–5 and 7).
6. **Upper bound side.** $f(n) \le d(\{1,\dots,n\})$, and $d(\{1, \dots, n\})$ is precisely the
   maximum size of a distinct-subset-sums subset of $[n]$ — the quantity of Erdős Problem #1. See
   `proof_upper_reduction.md` for the reduction remark and a proof that separated multi-scale
   constructions cannot improve the upper bound.

## Machine checks

`verify.sh` re-runs, from scratch: (a) exact verification of the orthogonality identity of
Lemma 7(ii) at $q = 61, 101$ against brute-force enumeration over all $r$ (independent
implementation via primitive roots); (b) the bound $|S_B(\chi)| \le 2M(\chi)$ for random
difference-$p$ APs, all $\chi \ne \chi_0$; (c) randomized brute-force verification of Lemma 6
(splicing) and Lemma 4 (transport) instances by exhaustive signed-sum enumeration; (d) numerical
verification of the §6 bookkeeping: the exact worst-case recursion trace satisfies
$\sum_j m_j \ge g - 2(\log_2 g)^2 - g^*$ for $g$ up to $10^6$, and the fitted coefficient
approaches $\approx 1.2$; (e) the numerical thresholds claimed in §6.
