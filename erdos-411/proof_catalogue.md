# Catalogue theorem: all certificate points $x\le 10^7$, $r\le 40$ for Erdős #411

This document states precisely what the computational sweep proves, relying on the
structural results of `proof_structural_lemmas.md` (cited as **L1**, **T2**, **T3**,
**L4**, **L5**, **L6**). All numerical claims are reproducible via `verify.sh`; the code
is in `code/` and the machine-readable certificates in `certificates/`.

## Definitions

$g(n)=n+\varphi(n)$, $g_0(n)=n$, $g_k=g\circ g_{k-1}$. For integers $x\ge2$, $r\ge1$,
$c\ge2$:

* **raw hit** $(x,r,c)$: $g_r(x)=c\,x$;
* **certificate** $C(x,r,c)$: $g_r(x)=c\,x$ and $\operatorname{rad}(c)\mid g_j(x)$ for
  $0\le j<r$. By **T2**, $C(x,r,c)$ holds iff $g_{k+r}(n)=c\,g_k(n)$ for all $k\ge K$,
  for every $n$ with $g_K(n)=x$; in particular $C(x,r,c)$ implies the eventual relation
  $E(x,r,c)$ of Erdős #411 (with multiplier $c$ in place of $2$).

**Reductions** (each produces certificates from certificates):

* *orbit step*: if $C(x,r,c)$ then $C(g(x),r,c)$ (**T2**, moreover-clause);
* *scaling*: if $C(x,r,c)$ and $\operatorname{rad}(s)\mid g_j(x)$ for $j<r$, then
  $C(sx,r,c)$ with $g_j(sx)=s\,g_j(x)$ (**L4**);
* *power*: if $C(x,r,c)$ then $C(x,jr,c^{\,j})$ (**L5**).

A certificate is **primitive** (relative to the search box) if it is not obtainable by
these reductions from a certificate with smaller $x$ (or smaller $r$ at the same $x$)
inside the box.

## Theorem A (exhaustive catalogue)

**Theorem A.** *Consider the search box $2\le x\le X=10^7$, $1\le r\le R=40$. Within this
box:*

1. *the complete list of raw hits has exactly $N_{\mathrm{raw}}$ elements — no orbit
   iteration overflowed or was truncated, so the enumeration is exhaustive;*
2. *exactly $N_{\mathrm{cert}}$ of them are certificates;*
3. *under the three reductions, the certificates collapse to exactly $N_{\mathrm{prim}}$
   primitive orbits, listed in Table 1;*
4. *consequently, every $n\ge 2$ whose orbit contains a certificate point $x\le X$ of a
   relation with $r\le R$ satisfies one of the catalogued eventual relations; and every
   catalogued certificate proves its eventual relation for all $n$ on its orbit
   (unconditionally, by **T2**).*

*(Numbers from the completed and fully verified $10^7$ sweep — see
`certificates/witnesses.json`: $N_{\mathrm{raw}}=16361$, $N_{\mathrm{cert}}=10536$,
$N_{\mathrm{prim}}=19$, recorded there as `n_raw_hits`, `n_certificates`,
`n_primitive`.)*

**Note on a $10^8$ extension.** A $10^8$ sweep was launched but is not part of this
theorem: its partial outputs (`logs/sweep_1e8_r40/`) contain tens of thousands of
truncated-orbit lines (`T …`) from the 64-bit overflow guard, which triggers for odd
starts $x\gtrsim 2\cdot10^7$ whose orbit values exceed $4.6\cdot10^{18}$ before step 40.
Exhaustiveness at $10^8$ therefore additionally requires completing those truncated
orbits with big-integer arithmetic; rerunning `postprocess.py` alone is NOT sufficient.
No such completion has been done, so all claims here are for $X=10^7$.

**Scope remarks (honesty).**
* The theorem catalogues **certificate points** $x\le X$, not **starts**: an eventual
  relation whose orbit enters the box only at a certificate point $>X$ is out of scope
  (example: the start $1570$ of [St25] has its first certificate point at
  $g_{28}(1570)=18755712>10^7$; its relation is nevertheless proved in Theorem B by
  direct verification of that certificate).
* Multipliers are automatically bounded in the box: $c\le(3/2)^{40}\approx1.1\cdot10^7$
  at even $x$ and $c<2^{40}$ in general (**L6**), so no relation is missed for lack of a
  $c$-bound.
* Exhaustiveness is claimed for the stated box only.

**Verification chain** (all rechecked from scratch by `verify.sh`):
1. two independent implementations (C `sweep.c`, pure-Python `probe.py`) produce
   *identical* raw-hit sets on the overlap $x\le10^5$, $r\le25$;
