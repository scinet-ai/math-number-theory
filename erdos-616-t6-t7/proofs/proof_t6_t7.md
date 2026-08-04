# Exact values of the Erdős–Hajnal–Tuza local-to-global covering function: $t(r)=1$ for $r\le 5$ and $t(6)=t(7)=2$

**Problem.** (Erdős problem #616, quoted from erdosproblems.com/616, accessed 2026-08-03.)
Let $r\geq 3$. For an $r$-uniform hypergraph $G$ let $\tau(G)$ denote the covering number
(transversal number), the minimum size of a set of vertices which includes at least one
from each edge in $G$. Determine the best possible $t=t(r)$ such that, if $G$ is an
$r$-uniform hypergraph where every subgraph $G'$ on at most $3r-3$ vertices has
$\tau(G')\leq 1$, we have $\tau(G)\leq t$.

The page displays the bounds of Erdős, Hajnal, and Tuza [EHT91]:
$\tfrac{3}{16}r+\tfrac{7}{8}\leq t \leq \tfrac{1}{5}r$.

**Results proved here.**

* **Proposition 1.** $t(3)=t(4)=t(5)=1$.
* **Theorem 1.** $t(6)=2$.
* **Theorem 2.** $t(7)=2$.

This document is a companion to `../proof_small_r.md` (same workspace, sibling write-up), which proves Proposition 1, the general lower bound $t(r)\ge2$ for $r\ge6$, and the monotonicity $t(r+1)\ge t(r)$ in more detail (with its own machine certificates); overlapping lemmas are re-proved here so that each document stands alone.

All hypergraphs below have edges of size exactly $r$; the vertex set may be finite or
infinite (the proofs cover both). We write $L(r)$ for the local hypothesis: *every
subgraph on at most $3r-3$ vertices has $\tau\le 1$.*

**Remark on consistency with [EHT91]** *(updated 2026-08-04 after obtaining the paper —
see `NOVELTY.md`)*. The floorless sandwich $\tfrac{3}{16}r+\tfrac{7}{8}\le t(r)\le\tfrac15 r$
displayed on erdosproblems.com/616 satisfies lower $\le$ upper **iff $r\ge 70$**, so read
verbatim it is self-contradictory for every $r<70$ — but this is an artifact of the
*paraphrase*, not of the paper. [EHT91]'s actual statements are: **Theorem 3 (p. 80):**
$(3r-3,1)\to_r \lceil r/5\rceil$ for all $r\ge 3$ (a ceiling, no largeness restriction),
and **p. 80:** the lower bound $t(r)\ge\lfloor\tfrac{3}{16}r+\tfrac78\rfloor$ (a floor,
from the Section-3 construction $H(r,k,q)$ with $x=\lfloor 3r/16-1/8\rfloor$, $q=2x+1$,
$k=3x+1$, $\tau=x+1$). With the floor and ceiling restored the bounds are consistent for
all $r$, and they agree exactly with Theorems 1–2 here: at $r=6,7$ both sides equal $2$.
(Stronger still — the t8/t11 round of this session showed that their Theorem 6(II), read
directly rather than through the lossy $\lfloor 3r/16+7/8\rfloor$ closed form, combines
with Theorem 3 to determine $t(r)=\lceil r/5\rceil$ for **all** $3\le r\le 20$; the first
value EHT91 leaves open is $t(21)\in\{4,5\}$. See `t8/proof_t8_t11.md`.) Nothing in this paper contradicts [EHT91]; an erratum
against the problem-page paraphrase is filed separately. One subtlety in the paper
itself: the p. 84 display "$(3r-3,1)\not\to_r\lfloor\tfrac{3}{16}r+\tfrac78\rfloor$" is
off by one against its own construction ($\tau=x+1$ witnesses $\not\to$ of $x$); the
p. 80 phrasing is the intended claim.

---

## 0. The local hypothesis as a statement about subfamilies

**Lemma 0.** $G$ satisfies $L(r)$ **iff** every finite subfamily
$\mathcal F$ of edges with $|\bigcup\mathcal F|\le 3r-3$ has a common vertex.

*Proof.* ($\Rightarrow$) Let $\mathcal F$ be such a subfamily and let $S=\bigcup\mathcal F$,
$|S|\le 3r-3$. The subgraph of $G$ induced on $S$ contains every edge of $\mathcal F$ and
has $\tau\le 1$ by $L(r)$, i.e. some single vertex $v$ meets every edge inside $S$. Since
an $r$-set is met by a single vertex iff it contains it, $v\in E$ for every
$E\in\mathcal F$. ($\Leftarrow$) Let $S$ be any vertex set with $|S|\le 3r-3$. The edges
contained in $S$ form a subfamily with union $\subseteq S$; if it is nonempty, its common
vertex is a transversal of size 1 of the induced subgraph; if it is empty, $\tau=0$.
(If "subgraph" is read as "arbitrary subhypergraph" rather than "induced subgraph" the
condition is unchanged, since $\tau$ can only drop when edges are removed.) $\blacksquare$

Throughout, "window violation" means a finite subfamily with union of size $\le 3r-3$
and **no** common vertex, which by Lemma 0 is exactly a violation of $L(r)$.

## 1. Minimal empty-intersection families (MEIFs)

**Definition.** A family $E_1,\dots,E_m$ ($m\ge 2$) of $r$-sets is a *minimal
empty-intersection family* (MEIF) if $\bigcap_{i=1}^m E_i=\emptyset$ while every proper
subfamily has nonempty intersection.

**Lemma 1 (finitization).** If a family of $r$-sets has no common vertex, then some
subfamily of at most $r+1$ of its edges has no common vertex.

*Proof.* Fix any edge $E_1$. For each $v\in E_1$ there is (by hypothesis) an edge $F_v$
with $v\notin F_v$. Then $\{E_1\}\cup\{F_v: v\in E_1\}$ has empty intersection and at
most $r+1$ members. $\blacksquare$

**Lemma 2 (structure of MEIFs).** Let $E_1,\dots,E_m$ be an MEIF of $r$-sets. Then:

1. For each $i$ there is a vertex $x_i\in\bigl(\bigcap_{j\ne i}E_j\bigr)\setminus E_i$,
   and $x_1,\dots,x_m$ are pairwise distinct.
2. $m\le r+1$.
3. Every finite family with empty intersection contains an MEIF (of size $\le r+1$).

*Proof.* (1) By minimality $\bigcap_{j\ne i}E_j\ne\emptyset$; if it were contained in
$E_i$, the total intersection would be nonempty. Distinctness: $x_i\notin E_i$ while
$x_j\in E_i$ for $j\ne i$. (2) $x_2,\dots,x_m$ are distinct elements of $E_1$, so
$m-1\le r$. (3) Take an inclusion-minimal subfamily with empty intersection (exists by
finiteness); it is an MEIF, and by (2) has $\le r+1$ members. $\blacksquare$

**Lemma 3 (type decomposition, span identity, span bound).**
Let $E_1,\dots,E_m$ be an MEIF of $r$-sets and let $V=\bigcup_i E_i$ (the *span* is
$|V|$). For a vertex $v\in V$ let its *type* be $T(v)=\{i: v\in E_i\}\ne\emptyset$, and
for $\emptyset\ne T\subseteq[m]$ let $c_T=\#\{v: T(v)=T\}$. Then:

1. $\sum_{T\ni i}c_T=r$ for every $i$ (uniformity), $c_{[m]}=0$ (empty intersection),
   and $c_{[m]\setminus\{i\}}\ge 1$ for every $i$ (the vertex $x_i$ of Lemma 2 has type
   exactly $[m]\setminus\{i\}$).
2. (Span identity.) $|V| = mr - D$ where $D:=\sum_T(|T|-1)\,c_T$
   (double counting: $mr=\sum_i\sum_{T\ni i}c_T=\sum_T|T|c_T$ and $|V|=\sum_T c_T$).
3. $D\ge m(m-2)$, hence $|V|\le m(r-m+2)$.
4. $m(r-m+2)-(3r-3) = (m-3)\,\bigl((r-1)-m\bigr)$. Consequently
   $|V|>3r-3$ is possible **only when $3<m<r-1$**, and any MEIF with
   $m\in\{2,3\}\cup\{r-1,\dots,r+1\}$ has span $\le 3r-3$.

*Proof.* (1) is immediate from the definitions and Lemma 2. (3): the $m$ required types
$[m]\setminus\{i\}$ each contribute $|T|-1=m-2$ to $D$, so $D\ge m(m-2)$ and
$|V|=mr-D\le mr-m(m-2)=m(r-m+2)$. (4): the quadratic
$f(m)=m(r-m+2)-(3r-3)=-m^2+(r+2)m-3r+3$ has roots $m=3$ and $m=r-1$, so
$f(m)=(m-3)((r-1)-m)$, which is $>0$ iff $3<m<r-1$; for $m$ outside the open interval,
$|V|\le m(r-m+2)\le 3r-3$. $\blacksquare$

**Corollary 4.** Suppose $G$ ($r$-uniform, $r\ge 3$) satisfies $L(r)$. Then:

1. Every two edges of $G$ intersect, and every three edges of $G$ have a common vertex.
2. If $3\le r\le 5$ then all edges of $G$ have a common vertex, i.e. $\tau(G)\le 1$.
   Hence $t(3)=t(4)=t(5)=1$.

*Proof.* (1) Two disjoint edges span $2r\le 3r-3$ (as $r\ge 3$): a window violation.
Three edges with no common vertex contain an MEIF with $m\in\{2,3\}$ (Lemma 2(3) applied
to the triple); $m=2$ is a disjoint pair (excluded), and an $m=3$ MEIF has span
$\le 3(r-1)=3r-3$ by Lemma 3(3), so the MEIF itself is a window violation. (2) If some
subfamily of $G$ had empty intersection, then by Lemmas 1 and 2(3) $G$ would contain an
MEIF; by Lemma 3(4) with $r\le 5$ there is no integer $m$ with $3<m<r-1$, so every MEIF
has span $\le 3r-3$ — a window violation. Hence all edges share a vertex. Finally
$t(r)\ge 1$ because a single edge has $\tau=1$ and trivially satisfies $L(r)$.
$\blacksquare$

*(Proposition 1 is Corollary 4(2). This recovers, with a complete proof, the correct
"Steps 1–2" fragment of the January 2026 AI-generated attempt posted by forum user
jkabrg; see "Novelty and priority".)*

## 2. $r=6$: rigidity and Theorem 1

**Lemma 5 (rigidity at $r=6$).** Let $G$ be $6$-uniform satisfying $L(6)$. Then every
MEIF contained in $G$ has $m=4$, span exactly $16$, and — after labelling the four
distinguished vertices $X=\{x_1,x_2,x_3,x_4\}$ — has the exact form
$$E_i=(X\setminus\{x_i\})\ \cup\ B_i \qquad (i=1,\dots,4),$$
where $B_1,\dots,B_4$ are pairwise disjoint $3$-sets disjoint from $X$. Consequently
$$E_k\cap E_l = X\setminus\{x_k,x_l\},\qquad |E_k\cap E_l|=2\quad\text{for all }k\ne l.$$

*Proof.* By Lemma 3(4) with $r=6$, an MEIF with span $>15$ must have $3<m<5$, i.e.
$m=4$; and by Lemma 0 an MEIF with span $\le 15$ is itself a window violation, so every
MEIF in $G$ has $m=4$ and span $\ge 16$; by Lemma 3(3), span $\le 4(6-4+2)=16$, so span
$=16$ and $D=mr-16=8=m(m-2)$ exactly. $D=8$ forces the type vector: the four required
types $[4]\setminus\{i\}$ contribute $2$ each (total $8$), so $c_{[4]\setminus\{i\}}=1$
exactly and **no** other type of size $\ge 2$ occurs; uniformity then forces exactly
$6-3=3$ vertices of singleton type $\{i\}$ in each $E_i$ (these are the $B_i$). The
intersection formula follows since the $B_i$ are pairwise disjoint and disjoint from
$X$. $\blacksquare$

*Machine cross-check:* `code/classify_minimal.py` enumerates **all** type vectors of
MEIFs (any $m$ from $2$ to $r+2$) with span $>15$ directly from the axioms in Lemma 3(1)
and confirms: the rigid $m=4$, span-16 vector above is the **unique** survivor, and all
its pairwise intersections have size 2 as stated.

**Theorem 1.** $t(6)=2$: every $6$-uniform hypergraph satisfying $L(6)$ has
$\tau\le 2$, and there is one with $\tau=2$.

*Proof.* **Lower bound.** Take the configuration of Lemma 5 as a standalone hypergraph
$G_0$ on $16$ vertices (the "gadget": $X$ plus disjoint $3$-sets $B_i$). Every proper
subfamily of $\{E_1,\dots,E_4\}$ has a common vertex ($E_i\cap E_j\ni x_k$ for
$k\notin\{i,j\}$), and the only subfamily without one — the whole family — has union of
size $16>15$, so by Lemma 0 $G_0$ satisfies $L(6)$. No single vertex covers all four
edges ($x_i\notin E_i$; each $b\in B_i$ lies only in $E_i$), and $\{x_1,x_2\}$ covers
($x_2\in E_1$, $x_1\in E_2,E_3,E_4$), so $\tau(G_0)=2$.
*(Machine-verified from the literal definition of $L(6)$ over all $58650$ vertex subsets
of size $6..15$, and $\tau=2$ exhaustively: `code/gadget_check.py`.)*

**Upper bound.** Let $G$ satisfy $L(6)$. If all edges share a vertex, $\tau\le 1$.
Otherwise, by Lemmas 1 and 2(3), $G$ contains an MEIF, which by Lemma 5 is a rigid
gadget $E_1,\dots,E_4$ with distinguished set $X$. Put $S:=E_1\cap E_2=\{x_3,x_4\}$.
We claim $S$ is a transversal of $G$. Suppose some edge $F$ satisfies
$F\cap S=\emptyset$. Then $F\cap E_1\cap E_2\subseteq F\cap S=\emptyset$, so the three
edges $F,E_1,E_2$ have no common vertex (note $F\notin\{E_1,E_2\}$ since
$E_1,E_2\supseteq S$), contradicting Corollary 4(1). Hence every edge meets $S$ and
$\tau(G)\le|S|=2$. $\blacksquare$

*Machine cross-check of the key step:* `code/gadget_check.py` also verifies exhaustively
that among all $74613$ possible additional 6-edges $F$ on a 22-vertex ground set
containing the gadget, every $F$ for which $\{E_1,\dots,E_4,F\}$ still satisfies $L(6)$
(there are 489, checked by complete enumeration of all subfamilies, using no lemma at
all) meets $E_1\cap E_2$.

**Remark (stronger structure).** Applying the transversal claim to every pair
$E_k\cap E_l$ shows more: in any $G$ as in the upper-bound proof, *every* edge contains
at least $3$ of the $4$ distinguished vertices $x_i$ of the fixed rigid MEIF (it meets
$X\setminus\{x_k,x_l\}$ for all six pairs $\{k,l\}$, so it misses at most one $x_i$).
Machine-confirmed on the 489 compatible extension edges: $336$ contain exactly $3$ of
the $x_i$ and $153=\binom{18}{2}$ contain all four.

## 3. $r=7$: near-rigidity and Theorem 2

**Lemma 6 (classification at $r=7$).** Let $G$ be $7$-uniform satisfying $L(7)$. Then
every MEIF contained in $G$ has $(m,\text{span})\in\{(4,19),(4,20),(5,19),(5,20)\}$, and
its type vector is the *rigid* one (required types $[m]\setminus\{i\}$ once each,
everything else singletons) either exactly (span $=m(9-m)$, i.e. $20$) or augmented by
**exactly one** extra vertex of a $2$-element type $\{i,j\}$ (span $19$). Consequently:

* (a) if $m=4$: **some** pair $k\ne l$ has $|E_k\cap E_l|=2$ (in the rigid case every
  pair; in the augmented case every pair $\{k,l\}\neq\{i,j\}$, since
  $E_k\cap E_l=X\setminus\{x_k,x_l\}$ for those pairs);
* (b) if $m=5$: for **every** triple $a<b<c$ in $[5]$,
  $E_a\cap E_b\cap E_c=\{x_d,x_e\}$ where $\{d,e\}=[5]\setminus\{a,b,c\}$
  (the extra vertex, when present, lies in only two edges, so it never enters a triple
  intersection; and $x_i\in E_a\cap E_b\cap E_c$ iff $i\notin\{a,b,c\}$).

*Proof.* By Lemma 3(4) with $r=7$: span $>18$ forces $3<m<6$, so $m\in\{4,5\}$; and
Lemma 0 forces span $\ge 19$ for any MEIF inside $G$. By the span identity,
$D=7m-\text{span}$.
For $m=4$: $D\le 28-19=9$, and $D\ge 8$; $D=8$ is the rigid vector (as in Lemma 5, with
singleton counts $7-3=4$); $D=9$ leaves exactly one unit of deficit beyond the required
types, which can only be one extra vertex of type of size 2 (any extra vertex of a
3-element type costs 2). For $m=5$: required types $[5]\setminus\{i\}$ cost $3$ each, so
$D\ge 15$, while $D\le 35-19=16$; $D=15$ is rigid (singleton counts $7-4=3$), $D=16$
adds exactly one vertex of a 2-element type (extra 3-type costs 2, extra 4-type costs
3). Statements (a), (b) now follow by reading off intersections from the type vectors,
exactly as in Lemma 5. $\blacksquare$

*Machine cross-check:* `code/classify_minimal.py` (same exhaustive enumeration, $r=7$,
all $m\le 9$) finds precisely these survivors — $1+6$ labeled type vectors at $m=4$ and
$1+10$ at $m=5$ — and verifies properties (a) and (b) on explicit materialized families.

**Theorem 2.** $t(7)=2$: every $7$-uniform hypergraph satisfying $L(7)$ has
$\tau\le 2$, and there is one with $\tau=2$.

*Proof.* **Lower bound.** The $r=7$ gadget ($X$ plus pairwise disjoint $4$-sets $B_i$,
$E_i=(X\setminus\{x_i\})\cup B_i$, span $20>18$) satisfies $L(7)$ and has $\tau=2$ by
the same argument as in Theorem 1: pairs and triples of its edges intersect in an $x$
vertex, and the only subfamily with no common vertex (all four edges) has union
$20>18$. *(Machine-verified literally over all $988095$ vertex subsets of size $7..18$:
`code/gadget_check.py`.)*

**Upper bound.** Let $G$ satisfy $L(7)$; assume no common vertex (else $\tau\le1$).
By Lemmas 1, 2(3) and 6, $G$ contains an MEIF with $m=4$ or $m=5$.

*Case A: $G$ contains an MEIF with $m=4$.* By Lemma 6(a) choose $k\ne l$ with
$S:=E_k\cap E_l$, $|S|=2$. If an edge $F$ had $F\cap S=\emptyset$ then $F,E_k,E_l$
would have no common vertex ($F\cap E_k\cap E_l=\emptyset$; $F\ne E_k,E_l$ as those
contain $S$), contradicting Corollary 4(1). So $S$ is a transversal: $\tau\le 2$.

*Case B: $G$ contains no MEIF with $m=4$.* Then **every four edges of $G$ have a common
vertex**: a 4-subfamily with empty intersection would contain an MEIF of size $2$, $3$
(impossible: their spans are $\le 18$ by Lemma 3(4), hence they are window violations,
so they cannot occur in $G$ at all) or $4$ (excluded in this case). Fix an MEIF
$E_1,\dots,E_5$ of $G$ ($m=5$, Lemma 6) with distinguished vertices
$X=\{x_1,\dots,x_5\}$.

We claim every edge $F$ of $G$ contains at least four of the five $x_i$. Indeed, let
$\{d,e\}\subseteq[5]$ be arbitrary and let $\{a,b,c\}=[5]\setminus\{d,e\}$. The four
edges $F,E_a,E_b,E_c$ have a common vertex $v$; then
$v\in F\cap(E_a\cap E_b\cap E_c)=F\cap\{x_d,x_e\}$ by Lemma 6(b). Thus $F$ meets
**every** pair $\{x_d,x_e\}$, so $F$ misses at most one element of $X$; as $|X|=5$,
$F$ contains at least four of the $x_i$. (For $F\in\{E_1,\dots,E_5\}$ this is anyway
immediate.)

In particular every edge contains $x_1$ or $x_2$ (missing both would mean missing two
elements of $X$), so $\{x_1,x_2\}$ is a transversal: $\tau\le 2$. $\blacksquare$

## 4. Why the argument stops at $r=7$, and what is next

The engine of both theorems is Lemma 3(4): the *slack* of an MEIF over the window,
$\max\ \text{span}-(3r-3)=(m-3)(r-1-m)$, is at most $1$ for $r=6$ and at most $2$ for
$r=7$, forcing (near-)rigidity. At $r=8$ the surviving sizes are already $m\in\{4,5,6\}$
with slacks $3,4,3$: MEIFs may deviate from rigidity by several extra multi-type
vertices, small pairwise intersections are no longer guaranteed, and the case analysis
changes character. This is consistent with (and explains the mechanism behind) the
linear lower bound $\Theta(r)$ of [EHT91]: for large $r$ the slack grows like $r^2/4$
and rigidity disappears entirely — precisely the gap that sank the January 2026
AI-generated claim $t(r)=2$ for all $r\ge 6$ (refuted on the forum by Terence Tao:
"the key claim in Step 4 is both unjustified and false in general").
Determining $t(8)$ (is it $2$ or $3$?) is the natural next target; the classification
via Lemma 3 remains finite there and the same machinery applies, but with genuinely
more cases: running the same enumeration at $r=8$ (window 21) yields $589$ surviving
labeled type vectors ($32$ at $m=4$ with spans $22..24$, $401$ at $m=5$ with spans
$22..25$, $156$ at $m=6$ with spans $22..24$) versus $1$ at $r=6$ and $18$ at $r=7$ —
a computer-aided case analysis looks feasible but is a genuine project.

## Novelty and priority

* erdosproblems.com/616 (accessed 2026-08-03/04): status **open**, "0 claimed proofs",
  no partial solutions recorded, no exact small values stated beyond the displayed
  sandwich $\tfrac{3}{16}r+\tfrac78\le t\le\tfrac15 r$ attributed to [EHT91].
* Forum thread for #616 (accessed 2026-08-04): five comments, all 18 Jan 2026,
  concerning an AI-generated attempt (posted by user jkabrg; ChatGPT 5.2 Pro transcript)
  claiming $t(r)=2$ for all $r\ge 6$, refuted by Terence Tao. The transcript's correct
  fragments correspond to our Corollary 4(2) ($r\le5$) and the lower-bound gadget; the
  upper bounds $t(6)\le 2$, $t(7)\le 2$ (Lemmas 5–6, Theorems 1–2) do not appear there,
  and no salvage has been posted since.
* [EHT91] = Paul Erdős, András Hajnal, Zsolt Tuza, *Local constraints ensuring small
  representing sets*, J. Combin. Theory Ser. A **58** (1991) 78–84,
  doi:10.1016/0097-3165(91)90074-Q. **Obtained and read 2026-08-04** (Elsevier
  open-archive scan; see `NOVELTY.md` for verbatim quotes). Resolution of the priority
  question: the paper **never states** $t(6)$, $t(7)$, or the small-$r$ values, and
  evaluates no small cases; but $t(6)=t(7)=2$ *follows* from its own displayed results —
  Theorem 3's upper bound $\lceil r/5\rceil=2$ combined with the p. 80 lower bound
  $\lfloor 3r/16+7/8\rfloor=2$ (whose construction conditions we verified to hold at
  $r=6,7$). Theorems 1–2 here are therefore the **first explicit recording** of these
  values, with independent proofs by a method (exhaustive MEIF/rigidity classification)
  not present in [EHT91], and complete machine certificates. The suspicion recorded in
  earlier drafts that the authors "knew a $\tau=2$ example at $r=6$" is confirmed: their
  $H(r,k,q)$ construction at $r=6$ is exactly such an example.
* Web searches (2026-08-03/04): arXiv/Google for the paper title, "Erdős problem 616",
  OpenAlex citation records — no post-1991 work on the $s=1$ local-to-global problem, no
  statement of $t(6)$ found anywhere.

## Verification artifacts

All in `../code/`, pure Python 3 (stdlib only), run via `../verify_t6t7.sh`
(the sibling `../verify.sh` covers the companion small-$r$ pack):

* `classify_minimal.py` — exhaustive enumeration of all MEIF type vectors with span
  $>3r-3$ for $r\in\{6,7\}$, $m\in\{2,\dots,r+2\}$, from the axioms of Lemma 3(1) only
  (the only analytic ingredient is the double-counting identity of Lemma 3(2), used as
  an exact pruning bound); materializes every survivor and re-verifies uniformity,
  empty intersection, minimality, span, and the intersection properties used in
  Theorems 1 and 2. Confirms Lemmas 5 and 6.
* `gadget_check.py` — certifies both lower-bound gadgets against the literal definition
  of $L(r)$ (all vertex subsets) and $\tau=2$ exhaustively; plus the exhaustive
  one-edge-extension check of the key step of Theorem 1 described above.
* `random_maximal_search.py` — falsification attempt with failure power: random
  greedy-maximal $L(r)$-families (gadget planted or not, $n$ up to 24, exact
  DFS local-property checker), verifying $\tau\le 2$ on every family produced. A single
  $\tau\ge3$ family would disprove the theorems; none was found.
* `planted_m5_search_r7.py` — the same falsification attempt seeded with the rigid
  $m=5$ MEIF of Lemma 6 (the Case B configuration of Theorem 2) instead of the 4-edge
  gadget; again $\tau\le 2$ throughout. Incidentally this certifies a second
  lower-bound witness at $r=7$: the rigid $m=5$ configuration itself (span 20)
  satisfies $L(7)$ and has $\tau=2$.
* `checker_crossval.py` — cross-validates the exact DFS local-property checker used
  by the two search scripts against an independent literal-definition oracle (all
  vertex subsets) on 400 unfiltered random families (both $L$-satisfying and
  $L$-violating ones occur, so agreement is two-sided). Added at the referee pass;
  the referee's independent run (separate implementation and seed) also agreed
  400/400, and independently re-derived every other number above (classification
  counts for $r=6,7,8$, the $58650$/$988095$-subset literal gadget checks, a literal
  $988095$-subset check of the $m=5$ witness, and the $74613$-edge extension check
  with its $489 = 336+153$ split).
