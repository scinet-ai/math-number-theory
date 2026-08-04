# Referee report: KoishiChan's proof of $f(n) \ge (1-o(1))\log_2 n$ (Erdős #963)

**Object refereed.** The forum comment by user **KoishiChan**, posted 00:21 on 05 Dec 2025 in the
Erdős Problem #963 discussion thread (https://www.erdosproblems.com/forum/thread/963), claiming:
every set $A$ of $n$ reals contains a dissociated subset of size $(1-o(1))\log_2 n$.
A verbatim capture of the thread (retrieved 2026-08-03 via the Internet Archive snapshot of
2026-07-09, the live page returning HTTP 403 to our fetcher) is in `caches/thread963.html`
and `caches/thread963.txt`. Thomas Bloom stated in-thread (07:32 on 23 Jan 2026) that the argument
looks good and asked KoishiChan for a formal write-up; as of 2026-08-03 none exists (arXiv and web
searches, see `finding_draft.json`), the statement page still reads OPEN on the latest verifiable
Internet Archive snapshot (2026-07-14; the live page returns HTTP 403 to our fetchers), and an
08 Jun 2026 in-thread question about the status went unanswered. This report is the line-by-line verification that was
requested, plus an effectivization (see `proof_main.md`).

**Verdict: the proof is CORRECT.** Every load-bearing step survives detailed checking. One
off-by-one error (found in-thread by Quanyu Tang, 09:00 on 05 Dec 2025) is real and is repaired by
KoishiChan's own fix (16:52 on 05 Dec 2025); we verify the fix quantitatively below. Three further
points are presentational gaps that a careful write-up must close but that do not threaten the
argument (G1–G3). The full repaired-and-effectivized proof, with all constants explicit, is
`proof_main.md` in this directory.

Throughout, "the post" = KoishiChan's 05 Dec 2025 comment; notation follows it:
$d_d(A)$ = size of the largest dissociated subset of $A$,
$f(n) = \min_{|A|=n} d_d(A)$, $M(\chi) = \sup_r |\sum_{i=1}^r \chi(i)|$.

---

## Verified steps

### V1. The orthogonality/Fourier identity (second-moment lemma, first display chain)

Claim: for prime $q$, $A, B \subseteq (\mathbb{Z}/q\mathbb{Z})^*$ and $r$ uniform on
$(\mathbb{Z}/q\mathbb{Z})^*$,
$$\mathbb{E}_r\, |rA \cap B|^2 \;=\; \frac{1}{(q-1)^2} \sum_{\chi} \Big|\sum_{a\in A}\chi(a)\Big|^2 \Big|\sum_{b\in B}\chi(b)\Big|^2 .$$
**Checked, correct.** $\mathbf 1_{ra=b} = \frac{1}{q-1}\sum_\chi \chi(rab^{-1})$ (orthogonality on
the cyclic group $(\mathbb{Z}/q\mathbb{Z})^*$; needs $a,b,r$ all invertible, which holds — see V5),
and $\mathbb{E}_r\, \chi(r)\chi'(r) = \mathbf 1_{\chi' = \bar\chi}$, which kills all off-diagonal
pairs exactly as the post asserts. Also machine-verified exactly (to $10^{-9}$) for random
instances at $q = 61, 101$: `verify.py --check fourier` (independent implementation via a
primitive root; no character library shared with the proof).

### V2. The AP-to-$M(\chi)$ bound

