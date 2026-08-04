# Exact small-$r$ values for Erdős problem #616: $t(3)=t(4)=t(5)=1$, $t(r)\ge 2$ for $r\ge 6$, and monotonicity

**Status: complete proofs — every lemma proved in full below; all finite claims additionally machine-verified (`code/verify_616.py`, `code/verify_atoms_lp.py`, driver `verify.sh`).**

## 1. The problem and definitions

Erdős problem #616 (statement as displayed at [erdosproblems.com/616](https://www.erdosproblems.com/616), archived copy in `sources/erdosproblems_616_2026-08-03.html`; problem due to Erdős, source tag [Er99]):

> Let $r\geq 3$. For an $r$-uniform hypergraph $G$ let $\tau(G)$ denote the covering number (or transversal number), the minimum size of a set of vertices which includes at least one from each edge in $G$. Determine the best possible $t$ such that, if $G$ is an $r$-uniform hypergraph where every subgraph $G'$ on at most $3r-3$ vertices has $\tau(G')\leq 1$, we have $\tau(G)\leq t$.

**Conventions.** All hypergraphs are $r$-uniform with $r \ge 3$ and finite (see Remark 2 for the infinite case). For a set $S$ of vertices of $G$, the *induced subgraph* $G[S]$ has vertex set $S$ and edge set $\{E \in G : E \subseteq S\}$. $\tau(G[S]) \le 1$ means some single vertex meets every edge of $G[S]$, vacuously true when $G[S]$ has no edges. We say $G$ has property $L(r)$ if $\tau(G[S]) \le 1$ for every $S$ with $|S| \le 3r-3$; this is the problem's local condition. Define
$$t(r) \;=\; \sup\{\tau(G) : G \text{ is $r$-uniform and has } L(r)\},$$
the "best possible $t$" of the problem. Erdős–Hajnal–Tuza [EHT91] proved (in their actual statements, verified against the paper on 2026-08-04 — see `NOVELTY.md`) $\lfloor\tfrac{3}{16}r+\tfrac78\rfloor \le t(r) \le \lceil\tfrac15 r\rceil$ for all $r\ge3$; the problem page's floorless paraphrase drops both the floor and the ceiling (see §6), and the exact small-$r$ values are recorded neither there nor in the paper.

**Results proved here.**

* **Theorem A.** $t(3)=t(4)=t(5)=1$.
* **Theorem B.** $t(r)\ge 2$ for every $r \ge 6$, witnessed by an explicit 4-edge hypergraph on $4r-8$ vertices.
* **Theorem C.** $t(r+1) \ge t(r)$ for every $r \ge 3$.

Theorems A and B together show that $r=6$ is the exact threshold where the local condition stops forcing a global common vertex. Theorem B is consistent with, and for $r=6$ equal to, the displayed [EHT91] lower bound $\tfrac{3}{16}r+\tfrac78$ (which equals $2$ exactly at $r=6$); its value here is that it is fully self-contained and certificate-checked. Theorem A appears to be new as a recorded statement (see §6 for the priority discussion; we could not access [EHT91] itself).

Throughout, "window" means a vertex set $S$ with $|S| \le 3r-3$.

## 2. Two elementary reductions

**Lemma 1 (subfamily criterion).** *An $r$-uniform hypergraph $G$ has $L(r)$ if and only if every nonempty subfamily $F$ of edges of $G$ with $|\bigcup F| \le 3r-3$ has $\bigcap F \neq \emptyset$.*

*Proof.* ($\Rightarrow$) Let $F$ be a nonempty edge subfamily with $|\bigcup F| \le 3r-3$ and put $S = \bigcup F$. Every edge of $F$ is contained in $S$, so $F \subseteq G[S]$. By $L(r)$ there is a vertex $v$ meeting every edge of $G[S]$; since each edge of $G[S]$ is an $r$-set contained in $S$ and $v$ covers it by itself, $v$ lies in every edge of $G[S]$, in particular $v \in \bigcap F$.

($\Leftarrow$) Let $|S| \le 3r-3$ and let $F$ be the edge set of $G[S]$. If $F = \emptyset$ then $\tau(G[S]) = 0$. Otherwise $\bigcup F \subseteq S$ gives $|\bigcup F| \le 3r-3$, so by hypothesis there is $v \in \bigcap F$; then $v \in \bigcup F \subseteq S$ and $v$ covers every edge of $G[S]$, so $\tau(G[S]) \le 1$. $\blacksquare$

