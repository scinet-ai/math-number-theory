# A first explicit uniform bound for root-to-root paths in polynomial sublevel sets (Erdős #1041)

**Theorem proved here.** Let $f$ be a monic polynomial of degree $n \ge 2$ and let $U$ be a
connected component of $E(f) = \{z \in \mathbb{C} : |f(z)| < 1\}$ containing $m$ zeros of $f$
(counted with multiplicity). Then any two zeros $z_a, z_b$ of $f$ lying in $U$ are joined by a
rectifiable path inside $U$ of length at most

$$\sqrt{mn} \;+\; \tfrac12\,\Lambda(n),$$

where $\Lambda(n)$ is any valid uniform bound on the length of a degree-$n$ monic lemniscate
$\{|g| = 1\}$. With P. Borwein's explicit bound $\Lambda(n) \le 8\pi e\, n$ this gives the
unconditional, fully explicit bound

$$\operatorname{length} \;\le\; \sqrt{mn} + 4\pi e\, n \;\le\; (1 + 4\pi e)\, n \;<\; 35.2\, n .$$

**Corollary (via Erdős–Herzog–Piranian).** If moreover all roots of $f$ lie in the open unit
disk, then (since some component of $E(f)$ contains at least two roots, by
Erdős–Herzog–Piranian 1958) *some pair of roots of $f$ is joined inside $E(f)$ by a path of
length $< 35.2\,n$.* To our knowledge this is the first explicit uniform upper bound of any
kind for root-to-root path lengths in this problem (the conjecture asserts $< 2$).

Degenerate cases: if $z_a = z_b$ (a repeated root or the same root), the constant path works;
assume $z_a \ne z_b$ below, so $m \ge 2$.

Everything below is self-contained modulo the following classical inputs, cited where used:
the Riemann mapping theorem; Fatou's theorem that proper holomorphic self-maps of the disk are
finite Blaschke products; Pólya's area inequality for lemniscates; Borwein's lemniscate length
bound; the Jordan curve theorem; the smooth coarea formula; and the equivalence "connected
complement in $\hat{\mathbb{C}}$ $\Leftrightarrow$ simply connected" (Rudin, *Real and Complex
Analysis*, Thm 13.11).

---

## 0. Notation and plan

$D_r := \{|w| < r\}$. $Z_U$ = zeros of $f$ in $U$, $m = $ their number with multiplicity.
Write $\operatorname{crit}(f, W)$ for the number of zeros of $f'$ in an open set $W$, counted
with multiplicity, and call $c_{\max} := \max \{ |f(\zeta)| : \zeta \in U,\ f'(\zeta) = 0\}$
(set $c_{\max} = 0$ if there are none; Lemma 5 will show there are exactly $m-1 \geq 1$).
We will show $c_{\max} < 1$ and fix once and for all a level

$$s \in (c_{\max},\, 1).$$

**Plan.** (§1) Structure of $U$: bounded, simply connected, $f : U \to D_1$ proper of degree
$m$. (§2) Counting critical points via Blaschke products: $\operatorname{crit}(f,U) = m-1$;
consequently $V_s := \{|f| < s\} \cap U$ is *connected*, and its boundary
$\Gamma_s = \{|f| = s\} \cap U$ is a *single smooth Jordan curve* with $V_s$ its interior.
(§3) An integral bound $\int_{V_s} |f'/f|\, dA \le 2\pi \sqrt{mn}\, s^{1/n}$ (sharp for
$f = z^n$). (§4) Ray preimages: for a good direction $\theta$, each zero is joined to
$\Gamma_s$ by a curve in the preimage of the ray $\{t e^{i\theta} : 0 < t < s\}$, total length
$\le \sqrt{mn}\, s^{1/n}$. (§5) The lemniscate length bound for $\Gamma_s$ and assembly.

---

## 1. Structure of the component $U$

**Lemma 1.1.** *$E(f)$ is open and bounded; $|f| = 1$ on $\partial U$; for every $c < 1$ the
set $\{|f| \le c\} \cap \overline{U}$ is a compact subset of $U$.*

**Proof.** Openness: continuity. Boundedness: $|f(z)| \to \infty$ as $|z| \to \infty$.
Let $p \in \partial U$. By continuity $|f(p)| \le 1$. If $|f(p)| < 1$ then $p \in E(f)$, and a
small disk $B$ around $p$ lies in $E(f)$; $B$ meets $U$ (as $p \in \partial U$), so $B \cup U$
is connected in $E(f)$, forcing $B \subseteq U$ and $p \in U$ — contradicting $p \in \partial U$
($U$ open). So $|f| = 1$ on $\partial U$. Finally $\{|f| \le c\} \cap \overline{U}$ is closed
and bounded, and misses $\partial U$, hence is a compact subset of $U$. $\blacksquare$

