#!/usr/bin/env python3
r"""Exhaustive classification of minimal empty-intersection families (MEIFs)
surviving the local window at r = 8, 9, 10, and verification of the FATNESS
LEMMA that drives the proof of t(8) = t(9) = t(10) = 2 (see proof_t8_t11.md).

Background (see ../proofs/proof_t6_t7.md, Lemmas 0-3):
A family E_1,...,E_m of r-sets is a MEIF if the intersection of all m sets is
empty while every proper subfamily has nonempty intersection.  Up to
isomorphism a MEIF is determined by its Venn-region cardinalities c_T
(T a nonempty subset of [m]); the axioms are
  - uniformity:   sum_{T ni i} c_T = r for every i
  - empty inter:  c_[m] = 0
  - minimality:   c_{[m]\{i}} >= 1 for every i
  - span = sum_T c_T = m*r - D  with  D = sum_T (|T|-1) c_T.
Inside an r-uniform hypergraph with the local property L(r) ("every subgraph
on at most 3r-3 vertices has tau <= 1") every MEIF must have span >= 3r-2
("survivor"), which forces 3 < m < r-1 (proof_t6_t7.md, Lemma 3(4)).

KEY CLAIM CHECKED HERE (machine half of the Fatness Lemma):
  For r in {8, 9, 10}, EVERY survivor type-vector has some pair {i,j} whose
  complementary (m-2)-subfamily {E_k : k != i,j} has intersection of size
  EXACTLY 2.  (Equivalently: no survivor is "3-fat".)
t(r) = 2 for r in {6,...,10} follows via the minimal-MEIF-size chain argument
of proof_t8_t11.md, whose only non-elementary ingredient is this claim.

The (m-2)-wise intersection size is read off the type vector exactly:
  |inter_{k != i,j} E_k| = sum_{T >= [m]\{i,j}} c_T
                         = c_{[m]\{i,j}} + c_{[m]\{i}} + c_{[m]\{j}}
(the only types containing [m]\{i,j} other than the excluded [m] itself).
This identity is additionally verified against explicitly materialized set
families (all survivors at r = 8, 9; a deterministic sample plus extremal
cases at r = 10, where survivors number in the millions).

Also run:
  - cross-check of the r=8 survivor counts against the numbers recorded in
    ../proofs/proof_t6_t7.md (32 at m=4, 401 at m=5, 156 at m=6; total 589);
  - NEGATIVE CONTROL with failure power: at r = 11, m = 4 the same detector
    DOES find 3-fat survivors (the covering budget first suffices there), so
    its silence at r <= 10 is meaningful, not vacuous.

Enumeration core adapted from ../code/classify_minimal.py (referee-checked in
the t6/t7 round), converted to streaming (no survivor list is stored).
"""
import sys
import time
from itertools import combinations

# ----------------------------------------------------------------------------
# Streaming enumeration core (adapted from ../code/classify_minimal.py)
# ----------------------------------------------------------------------------

def nonempty_proper_types(m):
    """All T with 2 <= |T| <= m-1, as frozensets; the m required types [m]\\{i}
    first (search order). Singletons handled implicitly (deficit 0)."""
    req = [frozenset(set(range(m)) - {i}) for i in range(m)]
    rest = []
    for k in range(m-1, 1, -1):
        for T in combinations(range(m), k):
            fT = frozenset(T)
            if fT not in req:
                rest.append(fT)
    return req + rest

