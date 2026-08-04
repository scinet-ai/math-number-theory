# The collinear-roots case of Erdős problem #1041 (Erdős–Herzog–Piranian path problem)

**Claim proved here.** Let $n \ge 2$ and let $f(z) = \prod_{j=1}^n (z - z_j)$ be monic of degree
$n$ with all roots in the open unit disk $\mathbb{D} = \{|z|<1\}$, and suppose all roots lie on a
common line $\ell \subset \mathbb{C}$ (in particular this covers every real-rooted $f$). Then two
roots of $f$ (counted with multiplicity) are joined inside $E(f) := \{z : |f(z)| < 1\}$ by a
possibly degenerate straight segment of length $< 2$. If the roots are distinct the segment is
nondegenerate and joins a pair of *consecutive* roots on $\ell$, and we get the quantitative bound

$$\min_{1 \le i \le n-1}\; \max_{z \in [z_i, z_{i+1}]} |f(z)| \;\le\; \left(\frac{\Delta}{n^n}\right)^{1/(n-1)} \;<\; 1, \qquad \Delta := \prod_{i<j} |z_i - z_j|^2 .$$

The degenerate (0-length) convention for repeated roots is the one accepted in the literature on
this problem: Venkata Siddharth Pendyala's degree-four theorem (arXiv:2606.24875) is stated for a
"possibly degenerate polygonal path", and the qualitative Erdős–Herzog–Piranian statement counts
zeros with multiplicity. Note the convention is *forced*: for $f(z) = z^n$ all roots coincide, so
no nondegenerate pair exists at all.

Throughout, $[a,b]$ denotes the straight segment $\{(1-t)a + tb : t \in [0,1]\}$.

---

## Lemma 1 (Reduction to a real polynomial on a chord)

*Let $\ell$ be a line meeting $\mathbb{D}$, written $\ell = \{a + tu : t \in \mathbb{R}\}$ with
$u$ a unit vector and $a \perp u$ (i.e. $a$ is the foot of the perpendicular from $0$ to $\ell$,
so $\operatorname{Re}(\bar a u) = 0$). Then:*

1. *$\ell \cap \mathbb{D} = \{a + tu : t \in (-h, h)\}$ with $h = \sqrt{1 - |a|^2} \in (0, 1]$;
   in particular the chord $\ell\cap\mathbb{D}$ has length $2h \le 2$.*
2. *If all roots of $f$ lie on $\ell$, say $z_j = a + t_j u$, then for every $t \in \mathbb{R}$,
   $|f(a + tu)| = |P(t)|$ where $P(t) := \prod_{j=1}^n (t - t_j)$ is a monic real polynomial,
   and all $t_j \in (-h, h)$.*

**Proof.** (1) $|a + tu|^2 = |a|^2 + t^2 + 2t\operatorname{Re}(\bar a u) = |a|^2 + t^2$, so
$a + tu \in \mathbb{D}$ iff $t^2 < 1 - |a|^2$. Since the roots lie on $\ell \cap \mathbb{D}$,
this set is nonempty, so $|a| < 1$ and $h \in (0,1]$.

(2) $f(a + tu) = \prod_j \big((a + tu) - (a + t_j u)\big) = \prod_j u\,(t - t_j) = u^n P(t)$,
and $|u| = 1$. Each root satisfies $z_j \in \mathbb{D}$, so by (1), $t_j \in (-h,h)$. $\blacksquare$

Note that under this correspondence the segment $[z_i, z_j]$ on $\ell$ has length exactly
$|t_i - t_j|$, and $|f|$ on it equals $|P|$ on $[t_i, t_j]$.

## Lemma 2 (Interlacing and unimodality on gaps)

*Let $P$ be monic of degree $n \ge 2$ with distinct real roots $t_1 < \cdots < t_n$. Then $P'$
has exactly one root $y_i$ in each open gap $(t_i, t_{i+1})$, $i = 1, \dots, n-1$, these are all
the roots of $P'$, each is simple, and*

$$\max_{t \in [t_i, t_{i+1}]} |P(t)| = |P(y_i)|.$$

**Proof.** By Rolle's theorem $P'$ has at least one root in each of the $n-1$ gaps; since
$\deg P' = n - 1$ it has exactly one per gap, each simple, and no others. Fix $i$. On the open
gap $(t_i, t_{i+1})$, $P$ has no roots, so $P$ has constant sign $\sigma_i \in \{\pm 1\}$ there;
set $g := \sigma_i P \ge 0$ on $[t_i, t_{i+1}]$, with $g(t_i) = g(t_{i+1}) = 0$ and $g > 0$
inside. The maximum of $g$ on the compact gap is positive, hence attained at an interior point,
which must be a critical point of $g$, i.e. equal to $y_i$. Thus
$\max |P| = g(y_i) = |P(y_i)|$. $\blacksquare$

## Lemma 3 (Product of critical values equals $|\mathrm{disc}|/n^n$)

*With $P$, $t_j$, $y_i$ as in Lemma 2, and $\operatorname{disc}(P) := \prod_{i<j}(t_j - t_i)^2$,*