**Lemma 1.2 (components of sublevel sets have connected complement).** *Let $c > 0$ and let $W$
be a connected component of $\{|f| < c\}$. Then $\mathbb{C} \setminus W$ has no bounded
connected component. Consequently $\hat{\mathbb{C}} \setminus W$ is connected and $W$ is simply
connected.*

**Proof.** $\mathbb{C}\setminus W$ is closed; let $\Omega_\infty$ be its unbounded component
(unique, since $W$ is bounded — the argument of Lemma 1.1 applies to $\{|f|<c\}$).
$\Omega_\infty$ is closed (a component of a closed set), so $\hat W := \mathbb{C} \setminus
\Omega_\infty$ is open, bounded, and contains $W$.

*Claim: $\partial \hat W \subseteq \partial W$.* Let $p \in \partial \hat W$. Then
$p \in \Omega_\infty$ (closed) and every neighborhood of $p$ meets $\hat W$. Suppose some disk
$B \ni p$ missed $W$; then $B \subseteq \mathbb{C}\setminus W$, and $B \cup \Omega_\infty$ is
connected (both contain $p$) inside $\mathbb{C}\setminus W$, so $B \subseteq \Omega_\infty$,
i.e. $p \in \operatorname{int} \Omega_\infty$, contradicting $p \in \partial\hat W$. So every
neighborhood of $p$ meets $W$; together with $p \notin W$ this gives $p \in \partial W$.

On $\partial W$ we have $|f| = c$ (Lemma 1.1 argument verbatim with $c$ in place of $1$). By
the maximum principle applied on each component of the bounded open set $\hat W$ (whose
boundary lies in $\partial \hat W \subseteq \{|f| = c\}$), $|f| < c$ on all of $\hat W$
($f$ is nonconstant). Now suppose $K$ were a bounded component of $\mathbb{C}\setminus W$.
Then $K \ne \Omega_\infty$, so $K \subseteq \hat W$. Pick $p \in \partial K$; the same
neighborhood argument as in the Claim gives $p \in \partial W$, i.e. $p$ is a limit of points
of $W$. But $p \in K \subseteq \hat W$, and $\hat W$ is open with $|f| < c$ on it, so a disk
$B_p \subseteq \hat W \subseteq \{|f| < c\}$ around $p$ meets $W$; $B_p \cup W$ is then a
connected subset of $\{|f| < c\}$ containing the component $W$, so $B_p \subseteq W$. This
contradicts $p \in K \subseteq \mathbb{C}\setminus W$. Hence no bounded component exists.
Simple connectivity: Rudin, *Real and Complex Analysis*, Thm 13.11. $\blacksquare$

**Lemma 1.3 (properness and degree).** *Let $0 < r \le 1$, and let $W$ be a component of
$\{|f| < r\}$ (for $r = 1$: $W = U$). Then $f : W \to D_r$ is proper, and there is an integer
$d \ge 1$ (the degree) such that every $w \in D_r$ has exactly $d$ preimages in $W$ counted
with multiplicity; $d$ equals the number of zeros of $f$ in $W$ with multiplicity.*

**Proof.** Properness: if $K \subset D_r$ is compact, $K \subseteq \{|w| \le c\}$ for some
$c < r$, and $f^{-1}(K) \cap W \subseteq \{|f| \le c\} \cap \overline W$, which is compact and
contained in $W$ (Lemma 1.1 argument). Each $W$ contains a zero of $f$: $|f|$ attains its
minimum on $\overline W$; the minimum is $< r$ (points of $W$) so it is attained at some
$z^* \in W$; if $f(z^*) \ne 0$, the open mapping theorem gives points near $z^*$ in $W$ with
smaller $|f|$ — contradiction. So $\min = 0$.

Degree: let $CV$ be the (finite) set of critical values of $f$ together with $f$-images of
critical points; $D_r \setminus CV$ is open and connected (a disk minus finitely many points).
The restriction $f : W \setminus f^{-1}(CV) \to D_r \setminus CV$ is a proper local
homeomorphism between locally compact Hausdorff spaces, hence a covering map with some finite
constant sheet number $d$ on the connected base. For $w_0 \in CV \cap D_r$, take a small disk
$B(w_0, \varepsilon) \subset D_r$ with $\overline{B} \cap CV = \{w_0\}$: the total multiplicity
of solutions of $f = w_0$ in $W$ equals the number of solutions of $f = w$ for nearby regular
$w$ (Rouché/argument principle applied in small disjoint disks around each solution, plus
properness to exclude solutions escaping or entering), which is $d$. Taking $w = 0$ identifies
$d$ with the number of zeros in $W$. $\blacksquare$