The post asserts $|\sum_{b\in B}\chi(b)| \le 2M(\chi)$ for $B = B_{p,i} = \{px+i : 1\le x\le X\}$.
This needs an argument, since $B$ is an AP of common difference $p$, not an interval, and $M(\chi)$
is defined by initial-interval sums. **Checked, correct**, via multiplicativity: for $p$ invertible
mod $q$,
$$\sum_{x=1}^{X}\chi(px+i) = \chi(p)\sum_{x=1}^{X}\chi(x+c), \qquad c := p^{-1}i \bmod q,$$
and $\sum_{x=1}^X \chi(x+c) = \sum_{y \le c+X}\chi(y) - \sum_{y\le c}\chi(y)$ over integers, each
partial sum bounded by $M(\chi)$ (for $\chi \ne \chi_0$ the sup over all $r$ equals the sup over
$r < q$, complete periods summing to zero). So the constant 2 is right. Machine-checked
per-character for random APs at $q=101$: `verify.py --check apbound`.
(A write-up must include this two-line reduction; the post uses it silently.)

### V3. The Montgomery–Vaughan citation — verified against the primary source

The post invokes: "A theorem of Montgomery and Vaughen [sic], 'MEAN VALUES OF CHARACTER SUMS'
(1979)... $\sum_{\chi \ne \chi_0} M(\chi)^4 \ll q^3$."
We pulled the paper (`refs/mv1979.pdf`, first page image `refs/mvp1-01.png`):
H. L. MONTGOMERY AND R. C. VAUGHAN, *Mean values of character sums*, Can. J. Math. **XXXI** (1979),
no. 3, 476–487, DOI 10.4153/CJM-1979-053-2. Its **Theorem 1** reads verbatim:

> THEOREM 1. *For any real $k > 0$,*
> $$\sum_{\chi \neq \chi_0} M(\chi)^{2k} \ll_k \phi(q) q^k$$
> *where the summation is over all non-principal characters modulo $q$.*

