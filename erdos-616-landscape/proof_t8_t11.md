# Erdős problem #616 at small uniformities: the exact landscape $t(r)=\lceil r/5\rceil$ for $r\le 20$ from [EHT91], an independent elementary proof for $r\le 12$, and the first genuinely open value $t(21)\in\{4,5\}$

**Status: complete proofs; every lemma proved in full below or cited to a precise
statement of [EHT91] (paper obtained this session, `../sources/EHT91.pdf`); all
finite claims machine-verified from scratch (driver `./verify.sh`).**

**Problem** (Erdős problem #616, statement as displayed at erdosproblems.com/616,
archived in `../sources/`). Let $r\ge 3$. For an $r$-uniform hypergraph $G$ let
$\tau(G)$ denote the covering (transversal) number. Determine the best possible
$t=t(r)$ such that, if $G$ is an $r$-uniform hypergraph in which every subgraph
$G'$ on at most $3r-3$ vertices has $\tau(G')\le 1$, then $\tau(G)\le t$.

We write $L(r)$ for the local hypothesis and *window* for a vertex set of size
$\le 3r-3$. Hypergraphs are $r$-uniform, vertex sets finite or infinite (all
arguments use only finite subfamilies via Lemma 1).

---

## 0. Summary and honest provenance

This session began before we could access the source paper

> [EHT91] P. Erdős, A. Hajnal, Zs. Tuza, *Local constraints ensuring small
> representing sets*, J. Combin. Theory Ser. A **58** (1991) 78–84.

Mid-session the paper was obtained and read in full. Its actual statements are
**stronger and cleaner than the paraphrase displayed on erdosproblems.com**, and
they change the correct framing of everything in this attack series (including the
earlier rounds' results $t(6)=t(7)=2$). We record the corrected state of knowledge
first; our own contributions are then stated against it.

**What [EHT91] actually proves** (§1 below, with page references):

* $t(r)\le\lceil r/5\rceil$ for all $r\ge3$ (their Theorem 3 — the displayed
  "$t\le r/5$" on the problem page omits the ceiling);
* $t(r)\ge t+1$ whenever $r\ge r_0(t):=5t+1+\lfloor(t-1)/3\rfloor$, via their
  Theorem 6(II)/Section 3 construction $H(r,3t+1,2t+1)$ (the displayed
  "$3r/16+7/8\le t$" is the paper's *simplified, weaker* closed form
  $\lfloor\frac{3}{16}r+\frac78\rfloor$, with a floor, from p. 84);
* consequently — although the paper never tabulates it —
  $$\boxed{t(r)=\lceil r/5\rceil\quad\text{for all } 3\le r\le 20,}$$
  and the smallest $r$ for which the results of [EHT91] do **not** determine
  $t(r)$ is $r=21$, with $t(21)\in\{4,5\}$ (machine-verified extraction, §6;
  the full undetermined set below $60$ is $\{21,26,31,36,37,41,42,\dots\}$).

In particular $t(8)=t(9)=t(10)=2$ and $t(11)=3$ — the nominal targets of this
session — were already *determined* (implicitly) by the 1991 paper, as were the
earlier rounds' values $t(r)=1$ ($r\le5$), $t(6)=t(7)=2$. **No exact value below
$r=21$ is new.** The displayed bounds on the problem page, being floorless/
ceilingless, pin none of the values beyond $r\le5$ and create a spurious
small-$r$ inconsistency ($\frac{3}{16}r+\frac78>\frac r5$ for $r<70$); the
earlier write-ups' "internal inconsistency of the displayed sandwich" observation
applies to that rendering only, **not** to the paper (with the floor and ceiling
the sandwich is consistent for every $r$). An erratum note for the problem page
is being prepared separately.

**What this document contributes:**

1. **(§3–4) A new, self-contained, elementary proof of $t(r)=2$ for
   $6\le r\le10$** — a *Fatness Lemma* for minimal empty-intersection families
   (MEIFs) plus a *minimal-MEIF-size chain* argument — methodologically disjoint
   from [EHT91]'s Theorem 6(I) proof (which splits on a minimum pairwise
   intersection), with exhaustive machine certificates over the full survivor
   landscape ($589$ / $46\,668$ / $8\,271\,972$ MEIF type-vectors at
   $r=8/9/10$; zero escape the lemma).
2. **(§5) A self-contained elementary proof of $t(11)=3$ and $t(12)=3$** (upper
   bounds via a sharpened fatness argument; lower bound $=$ the [EHT91] witness
   $H(r,7,5)$, for which we give a short self-contained correctness proof and
   full machine certification — for $H(11,7,5)$ the local property is *tight*:
   minimum bad-subfamily span $31$ against the threshold $31$).