2. every certificate (orbit prefix, $g_r(x)=cx$, radical divisibilities) is re-verified
   by direct iteration in a third, self-contained implementation
   (`verify_certificates.py`, disjoint code);
3. the $(r,c)=(2,2)$ certificate points $\le 8960$ agree exactly with OEIS A383044
   ("Numbers m such that phi(m) + phi(m+phi(m)) = m");
4. every example recorded in the literature is recovered inside the box (see Table 2);
5. consistency with [St25]'s $r=2$ theorem: the odd parts of *all* $(2,2)$-certificate
   points in the box are exactly $\{1,3,5,7,35,47\}$ (his residual branch requires a
   prime odd part $>10^{10}$, outside the box), independently confirming the
   classification in our range.

## Table 1 — primitive orbits, $x\le10^7$, $r\le40$ (list in `certificates/primitive_witnesses.json`)

The 19 primitive orbits of the verified $10^7$ box:

| $x$ | factorization | $r$ | $c$ | status vs literature |
|---|---|---|---|---|
| 4 | $2^2$ | 2 | 2 | classical ($n=2^l$ family head; A383044) |
| 10 | $2\cdot5$ | 2 | 2 | classical (ErGr80; also heads the $2^l\cdot5$, and via $g(10)=14$ the $2^l\cdot7$, families) |
| 70 | $2\cdot5\cdot7$ | 2 | 2 | classical ($2^l\cdot35$; $g(70)=94$ gives the $2^l\cdot47$ family) |
| 738 | $2\cdot3^2\cdot41$ | 4 | 3 | Cambie's example (erdosproblems.com/411) |
| 6075 | $3^5\cdot5^2$ | 20 | 6561 | **new odd orbit-root**; $27\cdot\mathrm{orbit}(6075)$ absorbs [St25]'s 385 |
| 9009 | $3^2\cdot7\cdot11\cdot13$ | 14 | 729 | $=g_2(3393)$: first certificate point of [St25]'s outlier 3393 |
| 11202 | $2\cdot3\cdot1867$ | 4 | 3 | **new orbit**, independent of 738 (no $2^a3^b\le2000$-scaled merge in 200 steps) |
| 11739 | $3\cdot7\cdot13\cdot43$ | 14 | 729 | **new odd entry branch** (merges downstream with the [St25] r=14 class) |
| 12402 | $2\cdot3^2\cdot13\cdot53$ | 25 | 729 | $=g_5(3114)$: first certificate point of Weintraub's 3114 (sharpens $k\ge6$ to $k\ge5$) |
| 13857 | $3\cdot31\cdot149$ | 14 | 729 | **new odd entry branch** (merges with orbit(6969) at 22737) |
| 13890 | $2\cdot3\cdot5\cdot463$ | 4 | 3 | **new orbit**, independent of 738 |
| 15702 | $2\cdot3\cdot2617$ | 25 | 729 | **new orbit-root**: $2\cdot\mathrm{orbit}(15702)$ absorbs [St25]'s 1702; commensurable with 3114, 1570 |
| 28002 | $2\cdot3\cdot13\cdot359$ | 9 | 9 | **new orbit-root**: $3\cdot\mathrm{orbit}(28002)$ absorbs all five [St25] r=9 starts 130,170,234,260,266 |
| 31851 | $3^2\cdot3539$ | 14 | 729 | **new odd entry branch** |
| 42498 | $2\cdot3^3\cdot787$ | 4 | 3 | **new orbit**, independent of 738 |
| 55742 | $2\cdot47\cdot593$ | 4 | 4 | earlier orbit point of Cambie's 148646 ($g_3(55742)=148646$) |
| 74829 | $3\cdot24943$ | 14 | 729 | **new odd entry branch** (merges with orbit(6175) at 316953) |
| 965505 | $3\cdot5\cdot191\cdot337$ | 20 | 6561 | **new odd orbit**; $\mathrm{orbit}(965505)$ meets $9\cdot\mathrm{orbit}(385)$ |
| 1622174 | $2\cdot17\cdot47711$ | 4 | 4 | earlier orbit point of Cambie's 4325798 |

Only six multiplier values occur among primitives:
$c\in\{2,3,4\}\cup\{9,729,6561\}=\{2,3,4,3^2,3^6,3^8\}$, and no primitive relation has
$25<r\le40$ anywhere in the box. (Non-primitive certificates realize exactly the derived
values: powers $c_0^{\,j}$ at $(x,jr_0)$ per **L5**, e.g. $c=531441=729^2$ at $r=28$.)

## Theorem B (proved relations for the recorded empirical examples)