With $k=2$: $\sum_{\chi\ne\chi_0} M(\chi)^4 \ll \phi(q)q^2 \le q^3$. **The citation is correct**,
with three remarks: (i) **no log factors** — the post's use is exactly right, with slack
($\phi(q)q^2$ vs $q^3$); (ii) **no primality assumption on $q$** in MV Theorem 1 (relevant to
Tao's almost-prime-$q$ suggestion); (iii) the surname is spelled **Vaughan** (the post's "Vaughen"
is a typo). The implied constant is ineffective-as-published but the proof (Pólya's Fourier
expansion + elementary lemmata, per the paper's §2) is effective in principle; this is the only
non-explicit constant in the whole argument, and it enters our effectivization only through the
threshold $n_0$, not through the shape of the bound.

### V4. Moments, Cauchy–Schwarz, Chebyshev

$\sum_{\chi\ne\chi_0}|S_A(\chi)|^4 \le |A|^2\sum_{\chi\ne\chi_0}|S_A(\chi)|^2 \le q|A|^3$ (Parseval:
$\sum_{\text{all }\chi}|S_A|^2 = (q-1)|A|$); Cauchy–Schwarz combines V2+V3 into
$\sum_{\chi\ne\chi_0}|S_A|^2|S_B|^2 \ll q^2|A|^{3/2}$; variance $\ll |A|^{3/2}$; Chebyshev gives
$$\mathbb{P}\Big(|rA\cap B| \le \tfrac{|A||B|}{2(q-1)}\Big) \ll \frac{(q-1)^2}{|A|^{1/2}|B|^2}.$$
**Checked, correct** (note $\mathbb{E}_r|rA\cap B| = |A||B|/(q-1)$ exactly, so the mean/median
bookkeeping is clean).

### V5. Hypotheses of the lemma in its application; union bound

$A \subset (\mathbb{Z}/q\mathbb{Z})^*$: yes, since $q >$ every element and elements are nonzero
(see G1). $B_{p,i} \subset (\mathbb{Z}/q\mathbb{Z})^*$: yes, all elements in $[1, q-1]$.
$|A| \ge L^{10}$ with $L = pk+1$: $(pk+1)^{10} \le (n^{1/12}\log_2 n + 1)^{10} \le n$ for large
$n$. $|B_{p,i}| \ge q/L$: **holds only when $q$ is large compared to $p,k$** (e.g. $q \ge 2p^2k^2$
suffices); the post leaves the largeness of $q$ implicit, but $q$ is a free parameter (any prime
exceeding $\max A$ works for the rest), so this is harmless — flagged as G3. Union bound over the
$p$ residue classes: failure probability $\ll p/L^3 \le 1/(p^2k^3) < 1$ for large $n$. **Correct.**

### V6. The off-by-one and its fix (the $\le q/k$ transport)

Quanyu Tang's objection (09:00, 05 Dec 2025) is correct: with $x \le \lfloor (q-1)/(pk)\rfloor$
the largest element of $B_{p,i}$ is $p\lfloor(q-1)/(pk)\rfloor + i$, which can exceed $q/k$.
KoishiChan's fix (16:52, 05 Dec 2025) — decrease the upper bound on $x$ by 1 — **works**: with
$x \le \lfloor(q-1)/(pk)\rfloor - 1$ and $0 \le i \le p-1$,
$$p\Big(\Big\lfloor\tfrac{q-1}{pk}\Big\rfloor - 1\Big) + i \;\le\; \tfrac{q-1}{k} - p + (p-1) \;=\; \tfrac{q-1}{k} - 1 .$$
Then any $k$ elements from $\bigsqcup_i B_{p,i}$ have every signed sum ($\pm 1, 0$ coefficients)
bounded in absolute value by $k \cdot \frac{q-1}{k} = q-1 < q$, so vanishing mod $q$ implies
vanishing over $\mathbb{Z}$: dissociativity over $\mathbb{Z}$ transfers to
$\mathbb{Z}/q\mathbb{Z}$ for such sets. **The transport step is sound after the fix.** (The fix
costs a factor absorbed into $|B| \ge q/L$, cf. V5.)

### V7. The splicing step (mod $p$)

$\Gamma = \{1, 2, \dots, 2^{\lfloor\log_2 p\rfloor - 1}\}$: signed sums lie in
$[-(2^{\lfloor\log_2 p\rfloor}-1), 2^{\lfloor\log_2 p\rfloor}-1] \subset (-p, p)$ and a nonzero
$\{-1,0,1\}$-combination of distinct powers of 2 is nonzero (lowest-set-bit), so $\Gamma$ is
dissociated mod $p$ with $|\Gamma| = \lfloor \log_2 p\rfloor$. If $D'$ (all elements
$\equiv 0 \bmod p$) is dissociated over $\mathbb{Z}$ and $a_i \equiv i \bmod p$ for $i \in \Gamma$,
then any vanishing signed sum of $D' \cup \{a_i\}$ reduces mod $p$ to a vanishing signed sum on
$\Gamma$, forcing those coefficients to 0, then dissociativity of $D'$ forces the rest to 0.
**Correct** (including the signed-sum version, which is what dissociativity requires — the post's
subset-sum phrasing is equivalent, see Lemma 0 of `proof_main.md`). Machine-checked on random
instances: `verify.py --check splice`.

### V8. The pullback through $r^{-1}$ and the contradiction