$$\prod_{i=1}^{n-1} |P(y_i)| \;=\; \frac{\operatorname{disc}(P)}{n^n}.$$

**Proof.** Since $P(t) = \prod_j (t - t_j)$, we have $P'(t_j) = \prod_{k \ne j}(t_j - t_k)$, so

$$\prod_{j=1}^{n} P'(t_j) = \prod_{j=1}^n \prod_{k \ne j} (t_j - t_k)
= \prod_{j < k} (t_j - t_k)(t_k - t_j) = (-1)^{n(n-1)/2} \operatorname{disc}(P). \tag{3.1}$$

On the other hand $P'$ is a degree-$(n-1)$ polynomial with leading coefficient $n$ and roots
$y_1, \dots, y_{n-1}$, i.e. $P'(t) = n \prod_{i=1}^{n-1} (t - y_i)$. Hence

$$\prod_{j=1}^{n} P'(t_j) = n^n \prod_{j=1}^n \prod_{i=1}^{n-1} (t_j - y_i)
= n^n \prod_{i=1}^{n-1} \Big[ (-1)^n \prod_{j=1}^n (y_i - t_j) \Big]
= n^n (-1)^{n(n-1)} \prod_{i=1}^{n-1} P(y_i). \tag{3.2}$$

Since $n(n-1)$ is even, $(-1)^{n(n-1)} = 1$. Taking absolute values in (3.1) = (3.2) gives the
claim. $\blacksquare$

## Lemma 4 (Discriminant of points in the open chord: Hadamard bound)

*Let $n \ge 2$ and let $x_1, \dots, x_n$ be distinct reals with $|x_i| < 1$ for all $i$. Then*

$$\operatorname{disc} := \prod_{i<j} (x_j - x_i)^2 \;<\; n^n.$$

**Proof.** Let $M$ be the $n \times n$ Vandermonde matrix $M_{ij} = x_i^{\,j-1}$
($i, j = 1, \dots, n$). Then $\det M = \prod_{i<j}(x_j - x_i)$, so
$\operatorname{disc} = (\det M)^2$. By Hadamard's inequality (see e.g. Horn & Johnson,
*Matrix Analysis*, 2nd ed., Cor. 7.8.3: $|\det M| \le \prod_i \|\text{row}_i\|_2$),

$$|\det M| \;\le\; \prod_{i=1}^n \Big( \sum_{k=0}^{n-1} x_i^{2k} \Big)^{1/2}.$$

For each $i$, since $|x_i| < 1$ and $n \ge 2$: $\sum_{k=0}^{n-1} x_i^{2k} = 1 + x_i^2 + \cdots
+ x_i^{2(n-1)} < n$ (the $k \ge 1$ terms are each $< 1$). Hence $|\det M| < n^{n/2}$ strictly,
and $\operatorname{disc} < n^n$. $\blacksquare$

**Remark.** Both the constant and the strictness are exactly right: for $n = 2$,
$x_{1,2} = \pm(1-\varepsilon)$ gives $\operatorname{disc} \to 4 = 2^2$, matching the tightness
of the whole conjecture on $f = z^2 - a^2$, $a \to 1^-$. The strict inequality is precisely
where the hypothesis "roots in the **open** unit disk" enters.

## Theorem (Collinear-roots case of #1041)

*Let $n \ge 2$ and let $f$ be monic of degree $n$ with all roots in $\mathbb{D}$ lying on a
common line $\ell$. Then two roots of $f$ (with multiplicity) are joined by a straight segment
of length $< 2$ contained in $E(f) = \{|f| < 1\}$. Precisely:*

* *if $f$ has a repeated root $z_0$, the degenerate segment $\{z_0\}$ joins two coincident
  roots and has length $0$;*
* *if the roots $z_1, \dots, z_n$ are distinct, ordered along $\ell$, there is an index $i$
  such that the closed segment $[z_i, z_{i+1}]$ lies in $E(f)$ and has length $< 2$; moreover*

$$\min_{1 \le i \le n-1} \max_{z \in [z_i, z_{i+1}]} |f(z)|
\;\le\; \left( \frac{\operatorname{disc}}{n^n} \right)^{1/(n-1)} < 1,
\qquad \operatorname{disc} = \prod_{i<j} |z_i - z_j|^2 .$$

**Proof.** If $f$ has a repeated root $z_0$, then $z_0 \in E(f)$ (as $f(z_0) = 0$), and the
constant path at $z_0$ joins two coincident roots; done. So assume the roots are distinct.

Apply Lemma 1: write $z_j = a + t_j u$ with $t_1 < \cdots < t_n$ in $(-h, h)$, $h \le 1$, and
$|f(a + tu)| = |P(t)|$, $P(t) = \prod (t - t_j)$ monic real with distinct roots. Note
$\operatorname{disc}(P) = \prod_{i<j}(t_j - t_i)^2 = \prod_{i<j} |z_i - z_j|^2 =
\operatorname{disc}$, since $|z_i - z_j| = |t_i - t_j|$.