[St25] introduces its examples with "the numbers that eventually **seem** to satisfy";
the erdosproblems.com/411 page records Cambie's as observations. Combining **T2** with
the verified certificates turns all of them into theorems, with sharp onset indices
(least $K$ such that the relation holds for all $k\ge K$, which is sharp by **T2**'s
moreover-clause):

| start $n$ | relation | first certificate point | sharp onset $K$ |
|---|---|---|---|
| 10, 94 | $g_{k+2}=2g_k$ | 10, 94 | 0 |
| 738 | $g_{k+4}=3g_k$ | 738 | 0 |
| 148646, 4325798 | $g_{k+4}=4g_k$ | themselves | 0 |
| 3114 (Weintraub) | $g_{k+25}=729\,g_k$ | $g_5=12402$ | **5** (recorded: $k\ge6$; fails at $k=4$) |
| 130 / 170 / 234 / 260 / 266 [St25] | $g_{k+9}=9g_k$ | $8892342$ (260: $17784684$) | 39 / 39 / 38 / 39 / 37 |
| 385 [St25] | $g_{k+20}=6561\,g_k$ | $g_{13}=251505$ | 13 |
| 1570 [St25] | $g_{k+25}=729\,g_k$ | $g_{28}=18755712$ | 28 |
| 1702 [St25] | $g_{k+25}=729\,g_k$ | $g_{15}=218700$ | 15 |
| 3393 / 6175 / 6969 [St25] | $g_{k+14}=729\,g_k$ | 9009 / 316953 / 22737 | 2 / 7 / 2 |

(Each "first certificate point" is a verified certificate in
`certificates/witnesses.json`; onset sharpness for the boxed points was checked by
direct computation of the failing previous index.)

## Commensurability structure (bounded computational observations)

Write $\mathrm{orbit}(x)\sim s\cdot\mathrm{orbit}(y)$ if the two sets share an element
(checked to 120–200 steps, values $\le10^{17}$–$10^{18}$; these are *bounded* claims).

* **r=9, c=9**: the four [St25] starts 130, 170, 234, 266 funnel into a single orbit
  whose first certificate point is 8892342, which lies on $3\cdot\mathrm{orbit}(28002)$;
  the fifth start 260 $=2\cdot130$ runs exactly $2\times$ that orbit (first certificate
  point $17784684=2\cdot8892342$, on $6\cdot\mathrm{orbit}(28002)$) — one
  commensurability class, generated by the new root 28002.
* **r=25, c=729**: $\mathrm{orbit}(15702)$ meets $3\cdot\mathrm{orbit}(3114)$;
  $2\cdot\mathrm{orbit}(15702)$ meets $\mathrm{orbit}(1702)$;
  $64\cdot\mathrm{orbit}(15702)$ meets $\mathrm{orbit}(1570)$ — one commensurability
  class with 15702 as the smallest known certificate point.
* **r=20, c=6561**: $27\cdot\mathrm{orbit}(6075)$ meets $\mathrm{orbit}(385)$;
  $\mathrm{orbit}(965505)$ meets $9\cdot\mathrm{orbit}(385)$ — one class, root 6075 (odd).
* **r=14, c=729**: the recorded outliers 3393, 6175, 6969 and the new branches 11739,
  13857, 31851, 74829 are all pairwise commensurable via $3$-power scalings; smallest
  certificate point 9009.
* **r=4, c=3**: the four orbits 738, 11202, 13890, 42498 show **no** commensurability
  relation for any scaling $s=2^a3^b\le2000$ within 200 steps (values to $10^{18}$) —
  four independent families, three of them new.

**Interpretation.** Modulo bounded-range commensurability, the entire known solution
set of Erdős #411 in the box is generated by: the three classical $(2,2)$ heads
(4, 10, 70 — equivalently A383044), **four** independent $(4,3)$ orbits, one $(4,4)$
pair of Cambie orbits (55742-root and 1622174-root — commensurability between the two
not found; not exhaustively excluded), and **one commensurability class each** for
$(9,9)$, $(14,729)$, $(20,6561)$, $(25,729)$, all of the latter with $c$ a power of $3$
and all rooted at certificate points first identified here.

## Attribution

Examples and conjectures from the erdosproblems.com/411 page are credited there to
"Selfridge and Weintraub", "Weintraub", and "Cambie" (page thanks "Stijn Cambie"); the
$r=2$ theory and the empirical examples 130, 170, 234, 260, 266, 385, 1570, 1702, 3393,
6175, 6969 are from Stefan Steinerberger, arXiv:2504.08023 [St25]. The values of the
original Selfridge–Weintraub $r=9$ solutions are not listed in the accessible sources
(ErGr80 p. 81 gives no values; [St25] says "all $n$ found were even"); our $(9,9)$-class
novelty claims are therefore phrased relative to the *recorded* examples only.
