# Exact values of f(n) for n ≤ 27 (Erdős problem #963)

**Claim.** Let $f(n)$ be the largest $k$ such that every $n$-element set $A \subset \mathbb{R}$
contains a dissociated subset of size $k$ (dissociated: all $2^{|B|}$ subset sums
$\sum_{b\in S} b$, $S \subseteq B$, are pairwise distinct). Then

| $n$ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18–27 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| $f(n)$ | 0 | 1 | 1 | 2 | 2 | 2 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | **4** | **4** | 4 | 4 | 4 |
| $\lfloor\log_2 n\rfloor$ | 0 | 1 | 1 | 2 | 2 | 2 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 4 |

In particular $f(n) \ge \lfloor \log_2 n\rfloor$ for all $n \le 27$, **with strict
inequality exactly at $n = 14, 15$** (where $f = 4 > 3$): the conjectured floor bound of
problem #963 is confirmed in this range but is *not* the truth — $f$ is not equal to
$\lfloor\log_2 n\rfloor$ as a function.

Conventions pinned from the problem statement ("any set $A\subset\mathbb{R}$ of size $n$"):
$A$ may contain $0$ and sign-pairs $\{x,-x\}$; the empty set is dissociated (size 0);
$\{x\}$ is dissociated iff $x \neq 0$; any set containing $0$ is not dissociated
(the subsets $\emptyset$ and $\{0\}$ have equal sums). Hence $f(1)=0$ (take $A=\{0\}$).

Equivalent characterization used throughout: $B = \{b_1,\dots,b_r\}$ is dissociated iff
there is **no nonzero $\varepsilon \in \{-1,0,1\}^r$** with $\sum_i \varepsilon_i b_i = 0$
(two subsets $S \ne S'$ with equal sums give $\varepsilon = \mathbf{1}_S - \mathbf{1}_{S'} \neq 0$;
conversely split a vanishing $\varepsilon$ into its positive and negative parts).

