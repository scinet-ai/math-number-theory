# The upper bound for Erdős #963: reduction to Erdős #1, and why multi-scale constructions do not help

Companion note to `proof_main.md` (notation as there: $d(A)$ = largest dissociated subset,
$f(n) = \min_{|A| = n} d(A)$ over reals). Define
$$\ell(n) := d(\{1, 2, \dots, n\}).$$

## 1. The interval bound is exactly the Erdős #1 extremal function

For a set of **positive** integers, "dissociated" literally means "all subset sums distinct"
(the two notions coincide for any reals by Lemma 0 of `proof_main.md`; for positive integers the
subset-sum phrasing is the classical one). Hence $\ell(n)$ is *by definition* the largest size of
a distinct-subset-sums subset of $\{1,\dots,n\}$ — the extremal quantity of Erdős Problem #1
(sum-distinct sets; Conway–Guy). Consequently:

**Proposition 1.** (a) $f(n) \le \ell(n)$.
(b) $\lfloor \log_2 n\rfloor + 1 \le \ell(n) \le \log_2 n + \log_2\log_2 n + 3$ for $n \ge 4$.

*Proof.* (a) The set $\{1,\dots,n\}$ is one competitor in the minimum defining $f$.
(b) Lower: $\{2^0, 2^1, \dots, 2^{\lfloor\log_2 n\rfloor}\} \subseteq \{1,\dots,n\}$ has distinct
subset sums (binary representation) and size $\lfloor\log_2 n\rfloor + 1$.
Upper: if $B \subseteq \{1,\dots,n\}$ has all subset sums distinct and $b := |B|$, the $2^b$
subset sums are distinct integers in $[0, bn]$, so $2^b \le bn + 1 \le 2bn$. If $b \ge 4$ then
$2^{b/2} \le 2^b / b \le 2n$, so $b \le 2\log_2 n + 2$; feeding this back,
$b \le \log_2 n + \log_2 b + 1 \le \log_2 n + \log_2(2\log_2 n + 2) + 1
 \le \log_2 n + \log_2\log_2 n + 3$ for $n \ge 4$
(using $\log_2(2\log_2 n + 2) \le 2 + \log_2\log_2 n$ for $n \ge 4$). If $b \le 3$ the bound is
trivial. $\blacksquare$

**Reduction remark.** Write $\delta(n) := \ell(n) - \log_2 n \in [1 - \{\log_2 n\},\,
\log_2\log_2 n + 3]$. Improving the interval upper bound for #963 from
$f(n) \le \log_2 n + (1+o(1))\log_2\log_2 n$ to $f(n) \le \log_2 n + O(1)$ *via the set*
$\{1,\dots,n\}$ is verbatim the statement $\delta(n) = O(1)$, i.e. the conjecture of Erdős
Problem #1 (that a sum-distinct subset of $[n]$ has size $\le \log_2 n + O(1)$). Conversely, the
best known sum-distinct constructions inside $[n]$ (Conway–Guy type; cf. the literature around
Dubroff–Fox–Xu, arXiv:2006.12988) give $\delta(n) \ge 2$ for infinitely many $n$ — literature
note, not used below. So the second-order term of the #963 upper bound, along the interval route,
is exactly #1 territory. Combining Proposition 1 with Theorem 2 of `proof_main.md`:
$$\log_2 n - 2(\log_2\log_2 n)^2 - D \;\le\; f(n) \;\le\; \log_2 n + \log_2\log_2 n + 3 .$$

## 2. Separated multi-scale constructions cannot beat the interval

Could some *other* $A$ do better than $\{1,\dots,n\}$ as an upper-bound witness? The natural
candidates are unions of dilated blocks at widely separated scales ("multi-scale" sets). They
cannot help:

**Proposition 2** (exact additivity across separated scales). Let $A_1, A_2$ be finite sets of
nonzero integers and $M > 2\sum_{a \in A_1} |a|$ an integer. Then $A := A_1 \cup M \! \cdot \! A_2$
is a disjoint union, and
$$d(A) \;=\; d(A_1) + d(A_2).$$

*Proof.* Disjointness: every element of $M A_2$ has absolute value $\ge M > \max_{A_1}|a|$.

