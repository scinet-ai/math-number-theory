# The case $(k_1,k_2)=(6,4)$ of Erdős problem #388

**Statement of the problem case.** Erdős #388 asks, for positive integers
$m_1,m_2,k_1,k_2$ with $k_1,k_2>3$ and $m_1+k_1\le m_2$ (two disjoint blocks of at
least four consecutive integers, the first entirely below the second), for the
solutions of
$$(m_1+1)(m_1+2)\cdots(m_1+k_1) \;=\; (m_2+1)(m_2+2)\cdots(m_2+k_2).$$
Here we resolve the length pair $(k_1,k_2)=(6,4)$ completely. Write $x=m_1$,
$y=m_2$; the equation is

$$(x+1)(x+2)(x+3)(x+4)(x+5)(x+6) \;=\; (y+1)(y+2)(y+3)(y+4). \tag{E}$$

**Theorem.** The only solution of (E) in positive integers is $(x,y)=(1,6)$,
i.e. $2\cdot3\cdot4\cdot5\cdot6\cdot7 = 7\cdot8\cdot9\cdot10 = 5040$. Its blocks
$\{2,\dots,7\}$ and $\{7,\dots,10\}$ share the element $7$, so it violates the
disjointness condition $m_1+k_1\le m_2$ (here $m_1+k_1=7 > 6=m_2$). Consequently
**Erdős #388 has no solution with $(k_1,k_2)=(6,4)$.**

*Completeness disclosure (what tool proved what):* the proof below reduces (E) to
the determination of all integral points on the elliptic curve
$E:\,u^2=t^3+10t^2+24t+1$ (LMFDB curve **10388.b1**). Integral-point completeness
is established by **SageMath 10.7** (`case64_sage.sage` in this workspace):
`E.gens(proof=True)` returns a certified Mordell–Weil basis $(-4,1),(-6,1)$ with
certified rank bounds $(2,2)$ and trivial torsion, and `E.integral_points()`
(the provably complete elliptic-logarithm/Pethő–Zimmer-style method, complete
given a full Mordell–Weil basis) returns exactly fourteen points. This is
cross-checked three ways: (i) the LMFDB entry for 10388.b1 lists the identical
fourteen points; (ii) an independent direct search over $-10\le t\le 10^7$
(`case64_reduction.py`) finds exactly the same list; (iii) a direct search of
(E) itself for $x \le 2\cdot 10^6$ finds only $(1,6)$. Every remaining step is
proved below and verified symbolically by `case64_reduction.py`.

## 1. Two polynomial identities

**Lemma 1.** For all $x$: with $t = x^2+7x+6$,
$$(x+1)(x+2)(x+3)(x+4)(x+5)(x+6) = t(t+4)(t+6).$$

*Proof.* Pair the factors symmetrically:
$(x+1)(x+6)=x^2+7x+6=t$, $(x+2)(x+5)=x^2+7x+10=t+4$, $(x+3)(x+4)=x^2+7x+12=t+6$.
$\square$

**Lemma 2.** For all $y$: with $u = y^2+5y+5$,
$$(y+1)(y+2)(y+3)(y+4) + 1 = u^2.$$

*Proof.* $(y+1)(y+4)=y^2+5y+4=u-1$ and $(y+2)(y+3)=y^2+5y+6=u+1$, so the product
is $(u-1)(u+1)=u^2-1$. $\square$

Both identities are also verified by symbolic expansion (sympy) in
`case64_reduction.py` (output: `identity ... : True`).

## 2. Reduction to an elliptic curve

Suppose $(x,y)$ is a solution of (E) in positive integers, and set
$t=x^2+7x+6$, $u=y^2+5y+5$ (both positive integers). By Lemmas 1 and 2,
$$t(t+4)(t+6) = u^2-1, \qquad\text{i.e.}\qquad u^2 = t^3+10t^2+24t+1. \tag{C}$$
So every solution of (E) gives an integral point $(t,u)$ on the elliptic curve
$$E:\; u^2 = t^3 + 10t^2 + 24t + 1,$$
subject to the two constraints
$$4t+25=(2x+7)^2 \text{ is a perfect square},\qquad 4u+5=(2y+5)^2 \text{ is a perfect square},$$
which exactly characterize when $t,u$ arise from integers $x,y$ (solve the
quadratics: $x=\tfrac{\pm\sqrt{4t+25}-7}{2}$, $y=\tfrac{\pm\sqrt{4u+5}-5}{2}$).
Conversely any integral point satisfying the constraints with the sign choices
giving $x,y\ge 1$ yields a solution of (E). The reduction is therefore exact in
both directions.

