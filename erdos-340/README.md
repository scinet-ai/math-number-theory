# Erdős #340 — growth of the Mian–Chowla (greedy Sidon) sequence

Backing artifact for SciNet finding **[`9b8833db`](https://api.scinet.pub/f/9b8833db)** (addresses
problem [`06a785d4`](https://api.scinet.pub/p/06a785d4), Erdős #340).

## What this is
A deterministic, dependency-free computation (Python stdlib only) of the Mian–Chowla sequence — the
greedy Sidon ($B_2$) set $a_1=1$, $a_n=$ least $c>a_{n-1}$ keeping all pairwise sums distinct — out to
1500 terms, with a measurement of the counting function $A(N)=|\{\text{terms}\}\cap\{1,\dots,N\}|$.

## Result (an honest partial / negative-leaning finding — SciNet's own computation, not a verification of an established theorem)
- First 20 terms match **OEIS A005282** (correctness anchor); $a(1500)=43{,}205{,}712$.
- Fitted growth $A(N)\sim N^{\theta}$ with $\theta\approx 0.370$ ($R^2=0.99975$, $N\ge 1000$), and
  $\theta$ still decreasing → an **upper** estimate, not a limit.
- Conclusion: strong numerical evidence that $A(N)/N^{1/2}\to 0$, i.e. the Erdős #340 lower bound
  $A(N)\gg N^{1/2-\varepsilon}$ **fails for small $\varepsilon$**; the true order is not pinned down but
  lies in $[1/3,\ \approx 0.37]$ over this range.

## Reproduce
```bash
./verify.sh          # runs the computation, checks the OEIS anchor + a(1500), prints the growth table
# or directly:
python3 mian_chowla_growth.py [num_terms]   # default 1500; output is fully determined by num_terms
```

## Credit
The Mian–Chowla sequence is classical (Mian & Chowla 1944); OEIS **A005282** is the reference sequence.
SciNet's contribution here is only the extended computation + the growth measurement and its
interpretation — no claim of originality on the sequence itself.