($\ge$) Let $B_1 \subseteq A_1$, $B_2 \subseteq A_2$ be dissociated with $|B_i| = d(A_i)$.
Suppose $\sum_{b \in B_1} \varepsilon_b b + M \sum_{b' \in B_2} \varepsilon'_{b'} b' = 0$ is a
signed relation. Then $M\,\big|\sum \varepsilon' b'\big| = \big|\sum \varepsilon_b b\big|
\le \sum_{a \in A_1} |a| < M/2$, so the integer $\sum \varepsilon' b'$ vanishes, forcing
$\varepsilon' = 0$ ($B_2$ dissociated), then $\varepsilon = 0$ ($B_1$ dissociated). So
$B_1 \cup M B_2$ is dissociated of size $d(A_1) + d(A_2)$.

($\le$) Any dissociated $B \subseteq A$ splits as $(B \cap A_1) \sqcup (B \cap M A_2)$; both parts
are dissociated (subsets), and $\frac1M(B \cap MA_2) \subseteq A_2$ is dissociated since dilation
by $M$ preserves signed relations. Hence $|B| \le d(A_1) + d(A_2)$. $\blacksquare$

**Corollary 3.** Let $A = A_1 \cup M_2 A_2 \cup \dots \cup M_s A_s$ ($s \ge 2$) be an iterated
separated union of interval blocks $A_i = \{1, \dots, n_i\}$, $n_1 \ge n_2 \ge \dots \ge n_s \ge 1$,
$\sum n_i = n$, with each dilation factor large enough that Proposition 2 applies at each of the
$s - 1$ junctions. Then
$$d(A) \;=\; \sum_{i=1}^s \ell(n_i) \;\ge\; \lfloor \log_2 n\rfloor + 1 + \sum_{i \ge 2} \lfloor \log_2 n_i \rfloor .$$

*Proof.* Additivity by induction on $s$ via Proposition 2. For the lower bound:
$\ell(n_i) \ge \lfloor\log_2 n_i\rfloor + 1$ (Proposition 1(b)), $n_1 \ge n/s$ gives
$\lfloor\log_2 n_1\rfloor \ge \lfloor\log_2 n\rfloor - \lceil\log_2 s\rceil$, and
$s - 1 \ge \lceil \log_2 s\rceil$ for $s \ge 1$, so
$\sum_i (\lfloor\log_2 n_i\rfloor + 1) \ge \lfloor\log_2 n\rfloor - \lceil\log_2 s\rceil + s
 + \sum_{i\ge2}\lfloor\log_2 n_i\rfloor \ge \lfloor\log_2 n\rfloor + 1 +
 \sum_{i\ge2}\lfloor\log_2 n_i\rfloor$. $\blacksquare$

**Consequences.** For any such multi-scale witness: $d(A) \ge \lfloor\log_2 n\rfloor + 1$, i.e. it
can never push the #963 upper bound below the interval's own trivial floor; and as soon as the
lower scales are non-negligible ($\sum_{i \ge 2} \lfloor\log_2 n_i\rfloor \ge \log_2\log_2 n + 3$,
e.g. a second scale of size $n_2 \ge 16\log_2 n$: then $\lfloor\log_2 n_2\rfloor \ge
\lfloor 4 + \log_2\log_2 n\rfloor = 4 + \lfloor\log_2\log_2 n\rfloor > \log_2\log_2 n + 3$),
we get $d(A) \ge \ell(n)$ by Proposition 1(b)
(using $\lfloor\log_2 n\rfloor + 1 \ge \log_2 n$) — the multi-scale
set is *at least as bad as* the single interval. So among separated multi-scale interval unions
the single interval is optimal up to an additive $O(\log_2\log_2 n)$, every lower scale of
super-polylog size strictly hurts, and any improvement of the upper bound to
$\log_2 n + O(1)$ must come either from the interval itself (= Erdős #1) or from genuinely
non-multi-scale structures. (The same argument with arbitrary blocks $A_i$ and $f$ in place of
$\ell$, using Theorem 2 of `proof_main.md` on each block, gives the analogous statement for
arbitrary separated unions with $O((\log_2\log_2 n_i)^2)$ losses per block.)
