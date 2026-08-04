# Exhaustive-search certificate for Erdős #388 up to $10^{36}$

**Claim (verified computational theorem).** Consider blocks of consecutive
positive integers $[s, s+k-1]$ of length $k\ge 4$. If two distinct such blocks
$[s_1,e_1]$, $[s_2,e_2]$ (with $s_1\le s_2$) are **disjoint** in the sense of
Erdős #388, i.e. $e_1 < s_2$ (equivalently $m_1+k_1\le m_2$ with $s_i=m_i+1$,
$e_i=m_i+k_i$), and have equal products
$$\prod_{n=s_1}^{e_1} n \;=\; \prod_{n=s_2}^{e_2} n \;=\; P \;\le\; 10^{36},$$
then
$$P = 17297280 = 8\cdot9\cdot10\cdot11\cdot12\cdot13\cdot14 = 63\cdot64\cdot65\cdot66,$$
i.e. $(m_1,k_1,m_2,k_2)=(7,7,62,4)$. In particular the known sporadic solution
is the **only** solution of Erdős #388 (both lengths $\ge4$, disjoint blocks)
with product up to $10^{36}$.

Witness identity: $8\cdots14 = 17297280 = 2^7\cdot3^3\cdot5\cdot7\cdot11\cdot13$
and $63\cdot64\cdot65\cdot66 = (3^2\cdot7)(2^6)(5\cdot13)(2\cdot3\cdot11) =
2^7\cdot3^3\cdot5\cdot7\cdot11\cdot13$. (Checked by `verify.sh`.)

**Scope notes.**
- The search enumerates blocks with start $s\ge 1$, a superset of the problem's
  $m\ge1 \Leftrightarrow s\ge2$; the unique disjoint collision found has
  $s_1=8$, so the result holds for either convention.
- Overlapping equal-product pairs are *expected* to be infinite (the family
  $n(n+1)\cdots(n^2+n-1)=(n+2)\cdots(n^2+n)$, cf. OEIS A064224); the sweep finds
  exactly the expected overlapping collisions (36 pairs up to $10^{36}$,
  including the trivial $[1..k]=[2..k]$ family and A064224 members
  $5040,\,19958400,\,259459200,\,20274183401472000,\dots$) — a positive control
  that collision detection has failure-power.
- Prior computational record (OEIS A163263, comment, accessed 2026-08-03 via the
  OEIS JSON API; sequence definition allows any lengths $\ge2$, our claim is the
  both-lengths-$\ge4$ sub-case matching Erdős #388): "Gaps between the first
  45000 primes were searched for additional terms, but none were found" —
  upper-block elements below $p_{45000}\approx 5\cdot10^5$, i.e. roughly
  $10^{22}$-equivalent for length-4 upper blocks. This certificate extends the
  verified range to $10^{36}$. The A163263 comment also already records the
  prime-free-upper-block observation ("only the lowest range ... can contain
  prime numbers; the other ranges are in a gap between consecutive primes").

## Method

For each length $k\ge4$, the products $p_k(s)=s(s+1)\cdots(s+k-1)$ are strictly
increasing in $s$; only lengths with $k$-th initial product $\le N$ occur
($k\le 32$ for $N=10^{36}$). All block products $\le N$ are enumerated in
globally sorted order by a $k$-way merge over the per-length streams; equal
values are then adjacent, and every collision group is emitted with each pair
classified DISJOINT ($e_1<s_2$ after ordering) or OVERLAP. All arithmetic is
exact (Python bigints / C `unsigned __int128`; $10^{36}\cdot 33 < 2^{127}$
bounds every intermediate).

Certificate quantities per run: per-length block counts, total count, an
order-independent checksum $\sum p \bmod (2^{61}-1)$, and the full collision
list.

## Two independent implementations

- `sweep.py` — pure Python (bigints, `heapq.merge`).
- `sweep.c` — C (`unsigned __int128`, hand-written binary heap), written
  independently of the Python control flow.

## Results

| $N$ | blocks enumerated | checksum $\bmod\,2^{61}{-}1$ | disjoint collisions | implementations |
|---|---|---|---|---|
| $10^{18}$ | 37 411 | 1319986051451446397 | 17297280 only | Python = C (identical counts, checksum, full collision list) |
| $10^{24}$ | 1 077 935 | 1733539725825114731 | 17297280 only | Python = C (identical) |
| $10^{30}$ | 32 752 361 | 2269460250881301492 | 17297280 only | Python = C (identical, incl. per-$k$ counts and all overlap pairs) |
| $10^{36}$ | 1 017 038 196 | 349154945598101266 | 17297280 only | Python = C (identical counts, checksum, full collision list; C 32 s, Python ~9 min CPU) — `out_c_36.txt`, `out_py_36.txt` |

Raw outputs: `out_py_24.txt`, `out_c_24.txt`, `out_py_30.txt`, `out_c_30.txt`,
`out_c_36.txt`, `out_py_36.txt` in this directory.

## Reproduce

```
./verify.sh          # fast: witness + both implementations at 10^18 and 10^24 + (6,4) checks
./verify.sh full     # adds the 10^30 cross-check (~15 s) and the 10^36 double run (~8 min)
```