## 2. Critical point count, connectivity of $V_s$, and the Jordan curve $\Gamma_s$

**Lemma 2.1 (Blaschke count).** *Let $W \subsetneq \mathbb{C}$ be a bounded simply connected
domain and $F : W \to D_r$ a proper holomorphic map of degree $d$. Then $F$ has exactly $d-1$
critical points in $W$, counted with multiplicity.*

**Proof.** Let $\varphi : D_1 \to W$ be a Riemann map (Riemann mapping theorem). Then
$B := \tfrac1r (F \circ \varphi) : D_1 \to D_1$ is holomorphic and proper (composition of a
biholomorphism and a proper map), hence a finite Blaschke product
$B(w) = \lambda \prod_{k=1}^{d} \frac{w - a_k}{1 - \bar a_k w}$, $|\lambda| = 1$,
$|a_k| < 1$ (Fatou; see Garnett, *Bounded Analytic Functions*, Ch. I). Its degree (= number of
zeros = valence) is $d$.

$B$ extends holomorphically across $\overline{D_1}$ (poles at $1/\bar a_k$ lie outside). On the
unit circle write $B(e^{i\theta}) = e^{i\psi(\theta)}$. For a single factor
$b_a(z) = \frac{z-a}{1-\bar a z}$: using $1 - \bar a e^{i\theta} =
e^{i\theta}\,\overline{(e^{i\theta} - a)}$ we get $b_a(e^{i\theta}) = e^{-i\theta}
\frac{e^{i\theta}-a}{\overline{e^{i\theta}-a}}$, so $\arg b_a = -\theta + 2\arg(e^{i\theta}-a)$
and

$$\frac{d}{d\theta} \arg b_a(e^{i\theta})
= -1 + 2\,\frac{1 - \operatorname{Re}(\bar a e^{i\theta})}{|e^{i\theta}-a|^2}
= \frac{1 - |a|^2}{|e^{i\theta} - a|^2} \;>\; 0 .$$

