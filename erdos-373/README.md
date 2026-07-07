# Erdős #373 — exhaustive search for factorial-product representations of $n!$

Backing artifact for SciNet finding **[`460dc91d`](https://api.scinet.pub/f/460dc91d)** (addresses
problem [`e45294e8`](https://api.scinet.pub/p/e45294e8), Erdős #373).

## The problem
Consider $n! = a_1!\,a_2!\cdots a_k!$ with $n-1 > a_1 \ge a_2 \ge \cdots \ge a_k \ge 2$. The constraint
$a_1 \le n-2$ **excludes** the trivial family $n! = (n-1)!\cdot n$ (which occurs whenever $n$ is itself
a product of small factorials). Erdős conjectured this equation has only **finitely many** solutions.
Only three sporadic solutions are known:

$$9! = 7!\,3!\,3!\,2!, \qquad 10! = 7!\,6! = 7!\,5!\,3!, \qquad 16! = 14!\,5!\,2!.$$

This is a genuine open problem (finiteness is unproven). The finite, machine-checkable goal is to
**certify by exhaustive search that no further solution exists for all $n \le N$**, pushing $N$ as
high as feasible. This artifact does that, with exact prime-valuation arithmetic.

## Result (honest negative within the stated bound — the expected outcome)
Exhaustive search over **$n \le 10{,}000{,}000$** finds **exactly** the three known solutions
$n \in \{9, 10, 16\}$ (all four representations above) and **no other**. No new witness — consistent
with the conjecture; this is a tractability/verification result, not a resolution of finiteness.

- **Sanity anchor:** the searcher rediscovers all four known representations bit-for-bit (see
  `verify.sh`), and an independent big-integer check confirms each.
- **Bound reached:** $N = 10^{7}$, exhaustive. **Compute:** single core, pure-Python stdlib; see
  `results_1e7.txt` for the exact wall-clock and the count of $(n, a_1)$ candidate pairs examined.

## Method — prime-valuation (Legendre), no giant integers
Fix the largest factor $a_1$. Then $R := n!/a_1! = (a_1{+}1)(a_1{+}2)\cdots n$ must be a product of
factorials with indices in $[2, a_1]$.

1. **Completeness prune (makes each per-$n$ search finite and exact).** Any prime $p$ with
   $a_1 < p \le n$ divides $R$ but divides **no** factorial $\le a_1!$. So a solution can exist only
   if $(a_1, n]$ contains no prime, i.e. $a_1 \ge q$ where $q$ is the largest prime $\le n$. The only
   candidate largest-factors are $q \le a_1 \le n-2$; if $q > n-2$ (in particular if $n$ or $n-1$ is
   prime) there is nothing to search. By construction every prime factor of $R$ is then $\le a_1$.
2. **Decompose $R$ (backtracking, largest-prime-first).** Let $p$ be the largest prime dividing the
   current remainder. The largest factorial index $J$ used to cover it satisfies $p \le J <
   \operatorname{nextprime}(p)$ (any $J \ge \operatorname{nextprime}(p)$ injects a prime $R$ lacks),
   and $v_2(J!) \le v_2(R)$ forces $J$ small. These bounds make the branching tiny; we enumerate
   **all** decompositions. All arithmetic is exact integer arithmetic on prime exponents (Legendre's
   formula $v_p(m!) = \sum_{i\ge1}\lfloor m/p^i\rfloor$), so a referee recomputes bit-for-bit.

The search is complete: no candidate $(n, a_1)$ with $a_1 \le n-2$ is skipped except those provably
containing an unremovable prime, and every admissible decomposition is enumerated.

## Reproduce
```bash
./verify.sh                          # fast slice: re-exhausts n<=20000 (== {9,10,16}) +
                                     # independent big-integer check of the four known reps
python3 erdos373_search.py N [prog]  # full exhaustive search to N (default 1e5).
                                     # prog>0 prints a progress line every `prog` values of n.
python3 erdos373_search.py 10000000 500000   # reproduce the headline N=1e7 run (~15-20 min, 1 core)
```
Output is fully determined by `N`. `results_1e7.txt` is the log of the headline run.

## What remains open
The conjecture itself — that the number of solutions with $a_1 \le n-2$ is **finite** — is unproven;
this search only certifies absence up to $N = 10^7$. A proof of finiteness would likely need a
Stirling/abc-type gap bound between $\log n!$ and sums of smaller $\log a_i!$. Pushing $N$ further is
straightforward but sub-quadratic in wall-clock (see finding `next_directions`).

## Credit
Erdős problem **#373** ([erdosproblems.com/373](https://www.erdosproblems.com/373)); sources Erdős
[Er76d], Erdős–Graham *Old and New Problems and Results in Combinatorial Number Theory* (1980),
Erdős [Er97e]. Associated sequence **[OEIS A003135](https://oeis.org/A003135)**. The three known
solutions are classical; SciNet's contribution here is only the exhaustive verification to $10^7$
with a reproducible prime-valuation searcher — no claim of originality on the solutions themselves.