**Lemma 2 (structure and span of minimal empty-intersection families).** *Let $F = \{E_1,\dots,E_m\}$ be an inclusion-minimal family of $r$-sets with $\bigcap_{i=1}^m E_i = \emptyset$ (minimal: every proper subfamily has nonempty intersection). Then:*

1. *$m \ge 2$, and for each $i$ there is a vertex $x_i \in \bigcap_{j \ne i} E_j$ with $x_i \notin E_i$; the $x_1,\dots,x_m$ are pairwise distinct;*
2. *$m \le r+1$;*
3. *$\bigl|\bigcup_{i=1}^m E_i\bigr| \le m(r-m+2)$.*

*Proof.* (1) $m \ge 2$ since a single $r$-set with $r\ge 3$ has nonempty "intersection" (itself). By minimality, for each $i$ the family $F \setminus \{E_i\}$ has nonempty intersection (for $m = 2$ this is the single set $E_j$, nonempty); pick $x_i \in \bigcap_{j\ne i}E_j$. If $x_i \in E_i$ then $x_i \in \bigcap F = \emptyset$, contradiction; so $x_i \notin E_i$. For $i \ne i'$: $x_i \notin E_i$ but $x_{i'} \in E_i$, so $x_i \ne x_{i'}$.

(2) The $m-1$ distinct vertices $\{x_j : j \ne 1\}$ all lie in $E_1$ (each $x_j$ with $j\neq 1$ lies in every $E_k$ with $k \ne j$, in particular in $E_1$), so $m-1 \le |E_1| = r$.

(3) Let $X = \{x_1,\dots,x_m\}$, $|X| = m$. Each edge $E_i$ contains the $m-1$ vertices $\{x_j : j \ne i\} \subseteq X$, hence $|E_i \setminus X| \le r-(m-1)$. Every vertex of $\bigcup F$ is in $X$ or in $E_i \setminus X$ for some $i$, so
$$\Bigl|\bigcup_{i=1}^m E_i\Bigr| \;\le\; m + m\,(r-m+1) \;=\; m(r-m+2). \qquad\blacksquare$$

**Remark 1 (sharpness).** The bound in (3) is attained: take $X = \{x_1,\dots,x_m\}$ and let $E_i = (X\setminus\{x_i\}) \cup P_i$ with $P_1,\dots,P_m$ pairwise disjoint $(r-m+1)$-sets disjoint from $X$. Each $|E_i| = (m-1)+(r-m+1) = r$ and the span is $m + m(r-m+1) = m(r-m+2)$. The family has empty intersection (a common vertex cannot lie in any $P_i$, which meets only $E_i$ when $P_i \neq \emptyset$, nor equal any $x_i \notin E_i$; if $m = r+1$ the $P_i$ are empty and the same conclusion holds on $X$), and it is inclusion-minimal because $x_i \in \bigcap_{j\ne i} E_j$ for each $i$. Machine check: the LP certificate `code/verify_atoms_lp.py` maximizes $|\bigcup F|$ over the exact structural constraints (1)–(2) (atom formulation) and finds optimum $= m(r-m+2)$ for all $3 \le r \le 12$, $2 \le m \le r+1$, confirming both the bound and its attainability.

**Remark 2 (infinite hypergraphs).** If $G$ is infinite with $\tau(G) \ge 2$, no single vertex covers all edges. Fix any edge $E$; for each $v \in E$ pick an edge $E_v$ with $v \notin E_v$. Then $\{E\} \cup \{E_v : v \in E\}$ is a finite subfamily with empty intersection, and it contains an inclusion-minimal such subfamily. All arguments below use only this finite subfamily, so Theorems A–C hold verbatim for infinite $r$-uniform hypergraphs.

## 3. Theorem A: $t(3)=t(4)=t(5)=1$

**Lemma 3.** *For $2 \le m \le r+1$, the quantity $m(r-m+2)$ satisfies*
$$\max_{2 \le m \le r+1} m(r-m+2) \;=\; 3r-3 \quad \text{for } r \in \{3,4,5\}.$$

*Proof.* $m \mapsto m(r-m+2)$ is a concave quadratic; over integers its maximum is at $m \in \{\lfloor (r+2)/2 \rfloor, \lceil (r+2)/2 \rceil\}$. Exhaustively (machine-checked in part [A] of `verify_616.py`):

* $r=3$: values for $m=2,3,4$ are $6,6,4$; max $= 6 = 3\cdot3-3$.
* $r=4$: values for $m=2,\dots,5$ are $8,9,8,5$; max $= 9 = 3\cdot4-3$.
* $r=5$: values for $m=2,\dots,6$ are $10,12,12,10,6$; max $= 12 = 3\cdot5-3$. $\blacksquare$

**Theorem A.** *For $r \in \{3,4,5\}$: every $r$-uniform hypergraph $G$ with $L(r)$ has $\tau(G) \le 1$, and this is best possible, i.e. $t(r) = 1$.*

*Proof.* Suppose for contradiction that $G$ has $L(r)$ but $\tau(G) \ge 2$. Then no vertex lies in every edge, i.e. the family of all edges has empty intersection, and $G$ has at least one edge. Choose an inclusion-minimal subfamily $F = \{E_1,\dots,E_m\}$ with $\bigcap F = \emptyset$ (exists by finiteness, or by Remark 2). By Lemma 2, $2 \le m \le r+1$ and $|\bigcup F| \le m(r-m+2) \le 3r-3$ by Lemma 3. So $F$ is a nonempty subfamily with $|\bigcup F| \le 3r-3$ and $\bigcap F = \emptyset$, contradicting Lemma 1. Hence $\tau(G) \le 1$.

Best possible: the hypergraph with a single $r$-edge has $L(r)$ (every induced subgraph has $0$ or $1$ edges, so $\tau \le 1$) and $\tau = 1$. Hence $t(r) \ge 1$, so $t(r)=1$ for $r \le 5$. $\blacksquare$

## 4. Theorem B: $t(r) \ge 2$ for $r \ge 6$

**The gadget $H_r$.** For $r \ge 6$, let $a_1,a_2,a_3,a_4$ be distinct vertices and $B_1,B_2,B_3,B_4$ pairwise disjoint $(r-3)$-sets, disjoint from $\{a_1,\dots,a_4\}$. Define
$$E_i \;=\; \bigl(\{a_1,a_2,a_3,a_4\} \setminus \{a_i\}\bigr) \cup B_i \qquad (i=1,2,3,4), \qquad H_r = \{E_1,E_2,E_3,E_4\}.$$
Each $|E_i| = 3 + (r-3) = r$, and $|V(H_r)| = 4 + 4(r-3) = 4r-8$.

**Lemma 4.** *For every $r \ge 6$, $H_r$ has property $L(r)$ and $\tau(H_r) = 2$.*

*Proof.* We verify the subfamily criterion of Lemma 1 over all nonempty $F \subseteq H_r$.

* $|F| = 1$: intersection is the edge itself, nonempty.
* $|F| = 2$, say $F = \{E_i, E_j\}$, $i \ne j$: with $\{k,\ell\} = \{1,2,3,4\}\setminus\{i,j\}$ we have $a_k, a_\ell \in E_i \cap E_j$ (each $a_k$ is omitted only from $E_k$). Nonempty.
* $|F| = 3$, say $F = \{E_i,E_j,E_k\}$ with $\ell$ the omitted index: $a_\ell \in E_i \cap E_j \cap E_k$. Nonempty.
* $|F| = 4$: $\bigcap F = \emptyset$ — indeed $a_i \notin E_i$, and every $B$-vertex lies in exactly one edge. But $\bigl|\bigcup F\bigr| = 4r-8$, and $4r-8 > 3r-3 \iff r > 5$; so for $r \ge 6$ this subfamily violates no window constraint: the criterion of Lemma 1 only restricts subfamilies with union of size $\le 3r-3$.

Hence every nonempty subfamily with union $\le 3r-3$ (namely all $F$ with $|F| \le 3$) has a common vertex, so $L(r)$ holds by Lemma 1.

$\tau(H_r) \ge 2$: as just noted, $\bigcap_{i=1}^4 E_i = \emptyset$, so no single vertex covers all four edges. $\tau(H_r) \le 2$: $\{a_1, a_2\}$ is a transversal — $a_1 \in E_2 \cap E_3 \cap E_4$ and $a_2 \in E_1$. $\blacksquare$

**Theorem B.** *For every $r \ge 6$, $t(r) \ge 2$.* 

*Proof.* Immediate from Lemma 4: $H_r$ is $r$-uniform, has $L(r)$, and $\tau(H_r) = 2$. $\blacksquare$

**Machine verification.** Part [B] of `verify_616.py` checks uniformity, span, the subfamily criterion, and $\tau = 2$ for all $6 \le r \le 40$; part [C] additionally verifies $L(r)$ for $r \in \{6,7\}$ *directly from the definition*, enumerating all $2^{16}$ (resp. $2^{20}$) vertex subsets and checking every window of size $\le 3r-3$ induces a subgraph with a common vertex. Part [D] is a negative control establishing failure-power: at $r=5$ the same gadget has span $12 \le 3\cdot 5 - 3$, and both checkers must (and do) flag the violating window — so a hypergraph *without* the local property is detected by this harness. A planted-bug test at the $2^{20}$ scale (edge replaced so that a 14-vertex window becomes bad) was also run and caught during development.

**Remark 3 (why $r=6$ is the threshold, and consistency with [EHT91]).** Theorem A shows the gadget idea cannot work for $r \le 5$: *any* witness family to $\tau \ge 2$ fits inside a forbidden window. At $r = 6$ the unique escape in Lemma 3's table opens at $m=4$: $4(r-4+2) = 16 > 15 = 3r-3$, and $H_6$ realizes exactly this extremal configuration ($4$ distinguished vertices plus $4$ disjoint private $3$-sets, span exactly $16$). The actual [EHT91] lower bound $\lfloor\tfrac{3}{16}r + \tfrac{7}{8}\rfloor$ equals $2$ for $6 \le r \le 11$ and first reaches $3$ at $r = 12$, so Theorem B matches it at $r=6$ and is weaker for large $r$ — Theorem B's contribution is the explicit, self-contained, machine-checked certificate and the exact threshold location, not an asymptotic improvement. (The failed AI attempt discussed in §6 claimed $t(r) = 2$ for *all* $r \ge 6$, which contradicts the [EHT91] lower bound for $r \ge 12$; nothing of that upper-bound claim is used here.)

## 5. Theorem C: monotonicity

**Lemma 5 (pendant extension).** *Let $r \ge 3$ and let $G$ be $r$-uniform with property $L(r)$. Let $P(G)$ be the $(r+1)$-uniform hypergraph obtained by adding, for each edge $E \in G$, a new pendant vertex $v_E$ (all distinct, none in $V(G)$) and replacing $E$ by $E' = E \cup \{v_E\}$. Then $P(G)$ has property $L(r+1)$ and $\tau(P(G)) = \tau(G)$.*

*Proof.* **$L(r+1)$:** By Lemma 1 (applied at uniformity $r+1$) it suffices to show every nonempty subfamily $F' = \{E'_1,\dots,E'_k\}$ of $P(G)$ with $|\bigcup F'| \le 3(r+1)-3 = 3r$ has a common vertex. Let $F = \{E_1,\dots,E_k\}$ be the corresponding edges of $G$. If $k = 1$ we are done. 

If $k = 2$: since $G$ is $r$-uniform and $r \ge 3$, $|E_1 \cup E_2| \le 2r \le 3r-3$; by Lemma 1 applied to $G$ (property $L(r)$), $E_1 \cap E_2 \ne \emptyset$, and $E_1 \cap E_2 \subseteq E'_1 \cap E'_2$.

If $k \ge 3$: the pendants $v_{E_1},\dots,v_{E_k}$ are distinct and belong to $\bigcup F'$ but not to $\bigcup F$, so $|\bigcup F| \le |\bigcup F'| - k \le 3r - 3$. By Lemma 1 applied to $G$, $\bigcap F \neq \emptyset$, and $\bigcap F \subseteq \bigcap F'$. In all cases $F'$ has a common vertex, so $P(G)$ has $L(r+1)$. 

**$\tau(P(G)) \le \tau(G)$:** any transversal of $G$ meets every $E \subseteq E'$, hence is a transversal of $P(G)$.

**$\tau(P(G)) \ge \tau(G)$:** let $T'$ be a minimum transversal of $P(G)$. Define
$$T \;=\; \bigl(T' \cap V(G)\bigr) \;\cup\; \{w_E : E \in G,\ v_E \in T'\},$$
where $w_E$ is an arbitrarily chosen vertex of $E$ (nonempty since $r\ge3$). Then $|T| \le |T'|$. Every edge $E \in G$ is covered: $T'$ meets $E' = E \cup \{v_E\}$, so either $T'$ meets $E$ at a vertex of $V(G)$ (which is in $T$), or $v_E \in T'$ and then $w_E \in T \cap E$. So $T$ is a transversal of $G$ and $\tau(G) \le |T| \le \tau(P(G))$. $\blacksquare$

**Theorem C.** *$t(r+1) \ge t(r)$ for every $r \ge 3$.*

*Proof.* Let $c < t(r)$ be arbitrary (if $t(r) = \infty$, read: let $c$ be any real; the argument gives $t(r+1) = \infty$). By definition of the supremum there is an $r$-uniform $G$ with $L(r)$ and $\tau(G) > c$. By Lemma 5, $P(G)$ is $(r+1)$-uniform, has $L(r+1)$, and $\tau(P(G)) = \tau(G) > c$. Hence $t(r+1) > c$. As $c < t(r)$ was arbitrary, $t(r+1) \ge t(r)$. $\blacksquare$

**Machine verification.** Part [E] of `verify_616.py`: $P(H_6)$ (7-uniform, 20 vertices) is verified to satisfy $L(7)$ by direct enumeration of all $2^{20}$ vertex subsets, with $\tau = 2$ exhaustively; iterated pendant extensions $P^{k}(H_6)$ up to uniformity 12 are verified via the subfamily criterion.

**Corollary.** $t(r) \ge 2$ for all $r \ge 6$ follows from $t(6) \ge 2$ and Theorem C alone — an independent route to Theorem B for $r>6$ (Theorem B's direct gadget proof does not need it, but the two agree).

## 6. Relation to the literature and to the failed AI attempt; novelty status

**[EHT91]** P. Erdős, A. Hajnal, Zs. Tuza, *Local constraints ensuring small representing sets*, J. Combin. Theory Ser. A **58** (1991) 78–84, doi:10.1016/0097-3165(91)90074-Q — the source of the bounds displayed on the problem page:
$$\frac{3}{16}r+\frac{7}{8}\;\le\; t \;\le\; \frac{1}{5}r.$$
**Update 2026-08-04: the paper was obtained and read** (Elsevier open-archive scan; verbatim quotes in `NOVELTY.md`). The displayed sandwich above is the *problem page's paraphrase* and drops a floor and a ceiling; the paper's actual statements are:

* **Upper bound (Theorem 3, p. 80, all $r\ge3$, no restriction):** $(3r-3,1)\to_r\lceil r/5\rceil$, i.e. $t(r)\le\lceil r/5\rceil$. In particular $t(r)\le 1$ for $r\le 5$ — so Theorems A–C's small-$r$ values are **implicit in [EHT91]**, though never stated there (the paper evaluates no small cases).
* **Lower bound (p. 80):** $t(r)\ge\lfloor\tfrac{3}{16}r+\tfrac78\rfloor$, via the Section-3 construction $H(r,k,q)$ ($x=\lfloor 3r/16-1/8\rfloor$, $q=2x+1$, $k=3x+1$, $\tau=x+1$). At $r=6$ this equals $2$: Theorem B agrees with [EHT91] there and our Theorem A pins the threshold from the other side.
* The floorless paraphrase is internally inconsistent for all $r<70$ (at $r=5$ it reads $1.8125\le t\le 1$); the actual floored/ceilinged statements are consistent for all $r$. An erratum against the problem-page background is filed separately.

**Priority status (resolved).** [EHT91] does not record $t(r)=1$ for $r\le5$ explicitly (it is an immediate corollary of their Theorem 3); Theorems A–C are the first explicit statement, with elementary self-contained proofs by a different method and machine certificates. This finding's framing is therefore: *explicit recording + independent verification-grade proofs*, not discovery of results beyond the 1991 technology.

**The January 2026 AI attempt.** On 18 Jan 2026, forum user **jkabrg** posted to the problem's discussion thread a ChatGPT 5.2 Pro proof attempt (link: https://chatgpt.com/s/t_696d3f4ce56c81918a918ff6a87eae54) claiming $t(r)=1$ for $r=3,4,5$ and $t(r)=2$ for all $r \ge 6$. **TerenceTao** replied that "ChatGPT 5.2 Pro locates multiple issues with the claimed proof, including that the final answer contradicts known bounds, and that the key claim in Step 4 is both unjustified and false in general", and **Nat Sothanaphan** noted "$t(r) = 2$ for $r \ge 6$ isn't possible because it's inconsistent with the [EHT91] result above." (All quotes verbatim from the archived thread, `sources/erdosproblems_616_forum_2026-08-03.html`.)

Relation to this write-up: the *upper-bound claim for $r\ge6$* was the fatal error and is **not used or claimed here** — indeed Lemma 2(3) shows minimal witness families can span up to $\approx (r+2)^2/4$ vertices, escaping every window, which is exactly the room the [EHT91] linear-in-$r$ lower-bound construction exploits. The salvageable ingredients — the span-counting mechanism behind Theorem A and the 4-edge gadget behind Theorem B — appear in that transcript (per the recon record of it; the transcript is JS-rendered and could not be re-fetched at write-up time). They are **re-derived independently and proved in full here**, with the following additions not in the transcript: the exact subfamily-criterion equivalence (Lemma 1) including the infinite case (Remark 2), the sharpness LP certificate (Remark 1), the monotonicity theorem (Theorem C / Lemma 5, giving $\tau(P(G)) = \tau(G)$ exactly, with no criticality hypothesis), and the full machine verification with negative controls. Credit for first proposing the gadget and the span-count route in this context belongs to the transcript posted by jkabrg.

**Novelty search performed (2026-08-03/04):** erdosproblems.com/616 page + all 5 forum comments (archived here); Semantic Scholar citation scan of [EHT91] (8 citing works, none post-2021, none on the $s=1$/vertex-local problem — per recon record); arXiv full-text searches for "local constraints ensuring small representing sets", Kostochka/Fon-Der-Flaass "property (p,2)" line (which concerns the *edges-local* variant "every $p$ edges have a cover of size 2", a different parameterization); SciNet search "Erdos 616" (0 hits). No record of exact values $t(3),t(4),t(5)$ or of the threshold statement was found anywhere except the (retracted-in-discussion) transcript above.

## 7. What remains open

* **$t(6)$:** we now know $t(6) \ge 2$; is $t(6) = 2$? By Lemma 2 and Lemma 3-style arithmetic, at $r=6$ every minimal empty-intersection family either fits in a window ($m \ne 4$, span $\le 15$) or is forced into the rigid $m=4$, span-exactly-16 gadget pattern; a $\tau \ge 3$ example must therefore be densely packed with interlocking copies of $H_6$. This looks finitely attackable (SAT/ILP over bounded configurations) but needs a compactness/critical-subfamily reduction first; not attempted here for budget reasons.
* **Exact $t(r)$ for $7 \le r$:** the gap between $\lceil 3r/16 + 7/8 \rceil$-type lower bounds and $r/5$ upper bounds is fully open; the displayed constants have not moved since 1991.
* **Reading [EHT91]:** required to settle the priority question of §6 and to learn the exact original bound statements.

## References

* [Er99] P. Erdős — source reference as tagged on erdosproblems.com/616 (list "Some of my favourite problems", 1999; per the problem page).
* [EHT91] P. Erdős, A. Hajnal, Zs. Tuza, *Local constraints ensuring small representing sets*, J. Combin. Theory Ser. A **58** (1991) 78–84. doi:10.1016/0097-3165(91)90074-Q.
* T. F. Bloom, Erdős Problem #616, https://www.erdosproblems.com/616, accessed 2026-08-03 (archived in `sources/`).
* Forum thread for #616 (comments by jkabrg, TerenceTao, Nat Sothanaphan, old-bielefelder, 18 Jan 2026), archived in `sources/erdosproblems_616_forum_2026-08-03.html`.
* ChatGPT 5.2 Pro transcript posted by jkabrg: https://chatgpt.com/s/t_696d3f4ce56c81918a918ff6a87eae54 (JS-rendered; content known via the recon record).