By Lemma 2 the critical points $y_1 < \cdots < y_{n-1}$ of $P$ interlace the $t_i$ and
$\max_{[t_i, t_{i+1}]} |P| = |P(y_i)|$. By Lemma 3 and then Lemma 4 (applicable since
$t_j \in (-h,h) \subseteq (-1,1)$),

$$\prod_{i=1}^{n-1} |P(y_i)| = \frac{\operatorname{disc}}{n^n} < 1 .$$

A product of $n - 1$ positive numbers being $< 1$ forces its minimum factor to be $< 1$;
more precisely $\min_i |P(y_i)| \le \big(\prod_i |P(y_i)|\big)^{1/(n-1)} =
(\operatorname{disc}/n^n)^{1/(n-1)} < 1$. Choose $i$ attaining the minimum. Then for every
$t \in [t_i, t_{i+1}]$: $|f(a+tu)| = |P(t)| \le |P(y_i)| < 1$ (interior points, by Lemma 2)
while at the endpoints $f = 0$. Hence the closed segment $[z_i, z_{i+1}] \subset E(f)$.

Its length is $t_{i+1} - t_i < 2h \le 2$ (both endpoints lie in the open interval $(-h,h)$);
alternatively, any two points of the open unit disk are at distance $< 2$. $\blacksquare$

---

## Remarks

**R1 (real-rooted case).** Taking $\ell = \mathbb{R}$: every monic real-rooted polynomial with
roots in $(-1,1)$ has a pair of consecutive roots joined by the straight segment between them
inside $E(f)$, with $\max$ of $|f|$ on that segment at most
$(\operatorname{disc}/n^n)^{1/(n-1)}$.

**R2 (sharpness).** For $f = z^2 - a^2$ with $a \to 1^-$, the unique gap has
$\max |f| = a^2 \to 1$ and segment length $2a \to 2$: neither the sub-level threshold $1$ nor
the length bound $2$ can be improved, even in the collinear class. The theorem's bound gives
$\max |f| \le \operatorname{disc}/4 = (2a)^2/4 = a^2$ — exact in this family.

**R3 (quantitative decay).** The Hadamard step is generous for $n \ge 3$: the sharp maximum
$\Delta_n$ of $\operatorname{disc}$ over $[-1,1]$ (attained at the Fekete points, classically
studied by Stieltjes and I. Schur (1918)) satisfies $\Delta_n / n^n \to 0$ superexponentially
(numerically $0.148$ at $n = 3$, $5\times 10^{-3}$ at $n=4$, $\sim 10^{-24}$ at $n = 10$), so
the best gap actually satisfies $\max |f| \le (\Delta_n/n^n)^{1/(n-1)} \to 0$. We do not need
this refinement and do not prove it here; Lemma 4 suffices and is self-contained.

**R4 (why "on the line" and not just "symmetric about a line").** The factorization
$f(a + tu) = u^n P(t)$ in Lemma 1 needs every root on $\ell$. If instead $f$ merely has
conjugate-symmetric roots (e.g. real coefficients with some non-real roots), the restriction of
$|f|$ to $\mathbb{R}$ is $\prod_{\text{real roots}} |t - t_j| \cdot \prod_{\text{pairs}}
((t-\alpha_k)^2 + \beta_k^2)$, the critical-value product identity for the real-root gaps fails
in general, and the question remains open in that class. We flag this explicitly as *not*
covered by the present theorem.

**R5 (repeated roots with at least two distinct values).** When $f$ has a repeated root the
theorem uses the accepted degenerate convention. If one insists on a nondegenerate pair
whenever $f$ has at least $p \ge 2$ distinct root values $s_1 < \cdots < s_p$ (multiplicities
$m_q$), the gap-critical-value machinery still gives exactly one critical point $y_i$ per gap
(the other $n - p$ critical points sit at the repeated roots, where $P$ vanishes), and the
Lemma 3 identity degenerates to $0 = 0$. A weighted version (with
$\prod_{q<r}|s_q - s_r|^{2 m_q m_r}$ in place of the discriminant) appears to exist in the
$\varepsilon \to 0$ cluster limit, but we have not proved it; this is left as an explicitly
open refinement. It is not needed for the theorem as stated (nor for the problem's accepted
formalization, which counts roots with multiplicity).

## Attribution and context

- The problem is Erdős problem #1041, from P. Erdős, F. Herzog, G. Piranian, *Metric
  properties of polynomials*, J. Analyse Math. 6 (1958), 125–148; they proved some component
  of $E(f)$ contains at least two roots.
- The degree-four case (all root configurations, not just collinear) was proved by
  **Venkata Siddharth Pendyala**, *A Degree-Four Lemniscate Path Theorem*, arXiv:2606.24875
  (June 2026); the same author's arXiv:2606.19178 treats origin-to-boundary path lengths in
  sublevel sets. Neither preprint treats the collinear/real-rooted case for general $n$
  (checked against both, August 2026).
- The identity of Lemma 3 is classical in spirit (a resultant identity); the proof above is
  self-contained.
- The general conjecture (some pair of roots joined by a path of length $< 2$) remains open;
  the collinear case proved here is, to our knowledge, the first unbounded-degree class of
  root configurations for which it is established with the *straight segment* as witness.