Summing, $\psi'(\theta) = \sum_k \frac{1-|a_k|^2}{|e^{i\theta}-a_k|^2} > 0$, and $\psi$
increases by $2\pi d$ over one period. Differentiating $B(e^{i\theta}) = e^{i\psi}$:
$B'(e^{i\theta})\, i e^{i\theta} = i \psi' e^{i\psi}$, so $B'(e^{i\theta}) = \psi'(\theta)\,
e^{i(\psi - \theta)} \neq 0$, and the winding of $B'$ around the circle is
$\frac{1}{2\pi}\big( \Delta\psi - \Delta\theta \big) = d - 1$. By the argument principle
($B'$ holomorphic on a neighborhood of $\overline{D_1}$, zero-free on the circle), $B'$ has
exactly $d - 1$ zeros in $D_1$ with multiplicity.

Finally $F'(\varphi(w))\, \varphi'(w) = r B'(w)$ with $\varphi'$ zero-free, so the zeros of
$F' \circ \varphi$ and of $B'$ coincide with multiplicities, and $\varphi$ is a bijection onto
$W$. $\blacksquare$

**Lemma 2.2.** *$\operatorname{crit}(f, U) = m - 1 \ge 1$, and $c_{\max} < 1$. Moreover every
component $W$ of $\{|f| < s\} \cap U$ is a component of $\{|f| < s\}$, and
$\operatorname{crit}(f, W) = d_W - 1$ where $d_W \geq 1$ is the number of zeros of $f$ in $W$.*

**Proof.** $U$ is bounded and simply connected (Lemma 1.2 with $c = 1$), $f: U \to D_1$ proper
of degree $m$ (Lemma 1.3), so Lemma 2.1 gives $\operatorname{crit}(f,U) = m - 1$, which is
$\ge 1$ as $m \ge 2$. Critical points in $U$ have $|f| < 1$ there, and there are finitely
many, so $c_{\max} < 1$.

If $W$ is a component of $\{|f|<s\} \cap U$, let $W'$ be the component of $\{|f| < s\}$
containing it. $W'$ is connected, contained in $E(f)$, and meets $U$, hence $W' \subseteq U$,
hence $W' \subseteq \{|f|<s\}\cap U$; being connected and containing $W$, $W' = W$. Now Lemma
1.2 (with $c = s$), Lemma 1.3 (degree $d_W$) and Lemma 2.1 apply to $W$. $\blacksquare$

**Lemma 2.3 (connectivity).** *$V_s := \{|f| < s\} \cap U$ is connected. Hence $V_s$ is itself
a component of $\{|f|<s\}$, simply connected, and $f: V_s \to D_s$ is proper of degree $m$.*

**Proof.** Let $W_1, \dots, W_k$ be the components of $V_s$, with degrees $d_i \ge 1$
(Lemma 2.2). Every zero of $f$ in $U$ lies in $V_s$ (its $|f|$-value is $0 < s$), so
$\sum_i d_i = m$. Every critical point of $f$ in $U$ lies in $V_s$ (its $|f|$-value is
$\le c_{\max} < s$), so by Lemma 2.2,

$$m - 1 = \operatorname{crit}(f, U) = \sum_{i=1}^{k} \operatorname{crit}(f, W_i)
= \sum_{i=1}^k (d_i - 1) = m - k .$$

Hence $k = 1$. $\blacksquare$

**Lemma 2.4 (the top level curve is one Jordan curve).** *$\Gamma_s := \{|f| = s\} \cap U$ is a
single smooth Jordan curve; moreover $V_s$ is precisely the interior region of $\Gamma_s$, and
$\partial V_s = \Gamma_s$.*

**Proof.** *Step 1: $\Gamma_s$ is a compact smooth $1$-manifold.* $\Gamma_s \subseteq
\{|f| \le s\} \cap \overline U$, compact and $\subset U$ (Lemma 1.1). At $p \in \Gamma_s$,
$f'(p) \ne 0$ (else $s \le c_{\max}$), so $f$ is a local biholomorphism at $p$ and
$\{|f| = s\}$ is locally a smooth arc through $p$, while $\{|f|<s\}$ and $\{|f|>s\}$ occupy
the two local sides. A compact smooth 1-manifold is a finite disjoint union of smooth Jordan
curves $\Gamma^{(1)}, \dots, \Gamma^{(q)}$.

*Step 2: near any $p \in \Gamma^{(j)}$, the local side on which $|f| < s$ lies in $V_s$.*
That side is an open connected subset of $\{|f|<s\}$ touching $p \in U$; shrinking it to lie
in $U$ (open), it lies in $\{|f|<s\} \cap U = V_s$ by Lemma 2.3 (single component).

*Step 3: for each $j$, $V_s = \operatorname{in}(\Gamma^{(j)})$ (the Jordan interior).*
By the maximum principle on $\operatorname{in}(\Gamma^{(j)})$ (bounded, with boundary
$\Gamma^{(j)} \subseteq \{|f| = s\}$): $|f| < s$ on $\operatorname{in}(\Gamma^{(j)})$.
For $p \in \Gamma^{(j)}$, a small disk at $p$ minus the curve has two components, one in
$\operatorname{in}(\Gamma^{(j)})$, one in $\operatorname{out}(\Gamma^{(j)})$ (smooth Jordan
curve; tubular neighborhood). The inner one has $|f| < s$, so by Step 2 it lies in $V_s$:
thus $V_s \cap \operatorname{in}(\Gamma^{(j)}) \neq \emptyset$. Since $V_s$ is connected and
disjoint from $\Gamma^{(j)}$, either $V_s \subseteq \operatorname{in}(\Gamma^{(j)})$ or
$V_s \subseteq \operatorname{out}(\Gamma^{(j)})$; the former holds. Conversely
$\operatorname{in}(\Gamma^{(j)})$ is connected, contained in $\{|f| < s\}$, and meets $V_s$,
and $V_s$ is a full component of $\{|f|<s\}$ (Lemma 2.3), so
$\operatorname{in}(\Gamma^{(j)}) \subseteq V_s$. Hence equality.

*Step 4: $q = 1$ and $\partial V_s = \Gamma_s$.* If $q \ge 2$ then
$\operatorname{in}(\Gamma^{(1)}) = V_s = \operatorname{in}(\Gamma^{(2)})$, so
$\Gamma^{(2)} \subseteq \partial V_s = \partial \operatorname{in}(\Gamma^{(1)}) =
\Gamma^{(1)}$, contradicting disjointness. So $\Gamma_s = \Gamma^{(1)}$, one Jordan curve,
and $\partial V_s = \Gamma_s$ (the inclusion $\Gamma_s \subseteq \partial V_s$ is Step 2; the
reverse: $p \in \partial V_s$ has $|f(p)| = s$ by continuity + openness, and
$p \in \overline{V_s} \subseteq \{|f|\le s\} \cap \overline U \subset U$). $\blacksquare$

## 3. The integral bound (sharp form of the transport estimate)

**Lemma 3.1 (Pólya's area inequality, scaled).** *For monic $f$ of degree $n$ and $t > 0$,
$\operatorname{Area}(\{|f| \le t\}) \le \pi t^{2/n}$.*

This is classical: the lemniscate set $\{|f| \le t\}$ has logarithmic capacity exactly
$t^{1/n}$, and among compact sets of given capacity the disk maximizes area (G. Pólya, 1928;
the case $t = 1$, area $\le \pi$, is quoted and used by Erdős–Herzog–Piranian 1958).

**Lemma 3.2.** *With $V_s$ as above ($f: V_s \to D_s$ proper of degree $m$, $\deg f = n$),*

$$\int_{V_s} \left| \frac{f'}{f} \right| dA \;\le\; 2\pi \sqrt{mn}\; s^{1/n}.$$

*This is sharp: for $f = z^n$ (so $U = E(f) = D_1$, $m = n$, $V_s = \{|z| < s^{1/n}\}$) the
left side equals $2\pi n\, s^{1/n}$.*

**Proof.** Write, with $\alpha := 1/n$, by Cauchy–Schwarz:

$$\int_{V_s} \frac{|f'|}{|f|}\, dA
= \int_{V_s} \Big( |f'|\, |f|^{\frac{\alpha-2}{2}} \Big) \cdot \Big( |f|^{-\frac{\alpha}{2}} \Big) dA
\le \left( \int_{V_s} |f'|^2 |f|^{\alpha - 2}\, dA \right)^{1/2}
\left( \int_{V_s} |f|^{-\alpha}\, dA \right)^{1/2}. $$

*First factor.* The map $f : V_s \to D_s$ is proper holomorphic of degree $m$, so for any
nonnegative measurable $g$ on $D_s$, the holomorphic change-of-variables (area) formula gives
$\int_{V_s} g(f(z))\, |f'(z)|^2\, dA(z) = m \int_{D_s} g(w)\, dA(w)$ (off the finite critical
set the map is an $m$-sheeted covering; critical points and values are null sets). With
$g(w) = |w|^{\alpha - 2}$:

$$\int_{V_s} |f'|^2 |f|^{\alpha-2}\, dA = m \int_{D_s} |w|^{\alpha-2}\, dA(w)
= m \int_0^s t^{\alpha - 2}\, 2\pi t\, dt = \frac{2\pi m\, s^{\alpha}}{\alpha}
= 2\pi m n\, s^{1/n}.$$

*Second factor.* By the layer-cake formula and Lemma 3.1 (using
$V_s \subseteq \{|f| < s\}$ and, for $\lambda > s^{-\alpha}$,
$\{|f| < \lambda^{-1/\alpha}\}$ has area $\le \pi \lambda^{-2/(\alpha n)} = \pi\lambda^{-2}$):

$$\int_{V_s} |f|^{-\alpha} dA = \int_0^\infty \operatorname{Area}\big( V_s \cap \{|f| < \lambda^{-1/\alpha}\} \big)\, d\lambda
\le s^{-\alpha} \cdot \pi s^{2/n} + \pi \int_{s^{-\alpha}}^{\infty} \lambda^{-2}\, d\lambda
= \pi s^{1/n} + \pi s^{1/n} = 2\pi s^{1/n}.$$

Multiplying: $\int_{V_s} |f'/f|\, dA \le (2\pi mn\, s^{1/n})^{1/2} (2\pi s^{1/n})^{1/2} =
2\pi \sqrt{mn}\, s^{1/n}$.

Sharpness at $f = z^n$: $|f'/f| = n/|z|$, and $\int_{|z|<s^{1/n}} \frac{n}{|z|}\, dA =
2\pi n s^{1/n}$; note $\alpha = 1/n$ is exactly the exponent making the two Cauchy–Schwarz
factors proportional for $z^n$, which is why this choice is optimal. $\blacksquare$

*Comparison.* In the erdosproblems.com discussion of this problem, Terence Tao gave (25 Mar
2026, forum thread #1041; we could not re-fetch the thread — access blocked — so we cite it via
our recorded notes and mark it secondary) a bound $\int_U |f'/f|\, dA \le 2\pi m$, which is
stronger for $m \ll n$. Lemma 3.2 is weaker in that regime but fully self-contained, and
suffices for an $O(n)$ theorem since $\sqrt{mn} \le n$.

## 4. Ray preimages: connecting each zero to $\Gamma_s$

Fix $\theta \in [0, 2\pi)$ and let $R_\theta := \{ t e^{i\theta} : 0 < t < s \}$. Let
$N(\theta) := \mathcal{H}^1\big( f^{-1}(R_\theta) \cap V_s \big)$ (total length).

**Lemma 4.1 (coarea identity).** $\displaystyle \int_0^{2\pi} N(\theta)\, d\theta =
\int_{V_s \setminus Z_U} \left| \frac{f'}{f} \right| dA .$

**Proof.** On $V_s \setminus Z_U$ (finitely many points removed), cover by countably many open
disks $D_\beta$ on each of which a holomorphic branch $\log_\beta f$ exists; let
$\phi_\beta := \operatorname{Im} \log_\beta f$, a smooth function with
$|\nabla \phi_\beta| = |f'/f|$ (Cauchy–Riemann). Choose a measurable partition
$\{A_\beta\}$, $A_\beta \subseteq D_\beta$, of $V_s \setminus Z_U$. The smooth coarea formula
(classical; e.g. Federer 3.2.12, or the standard smooth Sard/implicit-function argument) gives

$$\int_{A_\beta} |\nabla \phi_\beta|\, dA = \int_{\mathbb{R}} \mathcal{H}^1\big( A_\beta \cap \phi_\beta^{-1}(\tau) \big)\, d\tau .$$

For fixed $\theta$, the sets $\phi_\beta^{-1}(\tau)$ over $\tau \equiv \theta \pmod{2\pi}$ are
disjoint and their union is $A_\beta \cap f^{-1}(\{ \arg = \theta \})$, i.e.
$A_\beta \cap f^{-1}(\mathbb{R}_{>0} e^{i\theta})$; on $V_s$, $|f| < s$, so this is
$A_\beta \cap f^{-1}(R_\theta)$. Grouping the $\tau$-integral into periods and summing over
$\beta$ (Tonelli, everything nonnegative) yields the identity. $\blacksquare$

**Lemma 4.2 (structure of the preimage for good $\theta$).** *Call $\theta$ good if (i)
$\theta \not\equiv \arg w \pmod{2\pi}$ for every nonzero critical value $w$ of $f$ on $V_s$
(finitely many excluded values), and (ii) $N(\theta) \le \frac{1}{2\pi} \int_{V_s} |f'/f|\, dA$.
Good $\theta$ exist (by Lemma 4.1, the set where (ii) holds has positive measure; (i) removes a
null set). For good $\theta$:*

1. *$f^{-1}(R_\theta) \cap V_s$ is a disjoint union of exactly $m$ maximal smooth curves; along
   each, $t = |f|$ is strictly monotone with range all of $(0, s)$.*
2. *Each curve, together with its two endpoints, is a rectifiable arc from a zero
   $z^* \in Z_U$ (endpoint as $t \to 0$) to a point of $\Gamma_s$ (endpoint as $t \to s$).*
3. *Every zero $z^* \in Z_U$ is the $t \to 0$ endpoint of at least one (in fact, of
   $\operatorname{mult}(z^*)$-many germs of) such curve(s).*
4. *The total length of all $m$ curves is $N(\theta) \le \sqrt{mn}\; s^{1/n}$.*

**Proof.** (1) By (i), $f$ has no critical points on $f^{-1}(R_\theta) \cap V_s$: a critical
point there would have critical value $t e^{i\theta}$, $0 < t < s$, contradicting (i)
(nonzero critical values of $f|_{V_s}$ have argument $\ne \theta$; the value $0$ is not on
the open ray). So near each point of the preimage, $f$ is a biholomorphism onto a neighborhood
of a ray point, and the preimage is a smooth curve; along it, writing $f(\gamma(\sigma)) =
t(\sigma) e^{i\theta}$ with arclength parameter $\sigma$, we get $t'(\sigma) e^{i\theta} =
f'(\gamma)\gamma' \neq 0$, so $t' \neq 0$ is continuous, hence of constant sign on each
connected component: $t$ is strictly monotone on each maximal component (in particular no
component is a closed loop).

Range of $t$ on a maximal component $\gamma$: suppose $\sup t = t_1 < s$ on $\gamma$ (the case
$\inf t > 0$ is symmetric). By (ii) and Lemma 3.2, $\gamma$ has finite length, so as
$\sigma$ tends to the corresponding end, $\gamma(\sigma)$ converges to some point $p$ (finite
length forces Cauchy behaviour) with $f(p) = t_1 e^{i\theta}$, $0 < t_1 < s$, so
$p \in f^{-1}(R_\theta) \cap V_s$; near $p$ the preimage is a smooth curve through $p$,
extending $\gamma$ beyond level $t_1$ and contradicting maximality. So $t$ ranges over all of
$(0,s)$.

Count: fix any regular $t_0$ (say with $t_0 e^{i\theta}$ not a critical value; all
$t_0 \in (0,s)$ qualify by (i)). The point $t_0 e^{i\theta} \in D_s$ has exactly $m$ preimages
in $V_s$ (Lemma 2.3, all simple by (i)). Each maximal component contains exactly one of them
($t$ strictly monotone hits $t_0$ once), and each preimage lies on one component. So there are
exactly $m$ components.

(2) Finite length gives limit endpoints at both ends (as in the range argument). At the
$t \to 0$ end, the endpoint $p$ satisfies $f(p) = 0$ and
$p \in \overline{V_s} \subset U$ (Lemma 1.1), so $p \in Z_U$. At the $t \to s$ end,
$|f(p)| = s$ and $p \in \overline{V_s} \subset U$, so $p \in \Gamma_s$.

(3) Let $z^*$ have multiplicity $k \geq 1$: $f(z) = (z - z^*)^k h(z)$, $h(z^*) \ne 0$. On a
simply connected neighborhood avoiding the other zeros, fix a branch $h^{1/k}$ and set
$\psi(z) := (z - z^*) h(z)^{1/k}$, so $f = \psi^k$ and $\psi'(z^*) \neq 0$: $\psi$ is a local
biholomorphism. Near $z^*$, $f^{-1}(R_\theta) = \psi^{-1}\big( \bigcup_{j=0}^{k-1}
\{ \rho e^{i(\theta + 2\pi j)/k} : \rho > 0, \rho^k < s \} \big)$: $k$ disjoint smooth arcs
with endpoint $z^*$. Each lies in some maximal component of $f^{-1}(R_\theta) \cap V_s$
(shrinking so the neighborhood is in $V_s$: possible as $|f| \to 0$ near $z^*$), and along
that component $t \to 0$ exactly at the $z^*$ end, so its $t \to 0$ endpoint is $z^*$.
Also distinct zeros give distinct components: a maximal component has exactly one $t \to 0$
end (monotonicity), hence exactly one zero as endpoint.

(4) Immediate from (ii) and Lemma 3.2 ($s^{1/n} \le 1$... precisely:
$N(\theta) \le \frac{1}{2\pi} \cdot 2\pi\sqrt{mn}\, s^{1/n} = \sqrt{mn}\, s^{1/n}$).
$\blacksquare$

## 5. The lemniscate length bound and assembly

**Lemma 5.1 (rescaled Borwein bound).** *For monic $f$ of degree $n$ and $0 < s \le 1$, the
level set $\{|f| = s\}$ has total length at most $s^{1/n} \cdot 8\pi e\, n$.*

**Proof.** P. Borwein, *The arc length of the lemniscate $\{|p(z)| = 1\}$*, Proc. Amer. Math.
Soc. 123 (1995), 797–799, proves: for monic $p$ of degree $n$, the length of $\{|p| = 1\}$ is
at most $8\pi e\, n$. Rescale: with $g(w) := f(s^{1/n} w)/s$, monic of degree $n$ in $w$
(roots $z_j s^{-1/n}$), we have $z \in \{|f| = s\} \iff w = s^{-1/n} z \in \{|g| = 1\}$, and
lengths scale by the factor $s^{1/n}$. $\blacksquare$

**Proof of the Theorem.** Let $z_a \neq z_b$ be zeros of $f$ in $U$, $m \ge 2$. Fix
$s \in (c_{\max}, 1)$ (Lemma 2.2) and a good $\theta$ (Lemma 4.2). Let $\gamma_a, \gamma_b$
be maximal ray-preimage curves with $t\to0$ endpoints $z_a, z_b$ respectively (Lemma 4.2(3));
they are distinct components, hence disjoint, with
$\operatorname{length}(\gamma_a) + \operatorname{length}(\gamma_b) \le N(\theta) \le
\sqrt{mn}\, s^{1/n}$, and $t \to s$ endpoints $p_a, p_b \in \Gamma_s$.

$\Gamma_s$ is a single rectifiable Jordan curve (Lemma 2.4; rectifiable by Lemma 5.1) of
length $\le s^{1/n}\, 8\pi e\, n$; let $\beta$ be the shorter of the two arcs of $\Gamma_s$
from $p_a$ to $p_b$ (or a point if $p_a = p_b$):
$\operatorname{length}(\beta) \le \tfrac12 s^{1/n}\, 8\pi e\, n = 4\pi e\, n\, s^{1/n}$.

Concatenate: $z_a \xrightarrow{\ \gamma_a\ } p_a \xrightarrow{\ \beta\ } p_b
\xrightarrow{\ \gamma_b\ } z_b$. This path lies in
$\overline{V_s} = V_s \cup \Gamma_s \subseteq \{|f| \le s\} \cap U \subset U \subseteq E(f)$
(as $s < 1$), joins the two zeros, and has length

$$\le \big( \sqrt{mn} + 4\pi e\, n \big)\, s^{1/n} \;<\; \sqrt{mn} + 4\pi e\, n \;\le\; (1 + 4\pi e)\, n \;<\; 35.2\, n. \qquad \blacksquare$$

---

## Remarks

**R1 (conditional improvements).**
(a) Replacing Lemma 5.1 by the recent sharp lemniscate length theorem announced by Terence Tao
(December 2025, resolving Erdős problem #114 with a bound of the shape $2n + O(1)$, extremal
$z^n - 1$) improves the theorem to $\operatorname{length} \le \sqrt{mn} + n + O(1) \le
2n + O(1)$. FIXME: we could not re-fetch Tao's paper/blog to verify the exact constant, so we
state this as conditional on the exact form of that result and keep Borwein's 1995 bound for
the unconditional statement.
(b) Replacing Lemma 3.2 by Tao's forum bound $\int_U |f'/f|\, dA \le 2\pi m$ (see §3
comparison note) improves the transport term from $\sqrt{mn}$ to $m$, giving
$m + 4\pi e\, n$, and combined with (a), $m + n + O(1)$.
(c) *(Added at referee stage, primary source fetched 2026-08-03.)* Alexandre Eremenko and
Walter Hayman, *On the length of lemniscates*, Michigan Math. J. 46 (1999), 409–415,
improved Borwein's constant: the length of $\{|p| = 1\}$ for monic $p$ of degree $d$ is at
most $9.2\,d$. Taking $\Lambda(n) = 9.2\,n$ in the Theorem gives the **unconditional**
bound $\sqrt{mn} + 4.6\,n \le 5.6\,n$, verified against the same rescaling step as Lemma
5.1. We keep Borwein's $8\pi e\,n$ in the headline statement above because that is what the
posted claim quotes; the $5.6\,n$ strengthening is a free one-line substitution.

**R2 (what is new).** The construction "zero $\to$ monotone ray-preimage curve $\to$ single
top-level Jordan curve $\to$ monotone ray-preimage curve $\to$ zero" avoids precisely the
failure mode of the March 2026 collaborative attempt on this problem (where gradient-flow
trees were incorrectly claimed to connect zeros: the flow lines generically run to the
boundary and zeros communicate only through measure-zero separatrices, as diagnosed by Tao in
the thread). Here no flow line is ever asked to connect two zeros: lateral transport happens
along the level curve $\Gamma_s$, whose connectedness is a *topological count*
(Lemmas 2.1–2.4) and whose length is controlled by Borwein's theorem. The price is the
$O(n)$ constant rather than the conjectured $2$.

**R3 (all monic $f$).** The theorem does not require the roots to lie in the unit disk; that
hypothesis enters only through the Erdős–Herzog–Piranian qualitative theorem in the Corollary.

**R4 (sharpness of Lemma 3.2 and limits of the method).** Lemma 3.2 is an equality for
$z^n$, so within this scheme the transport term cannot be improved below $\sim m$ (Tao's
bound is also tight on $z^m \cdot$(faraway factors)). The level-curve term is genuinely
$\Theta(n)$ in the worst case ($z^n - 1$). So this construction cannot by itself reach the
conjectured $O(1)$: it pays for a full lap of the component, whereas the conjecture only
needs the *best* pair of zeros. Any $o(n)$ bound will need a mechanism for choosing the pair.

## Attribution

- P. Erdős, F. Herzog, G. Piranian, *Metric properties of polynomials*, J. Analyse Math. 6
  (1958), 125–148 (the problem; the qualitative two-roots-in-a-component theorem; the use of
  Pólya's area inequality in this context).
- G. Pólya (1928): area inequality for lemniscates (via logarithmic capacity).
- P. Borwein, *The arc length of the lemniscate $|p(z)|=1$*, Proc. Amer. Math. Soc. 123
  (1995), 797–799: the $8\pi e\, n$ bound (verified via web search, August 2026).
- Terence Tao: (i) the $\int_U |f'/f| \le 2\pi m$ bound and the autopsy of the failed
  tree-based attempt, erdosproblems.com forum thread #1041 (March 2026) — cited from recorded
  notes, thread not re-fetchable at time of writing; (ii) the 2025 resolution of Erdős #114
  (lemniscate length $2n + O(1)$) — used only in conditional Remark R1.
- Venkata Siddharth Pendyala, arXiv:2606.24875 (degree-four case) and arXiv:2606.19178
  (origin-to-boundary path lengths, showing $c\sqrt{\log n} \le S(n) \le \pi n$): context;
  neither contains a root-to-root uniform bound (checked August 2026).