3. **(§6) The rigorous extraction of the $r\le20$ landscape and of the first
   open value $t(21)\in\{4,5\}$,** including: the exact threshold
   $r_0(t)=5t+1+\lfloor(t-1)/3\rfloor$ for the [EHT91] construction (their p. 84
   closed form loses up to one unit of $\tau$: e.g. at $r=16$ it yields only
   $t(16)\ge3$, while the construction itself gives $t(16)\ge4=t(16)$); a proof
   that the *entire* $H(r,k,q)$ family fails at $r=21$ for $\tau\ge5$; and the
   razor-thin diagnostics ($p(21,4)=61=(3\cdot21-3)+1$).
4. **(§7) Structure theory at the jump $r=11$:** exactly $10$ labeled MEIF
   type-vectors at $(r,m)=(11,4)$ are "3-fat" (all pairwise intersections
   $\ge3$); every $\tau\ge3$ example at $r=11$ must contain $4$-edge MEIFs and
   all of them must be 3-fat; the witness $H(11,7,5)$ realizes exactly this
   structure. This explains *why* $t$ jumps at $11$ and gives the template for
   attacking $t(21)$.

Everything below is proved from first principles except where a statement is
explicitly credited to [EHT91]; all machine artifacts are in this directory.

## 1. What [EHT91] states (exact citations)

Notation of the paper: $(p,s)\rightarrow_r t$ means: every $r$-uniform set system
$\mathcal F$ in which every subsystem on at most $p$ elements has $\tau\le s$
satisfies $\tau(\mathcal F)\le t$. Thus $t(r)$ is the least $t$ with
$(3r-3,1)\rightarrow_r t$. Their results used here:

* **Theorem 3 (p. 80).** *For $r\ge3$, $(3r-3,1)\rightarrow_r\lceil r/5\rceil$.*
  (Derived from their Theorem 6(I) via the check $p(r,\lceil r/5\rceil)\le3r-3$,
  where $p(r,t,m)=\lceil m/t\rceil(r-m-t)+2r-m$ and
  $p(r,t)=\max_{1\le m\le r-1}p(r,t,m)$; we machine-verified this inequality for
  $3\le r\le60$, `eht_landscape.py`.)
* **Theorem 6 (p. 83).** *Suppose $p(r,t)=p(r,t,m)$. Then
  $(\max\{3r-3,\,p(r,t)\},1)\rightarrow_r t$, and
  $\bigl(p(r,t)-\lfloor\frac{t(t-1)}{m+2t-1}\rfloor-1,\,1\bigr)\nrightarrow_r t$.*
* **Section 3 (p. 82), the system $H(r,k,q)$** ($q<r$, $q<k<2q$): a central set
  $M$, $|M|=k$; for each $q$-subset $Y\subseteq M$ exactly one $r$-edge
  $H_Y\supseteq Y$ with $H_Y\cap M=Y$ and the parts outside $M$ pairwise
  disjoint. "Trivially $\tau(H(r,k,q))=k-q+1$." **Lemma 5/5′ (pp. 82–83)** lower
  bounds the span of empty-intersection subsystems; at $(k,q)=(3t+1,2t+1)$ it
  evaluates to $4(r-q)+q+\lceil q/3\rceil$.
* **p. 84, closing remark:** taking $x=\lfloor\frac{3}{16}r-\frac18\rfloor$,
  $q=2x+1$, $k=3x+1$ gives an $\mathcal F$ with the $(3r-3)$-local property and
  $\tau=x+1$, i.e. $t(r)\ge\lfloor\frac{3}{16}r+\frac78\rfloor$ — the source of
  the problem page's lower bound, *described in the paper itself as "a somewhat
  weaker lower bound"* than Theorem 6(II). The weakening is real: the p. 84
  estimate bounds the span as $4r-\frac83q\ge3r-2$, discarding the
  $\lceil q/3\rceil-q/3$ ceiling gain, and at e.g. $r\in\{11,16\}$ this loses
  exactly the unit that decides $t(11)=3$, $t(16)=4$.

## 2. Preliminaries: MEIFs (self-contained)

**Lemma 0 (window criterion).** *$G$ satisfies $L(r)$ iff every finite subfamily
$\mathcal F$ of edges with $|\bigcup\mathcal F|\le 3r-3$ has a common vertex.*

*Proof.* ($\Rightarrow$) Put $S=\bigcup\mathcal F$; the subgraph induced on $S$
contains $\mathcal F$ and has $\tau\le1$: some vertex $v$ meets every edge inside
$S$, and a single vertex meets an $r$-set iff it lies in it, so
$v\in\bigcap\mathcal F$. ($\Leftarrow$) For $|S|\le3r-3$, the edges contained in
$S$ form a subfamily with union $\subseteq S$; if nonempty, its common vertex is
a $1$-transversal of $G[S]$; if empty, $\tau(G[S])=0$. $\blacksquare$