Multiplication by $r^{-1}$ is an additive automorphism of $\mathbb{Z}/q\mathbb{Z}$, so it preserves
dissociativity mod $q$; a subset of $A$ dissociated mod $q$ is dissociated over $\mathbb{Z}$ (a
vanishing integer relation would vanish mod $q$). The contradiction structure — assume
$|D'| + |\Gamma| \ge k = d_d(A)+1$, extract $D''$ of size exactly $k$, transport (V6), pull back,
contradict maximality — **is correct**, and yields
$d_d(A) \ge \lfloor \log_2 p\rfloor + d_d(A'_{p,0})$. **Checked.**

### V9. Recursion arithmetic and unrolling

With $p \in [n^{1/12}/2,\, n^{1/12}]$ prime and $k \le \log_2 n$:
$\lfloor\log_2 p\rfloor \ge \frac{1}{12}\log_2 n - 2$ and
$|A'_{p,0}| \ge \frac{n}{2(pk+1)} \ge \frac{n^{11/12}}{4\log_2 n}$ for large $n$ — the post's
claimed recursion
$$f(n) \ge \min\Big(\log_2 n - 1,\ \tfrac1{12}\log_2 n - O(1) + f\big(\tfrac{n^{11/12}}{4\log_2 n}\big)\Big)$$
**is correct** (it uses monotonicity of $f$, see G2). "Iterating, we obtain
$(1-o(1))\log_2 n$" is correct but is the least detailed step of the post; the full unrolling
(done in `proof_main.md`, §6, and numerically cross-checked in `verify.py --check unroll`) gives
the explicit second-order term: the post's parameters yield
$f(n) \ge \log_2 n - \big(\tfrac{1}{2\log_2(12/11)} + o(1)\big)(\log_2\log_2 n)^2$, with
$\tfrac{1}{2\log_2(12/11)} \approx 3.99$.

---

## Gaps found — all minor, all repaired in `proof_main.md`

**G1 (the "standard reduction" to positive integers is stated too strongly).** The post reduces to
$A \subset \mathbb{Z}_{+}$. Reduction from $\mathbb{R}$ to $\mathbb{Z}$ is indeed standard (a
generic $\mathbb{Q}$-linear functional preserves exactly the vanishing patterns of
$\{-1,0,1\}$-combinations; `proof_main.md` §2 proves it). But the further step to *positive*
integers is not available verbatim: flipping the sign of an element preserves dissociativity
patterns, but if $A \supseteq \{x, -x\}$ the flipped *set* loses an element. Repair: the argument
never needs positivity of $A$ — only $0 \notin A$ and $q > 2\max|a|$ (so that $A$ embeds in
$(\mathbb{Z}/q\mathbb{Z})^*$ with distinct residues); the recursive call is on lifted sets in
$[1, q-1]$, which are positive automatically. Cost: at most one element (discarding 0), absorbed
into the error term. Not load-bearing, but a write-up must say it.

**G2 (implicit monotonicity of $f$).** $d_d(A'_{p,0}) \ge f(|A'_{p,0}|) \ge f(\text{lower bound
on } |A'_{p,0}|)$ needs $f$ nondecreasing — true and trivial (any set of size $n' \ge n$ contains
a subset of size $n$), but should be stated.

**G3 (largeness of $q$ is implicit).** See V5/V6: the lemma application needs
$|B_{p,i}| \ge q/L$, which fails for small $q$; since the only other constraint is
$q > \max A$ and $q$ prime, choosing $q \ge 2p^2k^2 + \max A$ (say) settles it. Should be stated.

None of G1–G3 is a mathematical obstruction; each has a one-to-three-line repair, incorporated in
`proof_main.md`.

## Judgement on the in-thread AI attempt (for completeness)

The 23 Jan 2026 comment by user "utahisnotastate" (labeled "Gemino Pro 3.5" in the post,
corrected to Gemini 3 Pro by Nat Sothanaphan in-thread) argues from the unjustified premise that
$\{1,\dots,n\}$ is the extremal set; as Terence Tao noted in-thread (05:28, 23 Jan 2026), that
premise is the entire problem. It establishes nothing about general $A$ and is unrelated to
KoishiChan's earlier, correct argument. We concur with Tao's assessment.

## Summary

- The proof of $f(n) \ge (1-o(1))\log_2 n$ posted by **KoishiChan** (05 Dec 2025) is **correct**,
  modulo the in-thread off-by-one fix and the routine repairs G1–G3.
- The Montgomery–Vaughan input is verified against the 1979 paper itself and is quoted correctly
  (indeed with slack).
- The write-up requested by Thomas Bloom on 23 Jan 2026, with all details and an explicit
  second-order error term, is `proof_main.md`; the mathematical content and priority for the
  asymptotic $f(n) \ge (1-o(1))\log_2 n$ belong to KoishiChan.