def enumerate_survivors(r, m, span_min, visit):
    """Stream all c-vectors (on non-singleton types; singleton counts forced
    by uniformity) satisfying the MEIF axioms with span >= span_min.
    Exact pruning via the identity span = m*r - D, D = sum_T (|T|-1) c_T:
    span >= span_min  <=>  D <= budget := m*r - span_min, and each still-
    unplaced required type [m]\\{i} will add >= m-2 to D.
    visit(counts, D, singles) is called once per solution; `counts` maps each
    non-singleton type to its (positive) multiplicity and must not be retained.
    Returns the number of solutions."""
    budget = m*r - span_min
    if budget < 0:
        return 0
    types = nonempty_proper_types(m)
    n_req = m
    deg = [0]*m
    n_sol = 0

    def rec(idx, counts, D):
        nonlocal n_sol
        req_left = n_req - idx
        if req_left > 0 and D + req_left * (m-2) > budget:
            return
        if idx == len(types):
            singles = [r - d for d in deg]
            assert min(singles) >= 0 and D <= budget
            n_sol += 1
            visit(counts, D, singles)
            return
        T = types[idx]
        w = len(T) - 1
        cap = min(min((r - deg[i]) for i in T), (budget - D) // w)
        lo = 1 if idx < n_req else 0
        for c in range(cap, lo - 1, -1):
            for i in T:
                deg[i] += c
            if c > 0:
                counts[T] = c
            rec(idx + 1, counts, D + w * c)
            if c > 0:
                del counts[T]
            for i in T:
                deg[i] -= c
    rec(0, {}, 0)
    return n_sol

# ----------------------------------------------------------------------------
# Materialization and direct set-level verification
# ----------------------------------------------------------------------------

def materialize(counts, singles, m):
    """Build explicit edges as sets of vertex ids from a c-vector."""
    edges = [set() for _ in range(m)]
    v = 0
    items = sorted(counts.items(), key=lambda kv: (-len(kv[0]), sorted(kv[0])))
    items += [(frozenset({i}), singles[i]) for i in range(m) if singles[i] > 0]
    for T, c in items:
        for _ in range(c):
            for i in T:
                edges[i].add(v)
            v += 1
    return edges, v

def verify_family_sets(edges, r, m, span_min):
    """Direct verification of the MEIF axioms and the survivor condition on
    explicit sets; returns the sorted (m-2)-wise intersection sizes."""
    assert all(len(E) == r for E in edges), "not r-uniform"
    assert not set.intersection(*edges), "intersection of all edges nonempty"
    for i in range(m):
        sub = [edges[j] for j in range(m) if j != i]
        assert set.intersection(*sub), f"(m-1)-subfamily omitting {i} empty"
    assert len(set().union(*edges)) >= span_min, "span below survivor threshold"
    sizes = []
    for i, j in combinations(range(m), 2):
        inter = set.intersection(*[edges[k] for k in range(m) if k not in (i, j)])
        sizes.append(len(inter))
    return sizes

# ----------------------------------------------------------------------------
# Fatness scan per (r, m)
# ----------------------------------------------------------------------------

def scan(r, m, span_min, materialize_every):
    """Enumerate survivors at (r, m); for each, compute all (m-2)-wise
    intersection sizes from the type vector; count 3-fat survivors.
    Materialize + set-verify every `materialize_every`-th survivor (and every
    3-fat one).  Returns (n_survivors, n_3fat, min_size_seen, max_size_seen,
    n_materialized, span_range)."""
    pairs = list(combinations(range(m), 2))
    req = [frozenset(set(range(m)) - {i}) for i in range(m)]
    pairc = {(i, j): frozenset(set(range(m)) - {i, j}) for i, j in pairs}
    stats = {"n": 0, "fat": 0, "min": None, "max": None, "mat": 0,
             "span_lo": None, "span_hi": None}

    def visit(counts, D, singles):
        stats["n"] += 1
        span = m*r - D
        stats["span_lo"] = span if stats["span_lo"] is None else min(stats["span_lo"], span)
        stats["span_hi"] = span if stats["span_hi"] is None else max(stats["span_hi"], span)
        mn = mx = None
        sizes = []
        for (i, j) in pairs:
            s = counts.get(pairc[(i, j)], 0) + counts[req[i]] + counts[req[j]]
            sizes.append(s)
        mn, mx = min(sizes), max(sizes)
        assert mn >= 2, "an (m-2)-wise intersection below the base value 2?!"
        stats["min"] = mn if stats["min"] is None else min(stats["min"], mn)
        stats["max"] = mx if stats["max"] is None else max(stats["max"], mx)
        fat = mn >= 3
        if fat:
            stats["fat"] += 1
        if fat or (stats["n"] % materialize_every == 1) or materialize_every == 1:
            edges, _ = materialize(counts, singles, m)
            set_sizes = verify_family_sets(edges, r, m, span_min)
            assert sorted(set_sizes) == sorted(sizes), \
                "type-vector intersection formula disagrees with explicit sets"
            stats["mat"] += 1

    n = enumerate_survivors(r, m, span_min, visit)
    assert n == stats["n"]
    return stats

def run_r(r, materialize_every, expect_counts=None):
    window = 3*r - 3
    print(f"\n=== r = {r}, window = {window}, survivors need span >= {window+1} ===",
          flush=True)
    tot = fat = 0
    counts = {}
    for m in range(2, r+3):
        t0 = time.time()
        if not (4 <= m <= r-2):
            # Lemma 3(4) says these cannot survive; verify by enumeration anyway.
            n_out = enumerate_survivors(r, m, window+1, lambda c, D, s: None)
            assert n_out == 0, f"unexpected survivor at r={r}, m={m}"
            counts[m] = 0
            continue
        st = scan(r, m, window+1, materialize_every)
        counts[m] = st["n"]
        tot += st["n"]
        fat += st["fat"]
        print(f" m={m}: {st['n']:9d} survivors (spans {st['span_lo']}..{st['span_hi']}); "
              f"(m-2)-wise intersection min={st['min']} max={st['max']}; "
              f"3-fat: {st['fat']}; set-verified: {st['mat']}  "
              f"[{time.time()-t0:.1f}s]", flush=True)
    print(f" [r={r}] total survivors: {tot}; 3-fat survivors: {fat}", flush=True)
    if expect_counts is not None:
        for m, c in expect_counts.items():
            assert counts.get(m, 0) == c, \
                f"r={r} m={m}: expected {c} survivors, got {counts.get(m, 0)}"
        print(f" [r={r}] survivor counts match the recorded t6/t7-round landscape: "
              f"{ {m: counts[m] for m in sorted(expect_counts)} }", flush=True)
    return fat

def negative_control_r11():
    """At r=11, m=4 the covering budget B = 5 equals the min cover cost 5, so
    3-fat survivors MUST appear -- verifying the detector has failure power."""
    r, m = 11, 4
    window = 3*r - 3
    found = []

    def visit(counts, D, singles):
        full = frozenset(range(m))
        sizes = []
        for i, j in combinations(range(m), 2):
            s = (counts.get(full - {i, j}, 0) + counts[full - {i}]
                 + counts[full - {j}])
            sizes.append(s)
        if min(sizes) >= 3:
            found.append((dict(counts), list(singles)))

    n = enumerate_survivors(r, m, window+1, visit)
    print(f"\n=== negative control: r = {r}, m = {m} (window {window}) ===")
    print(f" survivors: {n}; 3-fat survivors: {len(found)}")
    assert found, "expected 3-fat survivors at r=11 m=4 (budget = mincost = 5)"
    counts, singles = found[0]
    edges, _ = materialize(counts, singles, m)
    sizes = verify_family_sets(edges, r, m, window+1)
    assert min(sizes) >= 3
    pretty = sorted(((tuple(sorted(T)), c) for T, c in counts.items()),
                    key=lambda kv: (-len(kv[0]), kv[0]))
    span = m*r - sum((len(T)-1)*c for T, c in counts.items())
    print(f" example 3-fat MEIF at r=11 (span {span}): non-singleton c = {pretty}, "
          f"singletons = {singles}")
    print(f" its pairwise-complement intersection sizes: {sorted(sizes)} (all >= 3)")
    print(" => the 3-fatness detector CAN fire; its silence at r <= 10 is "
          "meaningful.", flush=True)

def main():
    # Recorded r=8 landscape from ../proofs/proof_t6_t7.md, section 4:
    # "32 at m=4 with spans 22..24, 401 at m=5 with spans 22..25,
    #  156 at m=6 with spans 22..24" (total 589).
    fat8 = run_r(8, materialize_every=1, expect_counts={4: 32, 5: 401, 6: 156})
    fat9 = run_r(9, materialize_every=1)
    fat10 = run_r(10, materialize_every=1000)
    for r, fat in ((8, fat8), (9, fat9), (10, fat10)):
        assert fat == 0, f"3-fat survivor at r={r}: Fatness Lemma FALSE"
    negative_control_r11()
    print("\nFATNESS LEMMA MACHINE CHECK PASSED for r = 8, 9, 10 "
          "(every survivor has an (m-2)-wise intersection of size exactly 2)")

if __name__ == "__main__":
    main()
