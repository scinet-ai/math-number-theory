#!/usr/bin/env python3
"""
Spot-verification of all recorded cells (independent of the solver AND of the
shifted-family reduction). For every results/sol_r*_k*_n*.json:

  1. family is a valid set of distinct r-subsets of [n], |family| == recorded f;
  2. family is down-closed (shifted) — a property the model enforces;
  3. DIRECT proof that the family contains NO k pairwise disjoint edges, with
     no shifting assumption: an O(|F|) certificate re-verified edge-by-edge
     (spanned vertices < rk, or an explicit <=(k-1)-vertex transversal) when
     one applies, else exhaustive branch-and-prune over the raw edge list.
     This unconditionally certifies the lower bound f(n;r,k) >= |family|;
  4. recorded f, conjectured value, and candidate values are re-derived from
     the binomial formula and must match the log.

Exit code 0 iff every check passes.
"""
import glob
import json
import math
import os
import sys

C = math.comb
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results")


def no_k_disjoint_certificate(edges, k, r):
    """Returns a short human-readable certificate string if `edges` provably
    contains NO k pairwise disjoint edges, else None. Each certificate is an
    unconditional proof, checked exhaustively here:

      union<rk : the edges span fewer than r*k vertices, so k pairwise
                 disjoint r-sets (needing r*k distinct vertices) cannot fit;
      transversal : an explicit set T of at most k-1 vertices hits every
                 edge (verified edge-by-edge); k pairwise disjoint edges
                 would need k distinct T-vertices.
    """
    span = set()
    for e in edges:
        span.update(e)
    if len(span) < r * k:
        return f"union<rk (spans {len(span)} < {r * k} vertices)"
    # greedy transversal: repeatedly take the highest-degree vertex
    from collections import Counter
    remaining = list(edges)
    T = []
    while remaining and len(T) < k - 1:
        cnt = Counter(v for e in remaining for v in e)
        v, _ = cnt.most_common(1)[0]
        T.append(v)
        remaining = [e for e in remaining if v not in e]
    if not remaining and len(T) <= k - 1:
        assert all(any(v in e for v in T) for e in edges)  # re-verify
        return f"transversal (T={sorted(T)} hits every edge)"
    return None


def has_k_disjoint(edges, k):
    """True iff `edges` contains k pairwise disjoint edges.

    Exhaustive branch-and-prune on vertex bitmasks: let v be the smallest
    vertex covered by any available edge; either the matching uses an edge
    containing v (branch over those, keeping only edges disjoint from it),
    or it uses none of them (recurse on the rest). Complete by construction.
    """
    ms = [sum(1 << (v - 1) for v in e) for e in edges]

    def rec(avail, needed):
        if needed == 0:
            return True
        if len(avail) < needed:
            return False
        allbits = 0
        for m in avail:
            allbits |= m
        v = allbits & -allbits  # lowest-labelled covered vertex, as a bit
        with_v = [m for m in avail if m & v]
        without_v = [m for m in avail if not (m & v)]
        # branch 1: the matching uses an edge containing v
        for e in with_v:
            rest = [f for f in without_v if not (f & e)]
            if len(rest) >= needed - 1 and rec(rest, needed - 1):
                return True
        # branch 2: no edge of the matching contains v
        if len(without_v) >= needed and rec(without_v, needed):
            return True
        return False

    return rec(ms, k)


def main():
    recs = {}
    with open(os.path.join(RESULTS, "results.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            recs[(r["r"], r["k"], r["n"])] = r  # last write wins

    ok = True
    nchecked = 0
    for path in sorted(glob.glob(os.path.join(RESULTS, "sol_r*_k*_n*.json"))):
        with open(path) as f:
            sol = json.load(f)
        r, k, n = sol["r"], sol["k"], sol["n"]
        rec = recs.get((r, k, n))
        if rec is None or not rec.get("certified_optimal"):
            continue  # uncertified cells are not claims
        fam = [tuple(sorted(e)) for e in sol["family"]]
        fs = set(fam)
        errs = []
        if len(fs) != len(fam):
            errs.append("duplicate edges")
        if any(len(set(e)) != r or e[0] < 1 or e[-1] > n for e in fam):
            errs.append("invalid edge")
        if len(fam) != rec["f"] or sol["f"] != rec["f"]:
            errs.append(f"size mismatch: |family|={len(fam)} recorded f={rec['f']}")
        # down-closure
        down_ok = True
        for e in fam:
            se = set(e)
            for i, a in enumerate(e):
                if a - 1 >= 1 and (a - 1) not in se:
                    e2 = tuple(sorted(e[:i] + (a - 1,) + e[i + 1:]))
                    if e2 not in fs:
                        down_ok = False
        if not down_ok:
            errs.append("not down-closed")
        # direct matching check — no shifting assumption. Prefer an O(|F|)
        # certificate (union<rk / explicit transversal, both re-verified
        # edge-by-edge above); fall back to exhaustive search.
        cert = no_k_disjoint_certificate(fam, k, r)
        if cert is None:
            cert = "exhaustive-search"
            if has_k_disjoint(fam, k):
                errs.append(f"family CONTAINS {k} pairwise disjoint edges")
        # formula re-derivation
        cc = C(r * k - 1, r)
        cv = C(n, r) - C(n - k + 1, r)
        conj = max(cc, cv)
        if (cc, cv, conj) != (rec["cand_clique"], rec["cand_cover"], rec["conjectured"]):
            errs.append("conjectured-value mismatch vs formula")
        if rec["matches_conjecture"] != (rec["f"] == conj):
            errs.append("matches_conjecture flag inconsistent")
        status = "OK " if not errs else "FAIL"
        print(f"{status} r={r} k={k} n={n} f={rec['f']} conj={conj} "
              f"match={rec['f'] == conj} no-matching-proof: {cert}"
              f"{'  ' + '; '.join(errs) if errs else ''}")
        ok &= not errs
        nchecked += 1

    print(f"{nchecked} certified cells verified; overall: {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