## 3. The curve and its integral points

For the model $u^2=t^3+10t^2+24t+1$ (i.e. $[a_1,a_2,a_3,a_4,a_6]=[0,10,0,24,1]$)
the standard invariants are
$$\Delta = 41552 = 2^4\cdot 7^2\cdot 53,\qquad c_4=448=2^6\cdot 7,\qquad j = \frac{2^{14}\cdot 7}{53}=\frac{114688}{53}$$
(computed in `case64_reduction.py`). Since $\Delta$ is 12th-power-free, the model
has minimal discriminant. The integral unimodular shift $t = X-3$ transforms the
curve to
$$Y^2 = X^3 + X^2 - 9X - 8$$
(expanded and checked symbolically in `case64_reduction.py`, section 6), which
is the reduced minimal Weierstrass model:
LMFDB curve **10388.b1**, conductor $10388=2^2\cdot 7^2\cdot 53$. Because the
shift $X=t+3$ is integral with integral inverse, it is a bijection between
integral points of the two models.

The Mordell–Weil group is $\mathbb{Z}\oplus\mathbb{Z}$: Sage certifies rank
bounds $(2,2)$, trivial torsion, and a proof-flagged generator pair (on our
model: $(-4,1)$ and $(-6,1)$; LMFDB lists the equivalent pair $(-1,1),(-3,1)$ on
10388.b1). Sage's `integral_points` and the LMFDB entry for 10388.b1 (accessed
2026-08-03) agree that the **complete list of integral points** is
$$X \in \{-3,\,-1,\,3,\,4,\,17,\,41,\,137\},\qquad
(X,Y)=(-3,\pm1),(-1,\pm1),(3,\pm1),(4,\pm6),(17,\pm71),(41,\pm265),(137,\pm1609).$$
Mapping back by $t=X-3$, the complete list of integral points on (C) is
$$(t,u)\in\{(-6,\pm1),\,(-4,\pm1),\,(0,\pm1),\,(1,\pm6),\,(14,\pm71),\,(38,\pm265),\,(134,\pm1609)\}. \tag{L}$$
Our independent brute search over $-10\le t\le 10^7$ (by Lemma 3 below no
integral point has $t\le -7$, so this interval misses nothing on the left)
finds exactly the fourteen points of (L) and no others — a consistency check on
the Sage/LMFDB list, and by itself it already covers all $x \le 3158$ directly
(and $x\le 2\cdot 10^6$ via the direct search of (E)).

**Lemma 3 (no points far left).** If $(t,u)$ is a real point on (C) then
$t > -7$. *Proof.* Write $f(t)=t^3+10t^2+24t+1=t(t+4)(t+6)+1$. For $t\le-7$ all
three factors $t,\,t+4,\,t+6$ are negative with $|t|\ge7$, $|t+4|\ge3$,
$|t+6|\ge1$, so $t(t+4)(t+6)\le-21$ and $f(t)\le-20<0$. Hence $u^2=f(t)$ has no
real solution with $t\le -7$. $\square$

(This is why the brute search interval $[-10,10^7]$ covers all negative
candidates.)

## 4. Filtering the integral points

For each $(t,u)$ in (L) we need $4t+25$ to be a perfect square (else no integer
$x$ exists):

| $t$ | $4t+25$ | square? | integer $x$ candidates $\frac{\pm a-7}{2}$ | $x\ge1$? |
|---|---|---|---|---|
| $-6$ | $1$ | yes, $a=1$ | $-3,\,-4$ | no |
| $-4$ | $9$ | yes, $a=3$ | $-2,\,-5$ | no |
| $0$ | $25$ | yes, $a=5$ | $-1,\,-6$ | no |
| $1$ | $29$ | no | — | — |
| $14$ | $81$ | yes, $a=9$ | $1,\,-8$ | **$x=1$** |
| $38$ | $177$ | no | — | — |
| $134$ | $561$ | no | — | — |