**Definition.** A family $E_1,\dots,E_m$ ($m\ge2$) of $r$-sets is a *minimal
empty-intersection family* (MEIF) if $\bigcap_iE_i=\emptyset$ while every proper
subfamily has nonempty intersection.

**Lemma 1 (finitization).** *If a family of $r$-sets has no common vertex, it
contains an MEIF of size $\le r+1$.*

*Proof.* Fix an edge $E_1$; for each $v\in E_1$ pick $F_v$ with $v\notin F_v$;
then $\{E_1\}\cup\{F_v\}$ has empty intersection and $\le r+1$ members; take an
inclusion-minimal empty-intersection subfamily (size bound from Lemma 2).
$\blacksquare$

**Lemma 2 (structure).** *For an MEIF $E_1,\dots,E_m$ of $r$-sets: (1) for each
$i$ there is $x_i\in(\bigcap_{j\ne i}E_j)\setminus E_i$, and the $x_i$ are
pairwise distinct; (2) $m\le r+1$.*

*Proof.* (1) $\bigcap_{j\ne i}E_j\ne\emptyset$ by minimality; were it inside
$E_i$, the full intersection would be nonempty. For $i\ne i'$: $x_i\notin E_i$
but $x_{i'}\in E_i$. (2) $x_2,\dots,x_m$ are distinct elements of $E_1$.
$\blacksquare$

**Lemma 3 (types, span identity, size range).** *Let $E_1,\dots,E_m$ be an MEIF
of $r$-sets with span $V=\bigcup_iE_i$. For $\emptyset\ne T\subseteq[m]$ let
$c_T=\#\{v:\{i:v\in E_i\}=T\}$. Then:*

1. *$\sum_{T\ni i}c_T=r$ for every $i$; $c_{[m]}=0$;
   $c_{[m]\setminus\{i\}}\ge1$ for every $i$.*
2. *(Span identity) $|V|=mr-D$ where $D:=\sum_T(|T|-1)c_T$.*
3. *$|V|\le m(r-m+2)$ and $m(r-m+2)-(3r-3)=(m-3)((r-1)-m)$; hence an MEIF with
   span $>3r-3$ has $3<m<r-1$.*

*Proof.* (1) Immediate; $x_i$ has type exactly $[m]\setminus\{i\}$. (2) Double
counting: $mr=\sum_T|T|c_T$, $|V|=\sum_Tc_T$. (3) The $m$ required types give
$D\ge m(m-2)$, so $|V|\le m(r-m+2)$; the quadratic factors as stated.
$\blacksquare$

**Corollary 4.** *If $G$ satisfies $L(r)$ ($r\ge3$): every two edges intersect,
every three edges have a common vertex, and every MEIF contained in $G$ has span
$\ge3r-2$ and size $4\le m\le r-2$.*

*Proof.* An MEIF of span $\le3r-3$ violates $L(r)$ by Lemma 0; Lemma 3(3) forces
$3<m<r-1$ for the survivors. A disjoint pair is an $m=2$ MEIF of span
$2r\le3r-3$; three edges with no common vertex contain an MEIF of size $2$ or
$3$, of span $\le\max(2r,3r-3)=3r-3$. $\blacksquare$

## 3. The Fatness Lemma

Fix an MEIF $E_1,\dots,E_m$, $m\ge4$, span $\ge3r-2$. For a pair
$\{i,j\}\subseteq[m]$ let
$$I_{ij}:=\bigcap_{k\in[m]\setminus\{i,j\}}E_k .$$
The only types $T\ne[m]$ with $T\supseteq[m]\setminus\{i,j\}$ are
$[m]\setminus\{i,j\}$, $[m]\setminus\{i\}$, $[m]\setminus\{j\}$; writing
$e_i:=c_{[m]\setminus\{i\}}-1\ge0$ and $f_{ij}:=c_{[m]\setminus\{i,j\}}\ge0$,
$$|I_{ij}|=2+e_i+e_j+f_{ij}.\tag{3.1}$$
Call the MEIF **3-fat** if $|I_{ij}|\ge3$ for every pair.

**Lemma F.** *Set $B(m,r):=(m-3)(r-1-m)-1$ and
$\operatorname{mincost}(m):=(m-2)^2+(m-3)$. If
$\operatorname{mincost}(m)>B(m,r)$, then the MEIF is not 3-fat: some pair has
$|I_{ij}|=2$ exactly. Moreover, in all cases*
$$(m-2)\sum_ie_i+(m-3)\sum_{i<j}f_{ij}\;\le\;B(m,r).\tag{3.2}$$

*Proof.* The types $[m]\setminus\{i\}$ (weight $|T|-1=m-2$) and
$[m]\setminus\{i,j\}$ (weight $m-3$) are pairwise distinct, so keeping only
their contributions to $D$:
$D\ge m(m-2)+(m-2)\sum e_i+(m-3)\sum f_{ij}$. The span identity and span
$\ge3r-2$ give $D\le mr-(3r-2)$, and
$mr-(3r-2)-m(m-2)=(m-3)(r-1-m)-1=B(m,r)$: this is (3.2).

If the MEIF is 3-fat, then by (3.1) $e_i+e_j+f_{ij}\ge1$ for every pair: the set
$A=\{i:e_i\ge1\}$ together with $\{\{i,j\}:f_{ij}\ge1\}$ covers the edges of
$K_m$. With $a=|A|$, at least $\binom{m-a}2$ pairs need $f_{ij}\ge1$, so by
(3.2), $B(m,r)\ge g(a):=(m-2)a+(m-3)\binom{m-a}2$ for some $a$. The increments
$g(a+1)-g(a)=(m-2)-(m-3)(m-a-1)$ are $\le0$ precisely for
$a\le m-1-\frac{m-2}{m-3}$, so $g$ is minimized at $a=m-2$ (for $m=4$ also at
$a=1$, same value), with $g(m-2)=(m-2)^2+(m-3)=\operatorname{mincost}(m)$.
Hence $\operatorname{mincost}(m)\le B(m,r)$ — contradiction. $\blacksquare$

**Values.** $\operatorname{mincost}(4,\dots,8)=(5,11,19,29,41)$;
$B(m,r)$ for the admissible sizes $4\le m\le r-2$:

| $r$ | $B(4,r)$ | $B(5,r)$ | $B(6,r)$ | $B(7,r)$ | $B(8,r)$ | $B(9,r)$ |
|----|----|----|----|----|----|----|
| 8  | 2 | 3 | 2 | — | — | — |
| 9  | 3 | 5 | 5 | 3 | — | — |
| 10 | 4 | 7 | 8 | 7 | 4 | — |
| 11 | **5** | 9 | 11 | 11 | 9 | 5 |
| 12 | 6 | **11** | 14 | 15 | 14 | 11 |

For $6\le r\le10$ (rows $r=6,7$: $B=0$ resp. $1,1$) every entry is
$<\operatorname{mincost}(m)$: **no MEIF inside an $L(r)$-graph is 3-fat.** At
$r=11$ the budget first reaches $\operatorname{mincost}$ at $m=4$ (bold), at
$r=12$ also at $m=5$; in closed form, $\operatorname{mincost}(m)>B(m,r)$ iff
$r<m+1+\frac{(m-2)(m-1)}{m-3}$, i.e. up to $r=10,11,13,15$ for $m=4,5,6,7$.

**Remark.** At $r=6$ ($B=0$), (3.2) forces $e\equiv f\equiv0$ and no other
extra types — exactly the $16$-vertex rigid-gadget classification of the earlier
round (`../proofs/proof_t6_t7.md`, Lemma 5).

*Machine verification (two independent routes + failure-power control):*
`classify_fatness.py` exhaustively enumerates **all** survivor type-vectors from
the axioms of Lemma 3(1) for $r=8,9,10$ ($589/46\,668/8\,271\,972$ labeled
vectors; the $r=8$ counts $32/401/156$ match the landscape recorded in the
$t6/t7$ round) and confirms every one has some $|I_{ij}|=2$, cross-checking
(3.1) on explicitly materialized set families (all survivors at $r=8,9$; a
deterministic sample at $r=10$). `independent_check.py` (no shared code)
verifies the covering step by brute force over all binary $(e,f)$ allocations
within budget and re-derives the full $r=8$ landscape by a second enumeration.
Both detectors fire at $(r,m)=(11,4)$ — the silence at $r\le10$ has failure
power.

## 4. The chain theorem: $t(r)=2$ for $6\le r\le10$, independently of [EHT91]

**Theorem 1.** *For $6\le r\le10$, every $r$-uniform $G$ with $L(r)$ has
$\tau(G)\le2$.*

*Proof.* If no edges, $\tau=0$; if all edges share a vertex, $\tau\le1$.
Otherwise $G$ contains MEIFs (Lemma 1), all of size $4\le m\le r-2$ and span
$\ge3r-2$ (Corollary 4). Let $m^\*$ be the **minimum** MEIF size in $G$.

*Claim 1: every $m^\*-1$ distinct edges of $G$ have a common vertex.* An
$(m^\*-1)$-subfamily with empty intersection contains an MEIF of size
$\le m^\*-1$: sizes $2,3$ are impossible (Corollary 4), sizes $4..m^\*-1$
contradict minimality of $m^\*$.

*Claim 2: some $S=I_{ij}$ of a fixed size-$m^\*$ MEIF has $|S|=2$.* By the
Values table, $\operatorname{mincost}(m^\*)>B(m^\*,r)$ throughout
$4\le m^\*\le r-2$, $6\le r\le10$; apply Lemma F.

*Claim 3: $S$ is a transversal.* Let $F$ be any edge. If $F=E_k$, $k\notin
\{i,j\}$, then $F\supseteq I_{ij}=S$. Otherwise $\{F\}\cup\{E_k:k\ne i,j\}$ are
$m^\*-1$ distinct edges; by Claim 1 they share a vertex $v\in F\cap I_{ij}$.

Hence $\tau(G)\le|S|=2$. $\blacksquare$

With the $\tau=2$ witnesses (§5's $H(r,4,3)$, i.e. the "gadget" of the earlier
rounds, machine-certified for $6\le r\le40$ in `../code/verify_616.py` and
literally at $r=8$ in `gadget_check_r8.py`), this re-proves
$$t(6)=t(7)=t(8)=t(9)=t(10)=2$$
**independently of [EHT91]** (whose Theorems 3 + 6(II) also pin these values —
see §6; the two methods are genuinely different: Theorem 6(I) splits on a
minimum pairwise intersection and re-windows; we classify the internal Venn
structure of one extremal MEIF).

**Remark (falsification search).** `search_tau3.py` additionally ran randomized
greedy-maximal $L(8)$-families, $n\le30$: all $24$ trials planted with the three
rigid survivor configurations at $r=8$ ($m=4,5,6$ — the structural regimes a
$\tau\ge3$ example would have to inhabit) completed with $\tau=2$ throughout, as
Theorem 1 predicts (`search_run.log`). The purely unplanted trials of the
original schedule were cut short by a session limit; a reduced unplanted
supplement was rerun separately (appended to the same log). The theorem depends
on none of these searches — they are falsification pressure only.

## 5. $t(11)=3$ and $t(12)=3$, self-containedly

### 5.1 Upper bounds

**Theorem 2.** *Every $11$-uniform $G$ with $L(11)$ has $\tau(G)\le3$; every
$12$-uniform $G$ with $L(12)$ has $\tau(G)\le3$.*

*Proof.* As in Theorem 1, assume a common vertex fails; MEIF sizes lie in
$\{4,\dots,r-2\}$, spans $\ge3r-2$; let $m^\*$ be minimal.

*Case $m^\*\ge6$ ($r=11$: $m^\*\in\{6,\dots,9\}$; $r=12$: $\{6,\dots,10\}$).*
By the Values table ($B(6,11)=11<19$, $B(6,12)=14<19$, and all larger $m$
likewise), Lemma F gives a pair with $|I_{ij}|=2$, and Claims 1/3 of Theorem 1
give $\tau\le2$.

*Case $m^\*=5$ (only possible trouble at $r=12$, where $B(5,12)=11=
\operatorname{mincost}(5)$; at $r=11$, $B(5,11)=9<11$ and Lemma F already gives
$\tau\le2$).* Sum (3.1) over all $\binom52=10$ pairs:
$$\sum_{i<j}|I_{ij}|=20+4\sum e_i+\sum f_{ij}.$$
By (3.2), $3\sum e+2\sum f\le11$, and maximizing $4\sum e+\sum f$ subject to it
gives $\le13$ (at $\sum e=3$, $\sum f=1$). So the ten $3$-wise intersections
$I_{ij}$ have total size $\le33$, and some $|I_{ij}|\le3$. Every $4$ edges of
$G$ share a vertex (Claim 1 with $m^\*=5$), so that $I_{ij}$ — an intersection
of three edges — is a transversal by Claim 3's argument: $\tau\le3$.

*Case $m^\*=4$.* Every $3$ edges share a vertex (Corollary 4), so **every**
pairwise intersection $E_k\cap E_l$ of the MEIF is a transversal of $G$
(any edge $F\notin\{E_k,E_l\}$ shares a vertex with $E_k,E_l$; and
$E_k,E_l\supseteq E_k\cap E_l$). For $m=4$, $I_{ij}=E_k\cap E_l$ where
$\{k,l\}=[4]\setminus\{i,j\}$, so (3.1) applies to pairwise intersections. If
the MEIF is not 3-fat, some $|E_k\cap E_l|=2$: $\tau\le2$. If it is 3-fat, sum
(3.1) over the six pairs: total $=12+3\sum e+\sum f$, and (3.2) reads
$2\sum e+\sum f\le B(4,r)$ ($=5$ at $r=11$, $6$ at $r=12$), so
$3\sum e+\sum f\le\lfloor\tfrac32B(4,r)\rfloor\le9$, total $\le21<24$: some
pair has $|E_k\cap E_l|=3$ exactly, a transversal of size $3$: $\tau\le3$.
$\blacksquare$

*(At $r=13$ this argument genuinely stops: $B(4,13)=8$ admits $e\equiv1$,
giving an $m=4$ MEIF with all six pairwise intersections of size $4$ — "4-fat".
For $13\le r\le20$ we therefore cite [EHT91] Theorem 3 for the upper bounds
$\lceil r/5\rceil$; extending the fatness method to those $r$ is open work.)*

### 5.2 Lower bounds: the [EHT91] system $H(r,3t+1,2t+1)$, verified

**Definition ([EHT91] §3).** $H(r,k,q)$ ($q<k<2q$, $q<r$): central $k$-set $M$;
for each $q$-subset $Y\subseteq M$ one edge $E_Y=Y\cup P_Y$ with the $P_Y$
pairwise disjoint $(r-q)$-sets disjoint from $M$.

**Lemma H.** *Let $t\ge1$, $k=3t+1$, $q=2t+1$. Then:*

1. *$\tau(H(r,k,q))=t+1$.*
2. *$H(r,k,q)$ satisfies $L(r)$ iff $r\ge r_0(t):=5t+1+\lfloor(t-1)/3\rfloor$.
   In particular $H(11,7,5)$ and $H(16,10,7)$ satisfy $L(11)$, $L(16)$ tightly
   (minimum empty-intersection span $=3r-2$ exactly).*

*Proof.* (1) $\tau\le t+1$: any $(t+1)$-subset $T\subseteq M$ leaves
$|M\setminus T|=2t<q$, so every $Y$ meets $T$. $\tau\ge t+1$: let $T$ be a
transversal, $i=|T\cap M|$, $j=|T\setminus M|$, and suppose $i+j\le t$. Each
element off $M$ covers at most one edge, while the edges with
$Y\subseteq M\setminus T$ number $\binom{k-i}{q}\ge\binom{q+j'}{q}$ where
$j'=t-i\ge j$; since $\binom{q+j}{j}>j$ for all $j\ge0$ (and $\ge1$ at $j=0$),
uncovered edges remain — contradiction.

(2) For $\ge2$ edges, intersections happen inside $M$
($\bigcap E_Y=\bigcap Y$), so empty-intersection subfamilies correspond to
families $\{Y_1,\dots,Y_m\}$ of $q$-subsets of $M$ with
$\bigcap Y_i=\emptyset$; the full span is $|\bigcup Y_i|+m(r-q)$. Pass to
complements $Z_i=M\setminus Y_i$ ($t$-sets... in general $(k-q)$-sets; here
$|Z_i|=t$): $\bigcap Y_i=\emptyset\iff\bigcup Z_i=M$, and
$|\bigcup Y_i|=k-|\bigcap Z_i|$. If the $Z_i$ share $c$ common elements, they
cover at most $c+m(t-c)$ elements of $M$, so covering $M$ requires
$c+m(t-c)\ge k=3t+1$; the span is $k-c+m(r-q)$. For $m\le3$:
$mt\le 3t<k$, impossible. For $m=4$: $c+4(t-c)\ge3t+1\iff c\le(t-1)/3$, so the
minimal span over $m=4$ families is $k-\lfloor(t-1)/3\rfloor+4(r-2t-1)$; for
$m\ge5$ the span exceeds this (each extra edge adds $r-q\ge$ the possible gain
in $c$, as $r-q\ge2t+1>t\ge c$ — formally, span $\ge k-(t-1)+m(r-q)$ is
increasing in $m$ and at $m=5$ already exceeds the $m=4$ minimum since
$r-q>t-1$). Realizability at the minimum is direct (fix a $c$-set, spread the
rest). So the minimum empty-intersection span equals
$$3t+1-\Bigl\lfloor\frac{t-1}3\Bigr\rfloor+4(r-2t-1),$$
and $L(r)\iff$ this is $\ge3r-2\iff r\ge5t+1+\lfloor(t-1)/3\rfloor$.
For $t=2$: $r_0=11$, minimum span $=4r-13=31$ at $r=11$ (threshold $3r-2=31$:
tight). For $t=3$: $r_0=16$, minimum span $4r-18=46$ at $r=16$ ($3r-2=46$:
tight). $\blacksquare$

*Machine certification* (`witness_t11.py`): for $H(r,7,5)$, $r=11..15$ — all
$\binom{21}{m}$, $m\le6$ subfamilies enumerated at the $Y$-level: minimum
empty-intersection span $31/35/39/43/47$, all $\ge3r-2$; $\tau=3$ exactly; for
the flagship $H(11,7,5)$ additionally an independent exact DFS check on the
literal $133$-vertex hypergraph. For $H(r,10,7)$, $r=16..20$: exhaustive
$m\le4$ plus the analytic $m\ge5$ floor; $\tau=4$ exactly. Failure-power
controls: $H(10,7,5)$ and $H(15,10,7)$ are correctly flagged as violating
$L(10)$/$L(15)$ (spans $27<28$, $42<43$) — consistent with $t(10)=2$,
$t(15)=3$.

**Corollary 3.** $t(11)=t(12)=3$ *(upper: Theorem 2; lower: Lemma H with
$t=2$)*, and $t(r)\ge3$ for $r\ge11$, $t(r)\ge4$ for $r\ge16$.

## 6. The exact landscape $r\le20$ and the first open value

**Theorem 4 (extraction from [EHT91] + this work).**
$$t(r)=\lceil r/5\rceil\qquad\text{for all }3\le r\le20.$$
*Sources per range: upper bounds — $r\le10$ Theorem 1 (also [EHT91] Thm 3),
$r=11,12$ Theorem 2 (also Thm 3), $13\le r\le20$ [EHT91] Thm 3. Lower bounds —
$r\le5$ trivial ($t\ge1$); $6\le r\le10$: $H(r,4,3)$ $=$ the $4$-edge gadget
($t=1$ in Lemma H, $r_0(1)=6$); $11\le r\le15$: $H(r,7,5)$; $16\le r\le20$:
$H(r,10,7)$ — all machine-certified.*

**Theorem 5 (first open value).** *The results stated in [EHT91] do not
determine $t(21)$: $t(21)\in\{4,5\}$. Specifically:*

1. *Upper: Theorem 3 gives $t(21)\le\lceil21/5\rceil=5$. Theorem 6(I) at $t=4$
   requires windows of size $p(21,4)=61$, but the available window is
   $3\cdot21-3=60$ — one short.*
2. *Lower: Theorem 6(II) at $t=4$ yields $(59,1)\nrightarrow_{21}4$, again one
   short of $60$. Moreover the **entire** $H(r,k,q)$ family fails: for every
   admissible $(k,q)$ with $k-q\ge4$ (i.e. $\tau\ge5$), $H(21,k,q)$ violates
   $L(21)$ — verified exactly via the complement criterion of Lemma H's proof
   over all $q<21$, $4\le k-q\le9$ (`eht_landscape.py`).*

*The undetermined set below $60$ is
$\{21,26,31,36,37,41,42,46,47,51,52,53,56,57,58\}$ (machine-computed from the
exact thresholds; the gaps widen as $r$ grows, consistent with the asymptotic
slack $3/16<1/5$).*

Deciding $t(21)$ therefore requires either a *new construction idea* (some
$21$-uniform $L(21)$ system with $\tau=5$ not of the $H$ shape) or a *new
upper-bound idea* ($\tau\le4$ from $L(21)$ — e.g. an extension of the fatness
method to "4-fat" configurations). This is, as far as we can determine, the
genuine current frontier of Erdős #616.

## 7. Structure at the jump $r=11$

**Proposition 6.** *Exactly $10$ labeled MEIF type-vectors at $(r,m)=(11,4)$
with span $\ge31$ are 3-fat (none exist for $r\le10$, any $m$; none for
$m\in\{5,\dots,9\}$ at $r=11$). One of them (span $31$):*
$$c_{\{1,2,3\}}=1,\ c_{\{1,2,4\}}=1,\ c_{\{1,3,4\}}=2,\ c_{\{2,3,4\}}=2,\
  c_{\{1,2\}}=1,\ c_{\{i\}}=6\ (i=1,\dots,4),$$
*with pairwise intersection sizes $(3,3,3,3,3,4)$. (Exhaustive enumeration +
explicit materialization, `classify_fatness.py`.)*

**Proposition 7.** *Let $G$ be $11$-uniform with $L(11)$ and $\tau(G)=3$
(such $G$ exist: $H(11,7,5)$). Then $G$ contains a $4$-edge MEIF, every
$4$-edge MEIF of $G$ is 3-fat, and every two edges of $G$ intersect in $\ge3$
vertices.*

*Proof.* If $G$ had no $4$-edge MEIF, the proof of Theorem 2 (cases
$m^\*\ge5$) gives $\tau\le2$. If some $4$-edge MEIF were not 3-fat, a pairwise
intersection of size $2$ would be a transversal ($\tau\le2$). Any two edges
$E,E'$: $E\cap E'$ is a transversal (every third edge meets it, by Corollary
4), so $|E\cap E'|\ge\tau=3$. $\blacksquare$

Indeed in $H(11,7,5)$ two edges intersect in $|Y\cap Y'|\ge2\cdot5-7=3$
vertices, and its $4$-edge MEIFs (e.g. $Y$'s $=$ the $5$-subsets omitting two
of $\{a,b,c,d\}\subseteq M$) realize the 3-fat pattern. The analogous
"$(t+1)$-fat" structural constraints at $r=21$ are the natural starting point
for the $t(21)$ attack.

## 8. Machine verification artifacts

All pure Python 3 stdlib, this directory, driver `./verify.sh` (logs
`*_run.log` from the runs used here):

* `classify_fatness.py` — streaming exhaustive enumeration of all survivor MEIF
  type-vectors for $r=8,9,10$ (all $m$), fatness check on every one (formula
  (3.1) + materialized set families), survivor-count cross-check at $r=8$
  against the previous round, negative control at $(11,4)$ ($10$ 3-fat vectors
  found, one materialized and re-verified).
* `independent_check.py` — independent double-check of the same nonexistence
  claim: exhaustive covering search over binary $(e,f)$ allocations (Lemma F's
  reduction), plus a from-scratch second enumeration of the $r=8$ landscape
  (no shared code; reproduces $32/401/156$, zero 3-fat).
* `gadget_check_r8.py` — the three $r=8$ rigid witnesses certified against the
  literal $L(8)$ definition (complete bitmask sweeps, $2^{24}/2^{25}$ subsets),
  $\tau=2$ exact, planted-bug control.
* `witness_t11.py` — certification of $H(r,7,5)$, $r=11..15$ ($\tau=3$, $L(r)$,
  exhaustive $Y$-level + independent literal DFS check at $r=11$) and
  $H(r,10,7)$, $r=16..20$ ($\tau=4$, $L(r)$); controls $H(10,7,5)$,
  $H(15,10,7)$ correctly rejected.
* `eht_landscape.py` — verification of the Theorem 3 reduction inequality
  ($r\le60$), agreement of the construction threshold $r_0(t)$ with Theorem
  6(II) ($t\le8$), the pinned/undetermined table, and the exhaustion of the
  $H$ family at $r=21$.
* `search_tau3.py` — randomized falsification of Theorem 1 at $r=8$ (exact
  local-property checker; planted and unplanted): $\tau\le2$ throughout.

## 9. Novelty, priority, and corrections

* **Exact values.** $t(r)=\lceil r/5\rceil$ for $r\le20$ is determined by
  [EHT91]'s published theorems (3 and 6(II)), although the paper states no
  table and the problem page's displayed (floorless) bounds pin nothing beyond
  $r\le5$. To our knowledge no explicit record of these values exists anywhere;
  but they should be credited to [EHT91], not claimed as new. This supersedes
  the framing of the earlier rounds in this workspace (`../proof_small_r.md`,
  `../proofs/proof_t6_t7.md`, written before the paper was accessible), whose
  *proofs* remain valid and independent but whose novelty discussions are now
  outdated — including the "displayed sandwich is internally inconsistent"
  observation, which concerns only the problem page's rendering
  ($\tfrac3{16}r+\tfrac78\le t\le\tfrac r5$ without floor/ceiling), not the
  paper. The exact displayed forms should read
  $\lfloor\tfrac3{16}r+\tfrac78\rfloor\le t(r)\le\lceil r/5\rceil$, which is
  consistent for all $r$ (erratum to be filed).
* **New here:** the Fatness Lemma and chain method (independent elementary
  proofs of the exact values for $r\le12$ with exhaustive certificates); the
  tight machine verification of the [EHT91] witnesses (their Lemma 5 is proved
  in the paper only in the weaker 5′ form "in accordance with the referee's
  suggestion" — our exhaustive checks confirm the crucial instances exactly, at
  span $31$ vs. threshold $31$ and $46$ vs. $46$); the exact threshold
  $r_0(t)=5t+1+\lfloor(t-1)/3\rfloor$ with proof; the identification and
  diagnostics of the first open value $t(21)$; and the 3-fat structure theory
  at the jump.
* **The January 2026 forum episode** (AI-generated claim $t(r)=2$ for all
  $r\ge6$, refuted by T. Tao) is doubly dead: $t(11)=3$ already follows from
  the 1991 paper.
* Novelty searches this session (2026-08-04): erdosproblems.com/616 + forum
  (unchanged since 2026-01-18); teorth/erdosproblems wiki (#616 listed only
  under "Incorrect proof found"); arXiv/web searches for the paper title and
  problem — no other post-1991 work on the $s=1$ vertex-local problem found;
  [EHT91]'s citation record (8 works) contains none either (recon scan
  2026-08-03).

## References

* [EHT91] P. Erdős, A. Hajnal, Zs. Tuza, *Local constraints ensuring small
  representing sets*, J. Combin. Theory Ser. A **58** (1991) 78–84.
  doi:10.1016/0097-3165(91)90074-Q. Obtained this session:
  `../sources/EHT91.pdf`.
* T. F. Bloom, Erdős Problem #616, https://www.erdosproblems.com/616
  (archived in `../sources/`).
* Companion write-ups (earlier rounds, independent proofs; novelty framing
  superseded per §9): `../proof_small_r.md`, `../proofs/proof_t6_t7.md`.