Write $\mathrm{md}(A)$ for the size of the largest dissociated subset of $A$, so
$f(n) = \min_{|A| = n} \mathrm{md}(A)$. Note $\mathrm{md}$ is monotone:
$A \subseteq A' \Rightarrow \mathrm{md}(A) \le \mathrm{md}(A')$ (every dissociated subset of
$A$ is one of $A'$), and subsets of dissociated sets are dissociated.

---

## 1. Reduction theorem (halving the dimension)

Define, for $m \ge 0$,
$$h(m) \;=\; \min\bigl\{\, \mathrm{md}(U) \;:\; U \subset \mathbb{R},\ |U| = m,\
0 \notin U,\ u \ne -u' \text{ for all } u,u' \in U \,\bigr\},\qquad h(0)=0 .$$
(That is: $m$ distinct nonzero reals, no two of which sum to $0$ — "$m$ distinct
sign-classes".)

**Theorem 1.** $f(n) = h\!\left(\lceil (n-1)/2 \rceil\right)$ for all $n \ge 1$.

*Proof.*

**(a) Sign flips preserve dissociativity.** If $B' $ is obtained from $B$ by replacing
some elements $b$ by $-b$, then vanishing ternary combinations of $B'$ correspond to
vanishing ternary combinations of $B$ with the corresponding $\varepsilon_i$ negated. So
$B$ dissociated $\iff$ $B'$ dissociated.

**(b) $h$ is nondecreasing.** Let $U$ attain $h(m)$, $m \ge 1$, and drop one element to
get $U'$ ($|U'| = m-1$, still class-distinct). Then
$h(m) = \mathrm{md}(U) \ge \mathrm{md}(U') \ge h(m-1)$ by monotonicity of $\mathrm{md}$.

**(c) $\mathrm{md}(A) = \mathrm{md}(R)$ for a class-representative subset $R \subseteq A$.**
Given any finite $A \subset \mathbb{R}$, partition $A \setminus \{0\}$ into *sign classes*
$\{x, -x\} \cap A$; let $c$ be the number of classes and pick one element of each class,
giving $R \subseteq A$ with $|R| = c$, $R$ class-distinct and $0\notin R$.
$\mathrm{md}(A) \ge \mathrm{md}(R)$ since $R \subseteq A$. Conversely let $B \subseteq A$ be
dissociated. Then $0 \notin B$, and $B$ contains at most one element of each class ($x + (-x) = 0$
is a vanishing ternary combination). Map each $b \in B$ to the representative of its class
(i.e. $b$ or $-b$); this is an injection into $R$ whose image is dissociated by (a). So
$\mathrm{md}(A) \le \mathrm{md}(R)$, hence equality.

**(d) Lower bound $f(n) \ge h(\lceil (n-1)/2\rceil)$.** Let $|A| = n$. At most one element
of $A$ is $0$ and each class has at most 2 elements, so the class count satisfies
$n \le 1 + 2c$, i.e. $c \ge \lceil (n-1)/2 \rceil$. By (c), (b):
$\mathrm{md}(A) = \mathrm{md}(R) \ge h(c) \ge h(\lceil (n-1)/2\rceil)$.

**(e) Upper bound (construction).** Let $m = \lceil (n-1)/2\rceil$ and let
$U = \{u_1, \dots, u_m\}$ attain $h(m)$ (for $n=1$ take $A=\{0\}$). Let
$p = n - 1 - m = \lfloor (n-1)/2 \rfloor \le m$ and set
$$A \;=\; \{0\} \,\cup\, \{\pm u_1, \dots, \pm u_p\} \,\cup\, \{u_{p+1}, \dots, u_m\}.$$
Then $|A| = 1 + 2p + (m - p) = n$, all elements distinct (class-distinctness of $U$), and
the class representatives of $A$ are exactly $U$, so $\mathrm{md}(A) = \mathrm{md}(U) = h(m)$
by (c). Hence $f(n) \le h(m)$. $\blacksquare$

So the whole table reduces to computing
$$h(1),\dots,h(13): \qquad f(2t) = f(2t+1) = h(t) \quad (t\ge 1), \qquad f(1) = h(0) = 0 .$$

## 2. Coincidence patterns as rational subspaces

Fix $m$ and a class-distinct tuple $U = (u_1,\dots,u_m)$ as in the definition of $h$.
Its **pattern** is $N(U) = \{\varepsilon \in T_m : \sum_i \varepsilon_i u_i = 0\}$ where
$T_m = \{-1,0,1\}^m$. Let $V = \operatorname{span}_{\mathbb{Q}} N(U) \subseteq \mathbb{Q}^m$.

**Lemma 2.** (i) $V \cap T_m = N(U)$. (ii) $V$ contains none of the vectors
$e_i$, $e_i - e_j$, $e_i + e_j$ ($i \ne j$). (iii) For $S \subseteq [m]$, the subset
$\{u_i : i \in S\}$ is dissociated iff no nonzero $\varepsilon \in V \cap T_m$ has
support $\subseteq S$. Hence $\mathrm{md}(U)$ depends only on $V$:
$\mathrm{md}(U) = \mathrm{maxdiss}(V) := \max\{|S| : \text{no nonzero } \varepsilon \in V\cap T_m,\ \operatorname{supp}\varepsilon \subseteq S\}$.

*Proof.* (i) Orthogonality to the real vector $(u_1,\dots,u_m)$ is linear, so every vector
of $V$, in particular every ternary one, lies in $N(U)$; conversely $N(U) \subseteq V$ by
definition. (ii) $e_i \in V$ would force $u_i = 0$; $e_i \mp e_j \in V$ would force
$u_i = \pm u_j$ — all excluded by class-distinctness. (iii) is the ternary
characterization of dissociativity plus (i). $\blacksquare$

**Lemma 3 (realization).** Conversely, let $V \subseteq \mathbb{Q}^m$ be any subspace
spanned by ternary vectors such that $e_i, e_i \pm e_j \notin V$. Then there exists a
class-distinct **integer** tuple $U$ with $N(U) = V \cap T_m$ (hence
$\mathrm{md}(U) = \mathrm{maxdiss}(V)$).

*Proof.* Let $W = V^{\perp} \cap \mathbb{Q}^m$; over $\mathbb{Q}$, $W^{\perp} = V$. For each
ternary $\varepsilon \notin V$ the set $\{w \in W : \varepsilon \cdot w = 0\}$ is a proper
subspace of $W$ (else $\varepsilon \in W^\perp = V$). A vector space over the infinite
field $\mathbb{Q}$ is not a finite union of proper subspaces, so there is $w \in W$ avoiding
all of them; scaling clears denominators. This $U = w$ satisfies $\varepsilon \cdot U = 0$
exactly for $\varepsilon \in V \cap T_m$; the excluded vectors $e_i, e_i\pm e_j$ make the
coordinates nonzero, distinct and non-sign-paired. $\blacksquare$

(In the computation, Lemma 3 is not taken on faith: each extremal witness is produced as an
explicit integer tuple and *re-verified by direct subset-sum enumeration*.)

**Corollary 4.**
$h(m) = \min \{\mathrm{maxdiss}(V)\}$ over all subspaces $V \subseteq \mathbb{Q}^m$ spanned
by ternary vectors with $e_i, e_i\pm e_j \notin V$ ("valid subspaces"). This is a
*finite* problem.

The analogous statement for $f$ itself (used for the independent cross-checks) replaces the
constraint list by $e_i - e_j \notin V$ only ($A$ may contain $0$ and sign-pairs, but its
elements are distinct).

## 3. Certification of the lower bounds

To prove $h(m) \ge k$ we must show: **no valid $V$ has $\mathrm{maxdiss}(V) \le k-1$**,
i.e. no valid $V$ "covers" every $k$-subset $S \subseteq [m]$ (covers = contains a nonzero
ternary vector supported inside $S$). Note that in a valid ($h$-mode) subspace every ternary
vector has support of size $\ge 3$, since the ternary vectors of support size $\le 2$ are, up
to sign, exactly the excluded $e_i$, $e_i \pm e_j$.

The search: maintain a valid subspace $V$ (starting from a first generator, see symmetry
below); find the first uncovered $k$-subset $S$ in a fixed order; branch over all ternary
$w$ with $\operatorname{supp}(w) \subseteq S$, $|\operatorname{supp}(w)| \ge 3$, $w \notin V$,
for which $V' = \operatorname{span}(V \cup \{w\})$ is still valid; recurse. Memoize visited
subspaces by their canonical reduced row echelon form.

**Lemma 5 (completeness).** If some valid $V^*$ covers all $k$-subsets, the search finds
some adversary. *Proof sketch (induction on $\operatorname{corank}$, using that validity is
inherited by subspaces of valid spaces — the constraints are of the form $x \notin V$):*
every node $V \subseteq V^*$ either covers everything (found), or its first uncovered $S$ is
covered in $V^*$ by some ternary $w^*$ with $\operatorname{supp} \subseteq S$; the branch
$w^*$ produces $V' = V + \langle w^*\rangle \subseteq V^*$ of strictly larger rank, valid, and
(by induction) its subtree finds an adversary. Memoized "refuted" entries are sound by the
same induction (a subspace is marked refuted only after all its branches are exhausted, and
ranks strictly increase along any chain, so no cyclic dependence). $\blacksquare$

**Symmetry at the root.** In $h$-mode, signed coordinate permutations (the hyperoctahedral
group) map valid subspaces to valid subspaces and preserve the covering property (the
constraint list $\{e_i,\, e_i \pm e_j\}$ and $T_m$ are invariant). Any adversary covers the
first $k$-subset $S_0$ with some ternary $w$, $|\operatorname{supp} w| = s \in \{3,\dots,k\}$;
a signed permutation maps $w$ to $(1,\dots,1,0,\dots,0)$ ($s$ ones). So in $h$-mode it
suffices to root the search at these $\le k$ canonical first vectors.
In $f$-mode the constraint list $\{e_i - e_j\}$ is **not** invariant under sign flips (a
flip of coordinate $j$ maps $e_i - e_j$ to $e_i + e_j$, which is permitted in $f$-mode), so
only plain coordinate permutations and global negation (which acts trivially on spans) may
be used: replacing $w$ by $-w$ if needed, at most $\lfloor s/2\rfloor$ entries are $-1$, and
a permutation moves the support to an initial segment with the $-1$s last. The $f$-mode
roots are therefore $(1^{\,s-j}\,(-1)^{\,j}\,0\cdots0)$ for $1 \le s \le k$,
$0 \le j \le \lfloor s/2 \rfloor$, excluding forbidden vectors. (An earlier draft
incorrectly applied the signed-permutation reduction in $f$-mode as well; the $f$-mode
runs below use the corrected roots, and the $k \le 2$ runs were unaffected since the only
support-$2$ mixed-sign pattern $e_i - e_j$ is forbidden. The independent verifier
optionally skips the reduction entirely and starts from *all* candidate vectors of $S_0$;
results agree.)

**Exactness of mod-$p$ arithmetic.** The fast engine does linear algebra over
$\mathbb{F}_p$, $p = 2^{31}-1$. All matrices occurring have $\le 10$ columns and ternary
rows, so by Hadamard's inequality every minor determinant is $< 10^{5}$ in absolute value.
Every entry of an exact rational RREF, and every entry of a reduced residual vector, is a
ratio of such minors (Cramer), with numerator and denominator nonzero integers of absolute
value $< 10^5 < p$. Such a rational neither vanishes nor blows up mod $p$, so ranks,
membership tests, and RREF canonical forms over $\mathbb{F}_p$ coincide with the rational
ones for all inputs of this computation. Memoization additionally needs the mod-$p$ RREF
key to be *injective* on the subspaces arising (a key collision between distinct subspaces
would silently prune an unexplored branch): two distinct entries $a/b \ne c/d$ collide
mod $p$ only if $p \mid ad-bc$, and since every run has dimension $\le 9$ the minors obey
$|a|,|b| \le (\sqrt 9)^9 = 19683$, giving $|ad-bc| \le 2\cdot 19683^2 < 7.8\cdot 10^8 < p$
— so no collision is possible. (Also cross-checked against two exact
implementations: `Fraction`-based and fraction-free integer elimination.)

## 4. Results of the certified computation

Lower bounds (exhaustive refutations; `search963.py refute`, cross-run by
`verify_independent.py` with different arithmetic, data structures, branching order, and
without the root symmetry reduction):

| claim | mode | dim | k | search outcome | nodes |
|---|---|---|---|---|---|
| $h(3) \ge 2$, $h(4) \ge 3$ | h | 3, 4 | (full enumeration) | min maxdiss = 2 over 5 subspaces; = 3 over 361 subspaces | 5; 361 |
| $h(5) \ge 3$ | h | 5 | 3 | refuted | 3 |
| $h(6) \ge 3$ | h | 6 | 3 | refuted | 3 |
| $h(7) \ge 4$ | h | 7 | 4 | **refuted** | 283 215 |
| $f(4) \ge 2$ (direct) | f | 4 | 2 | refuted | 4 |
| $f(5),f(6),f(7) \ge 2$ (direct) | f | 5–7 | 2 | refuted | 4 each |
| $f(8) \ge 3$ (direct) | f | 8 | 3 | refuted | 5 630 |
| $f(9) \ge 3$ (direct) | f | 9 | 3 | refuted | 8 870 |

$h(m) \ge 4$ for $m \ge 7$ follows from $h(7) \ge 4$ by monotonicity (Theorem 1(b)).
The direct $f$-mode rows use only the $e_i - e_j$ constraints, i.e. they certify $f(n)$
in dimension $n$ *without* Theorem 1 — and agree with its predictions.

The key refutation $h(7)\ge 4$ was executed twice: fast engine (mod-$p$ RREF,
recursive DFS, lexicographic branching, root-symmetry reduction) and the independent
engine (fraction-free integer elimination, explicit stack, reversed branching order,
`Fraction`-RREF memo keys). Both refute, and both visit **exactly 283 215 subspaces** —
as they must, since the two engines share the same branching rule (first uncovered
$k$-subset in lexicographic order, same root representatives), which determines the
reachable set of valid subspaces independently of arithmetic, data structures, and
within-subset candidate order; the identical count is a strong end-to-end consistency
check of both memoizations. (An engine with a *different* subset order visits a
different, generally larger, set of subspaces but must reach the same verdict.)
The smaller refutations, **including both direct $f$-mode $k=3$ runs ($f(8)$, $f(9)$)**,
were additionally re-run on the independent engine *without* the root-symmetry reduction
(full branching over every candidate first vector), also agreeing — so the $f$-mode
certifications do not depend on the root reduction at all.

Upper bounds (explicit witnesses, verified by direct subset-sum enumeration in
`verify_witnesses.py` — no linear algebra involved):

| $m$ | witness $U$ for $h(m) \le \cdot$ | $\mathrm{md}$ |
|---|---|---|
| 1 | $\{1\}$ | 1 |
| 2 | $\{1,2\}$ | 2 |
| 3 | $\{1,2,3\}$ | 2 |
| 4 | $\{1,2,3,4\}$ | 3 |
| 5 | $\{1,\dots,5\}$ | 3 |
| 6 | $\{1,\dots,6\}$ | 3 |
| 7–12 | $\{1,\dots,m\}$ | 4 |
| 13 | $\{1,2,3,4,5,6,7,8,9,10,12,13,15\}$ | 4 |

For $m \le 12$ the initial interval happens to be $h$-extremal, but
$\mathrm{md}([1..13]) = 5$ (the interval picks up the Conway–Guy-type 5-element set
$\{6,9,11,12,13\} \subset [13]$ with distinct subset sums), and the $m = 13$ witness —
found by randomized local search, then verified exhaustively (all $\binom{13}{5} = 1287$
5-subsets carry a vanishing $\{-1,0,1\}$-combination) — shows that **the extremal
configurations stop being intervals at $k = 4$**: it skips 11 and 14 and reaches to 15.

Combining: $h(1)=1$, $h(2)=2$, $h(3)=2$, $h(4)=h(5)=h(6)=3$, $h(m)=4$ for $7\le m\le 13$,
and Theorem 1 yields the table of $f$ at the top. Explicit $f$-extremal witnesses (all
verified directly):

* $n=3$: $\{0, 1, -1\}$, $\ \mathrm{md}=1$;
* $n=5$: $\{0, \pm1, \pm2\}$, $\ \mathrm{md}=2$;
* $n=7$: $\{0, \pm1, \pm2, \pm3\}$, $\ \mathrm{md}=2$;
* $n=9$: $\{0, \pm1, \pm2, \pm3, \pm4\}$, $\ \mathrm{md}=3$;
* $n=13$: $\{0, \pm1, \pm2, \pm3, \pm4, \pm5, \pm6\}$, $\ \mathrm{md}=3$;
* $n=25$: $\{0, \pm1, \pm2, \dots, \pm12\}$, $\ \mathrm{md}=4$;
* $n=27$: $\{0, \pm1, \dots, \pm10, \pm12, \pm13, \pm15\}$, $\ \mathrm{md}=4$;
* even $n$: drop one signed element, e.g. $n=8$: $\{0,\pm1,\pm2,\pm3,4\}$, $\mathrm{md}=3$.

## 5. Remarks

1. **The floor bound is strict at $n = 14, 15$.** Erdős's question (as posed on
   erdosproblems.com #963) asks whether $f(n) \ge \lfloor \log_2 n \rfloor$. In the range
   $n\le 27$ the answer is yes — but at $n = 14, 15$ we get $f(n) = 4 > 3$: the
   symmetric-set adversary $\{0,\pm u_1,\dots,\pm u_t\}$ that is exactly optimal cannot push
   $f$ down to the floor there, because $h(7) = 4 > 3$: *every* 7 reals with distinct
   sign-classes contain a dissociated quadruple, while $\lfloor\log_2 14\rfloor = 3$.
2. **Structure of $f$: a staircase governed by $T(k) := \max\{m : h(m) \le k\}$.**
   $f$ equals $k$ exactly on $n \in [2T(k-1)+2,\ 2T(k)+1]$. The certified data:
   $T(1) = 1$, $T(2) = 3$, $T(3) = 6$, $T(4) \ge 13$ (whether $T(4) = 13$ is open —
   our search found no 14-class set of $\mathrm{md}$ 4; certifying $h(14) \ge 5$
   exhaustively at $m=14$, $k=5$ is out of reach for this method). The upper-bound side of
   $T(k)$ (how large can a class-distinct real set with no dissociated $(k+1)$-subset be)
   is a structured relative of Erdős problem #1 (distinct subset sums): interval sets give
   $T(k) \ge u_{k+1} - 1$ where $u_{k+1}$ is the minimal top element of a
   $(k+1)$-element distinct-subset-sums set, and the $m=13$ witness shows this is
   **not** tight at $k = 4$ ($13 > u_5 - 1 = 12$).
3. **Not an OEIS sequence.** The first 21 values of $f$ coincide with
   A000194 (nearest integer to $\sqrt{n}$, with $f(1)=0$ read appropriately), but diverge
   at $n = 22$: $f(22) = 4$ while A000194 gives 5. No OEIS entry matches the certified
   sequence $0,1,1,2,2,2,2,3^{(6)},4^{(14)},\dots$; the small-$n$ resemblance to
   $\sqrt{n}$-growth is an artifact of the pre-asymptotic regime (asymptotically
   $f(n) = (1+o(1))\log_2 n$ granting the 2025 forum proof of the lower bound).
4. **Scaling of the certification.** The refutation at $m=7$, $k=4$ visited $2.8\cdot 10^5$
   subspaces; the analogous $m=14$, $k=5$ refutation is far out of reach for this method
   without substantially more symmetry reduction.

## Reproduction

```
sh verify_smalln.sh    # re-runs every certified claim from scratch (~15-25 min)
```

All searches are deterministic. Code: `search963.py` (fast engine),
`verify_independent.py` (independent engine), `verify_witnesses.py` (direct subset-sum
checks), `falsifier.py` (randomized sanity: no random set ever beats the claimed minimum).
(`verify.sh`/`verify.py` in this directory belong to the companion write-up
`proof_main.md` on the asymptotic lower bound; the two verifications are disjoint.)