The only surviving value is $t=14$, $x=1$. Then $u=\pm71$; since $y\ge1$ forces
$u=y^2+5y+5\ge 11>0$, we need $u=71$: $4u+5=289=17^2$, $y=\frac{17-5}{2}=6$
(the other sign gives $y=-11<1$). So $(x,y)=(1,6)$ is the unique positive
solution of (E). Finally $m_1+k_1 = 1+6 = 7 > 6 = m_2$, so the two blocks are
not disjoint (they share the element $7$), and (E) contributes **no** solution
to Erdős #388. $\blacksquare$

## 5. Novelty and prior work

- Mordell (1963) solved the $(3,2)$ analogue; R.A. MacLeod and I. Barrodale,
  *On equal products of consecutive integers*, Canad. Math. Bull. 13 (1970)
  255–259, proved impossibility for length pairs $(2,4),(2,6),(2,8),(2,12),(4,8),(5,10)$
  — the pair $(6,4)$ is not among them (they gave only numerical evidence in the
  range $\max\le 15$).
- The ratio case (lengths $k$ and $mk$, $m\ge2$; Saradha–Shorey and
  Saradha–Shorey–Tijdeman, 1992–95) does not cover $(6,4)$ since neither length
  divides the other with quotient $\ge 2$ ($6$ is not a multiple of $4$).
- L. Hajdu and R. Tijdeman, *The Diophantine equation $f(x)=g(y)$ for
  polynomials with simple rational roots*, arXiv:2204.12345: their Section 10
  (Theorem 10.1) proves ineffective finiteness for equal products from disjoint
  blocks of bounded size **only when $k\nmid 2\ell$**; for our lengths
  $\{4,6\}$ one has $4\mid 12$, so the pair is *excluded* from their theorem, and
  in any case they produce no explicit solution lists.
- **Prior resolution (found in referee audit, 2026-08-03): the $(6,4)$ pair is
  NOT new.** L. Hajdu and Á. Pintér, *Combinatorial Diophantine equations*,
  Publ. Math. Debrecen 56 (2000), 391–403, already determined all solutions:
  the historical overview of Hajdu–Tijdeman (arXiv:2204.12345, Section 2, p. 6)
  records "Hajdu and Pintér [40] showed that the only positive integer solution
  for $(k,\ell)=(4,6)$ is $(7,2)$" — in their normalization
  $x(x+1)(x+2)(x+3)=y(y+1)\cdots(y+5)$ with $(x,y)=(7,2)$, i.e.
  $7\cdot8\cdot9\cdot10 = 2\cdot3\cdots7 = 5040$, exactly our $(x,y)=(1,6)$.

The Theorem above therefore **agrees with and independently verifies the known
result of Hajdu–Pintér (2000)**; its contribution is a self-contained modern
reduction plus a reproducible SageMath `proof=True` Mordell–Weil/integral-point
certificate, together with the (immediate) corollary that Erdős #388 has no
$(6,4)$ solution. It is *not* the first complete resolution of this length
pair, contrary to an earlier draft of this write-up.

Problem source: T. F. Bloom, Erdős Problem #388,
https://www.erdosproblems.com/388, accessed 2026-08-03 (status: open; statement
verified verbatim on that date: $k_1,k_2>3$, $m_1+k_1\le m_2$).

## 6. Verification

Run `./verify.sh` (step 4/4 covers this case; or run
`.venv/bin/python case64_reduction.py` directly): it re-checks both polynomial
identities symbolically, recomputes the curve invariants, re-runs the
$t\le 10^7$ integral-point search, applies the filter, verifies the transform
to 10388.b1 symbolically, and confirms the direct search of (E) to
$x\le 2\cdot10^6$ finds only $(1,6)$. Run `./verify.sh sage` to additionally
re-run the Sage Mordell–Weil certificate and integral-point computation
(`case64_sage.sage`, requires the `e388sage` conda env).
