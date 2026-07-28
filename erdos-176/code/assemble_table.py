#!/usr/bin/env python3
"""Assemble the N(k,l) table from certified log events + derived rules.

Sources per cell are tracked:
  spencer    — Spencer 1973 formula for l=1: k=2^t m (m odd) => N(k,1)=2^t(k-1)+1
  parity     — Adenwalla (erdosproblems.com/176 comment, 2026-03-19):
               k-AP sums have parity of k, so N(k,l+1)=N(k,l) when k !≡ l (mod 2)
  vdW        — N(k,k)=W(k): W(3)=9, W(4)=35, W(5)=178, W(6)=1132
  goss       — Goss (quantiterate) Zenodo 10.5281/zenodo.20763838: odd-k l=2 row
  this-work  — our certified SAT computations (witness + DRAT, from log.jsonl)
Emits results/table.md and results/table.json.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "log.jsonl")

W = {1: 1, 2: 3, 3: 9, 4: 35, 5: 178, 6: 1132}
GOSS = {3: 9, 5: 22, 7: 49, 9: 65, 11: 112}
KMAX = 13


def spencer(k):
    t = 0
    m = k
    while m % 2 == 0:
        m //= 2
        t += 1
    return (2 ** t) * (k - 1) + 1


def main():
    val = {}   # (k,l) -> value
    src = {}   # (k,l) -> source

    def put(k, l, v, s):
        if not (1 <= l <= k):
            return
        if (k, l) in val:
            if val[(k, l)] != v:
                print(f"CONFLICT at N({k},{l}): {val[(k,l)]} ({src[(k,l)]}) "
                      f"vs {v} ({s})", file=sys.stderr)
                sys.exit(1)
            return
        val[(k, l)] = v
        src[(k, l)] = s

    # this-work certified cells first (they take precedence for provenance,
    # but conflicts with any derived rule are fatal)
    ours = {}
    if os.path.exists(LOG):
        for line in open(LOG):
            r = json.loads(line)
            if r.get("event") == "certified" and r.get("drat_verified"):
                cell = r["cell"]  # "N(k,l)"
                k, l = map(int, cell[2:-1].split(","))
                ours[(k, l)] = r["value"]
    for (k, l), v in ours.items():
        put(k, l, v, "this-work")

    for k in range(2, KMAX + 1):
        put(k, 1, spencer(k), "spencer")
        if k in W:
            put(k, k, W[k], "vdW")
        if k in GOSS and (k, 2) not in val:
            put(k, 2, GOSS[k], "goss")

    # parity closure: N(k,l+1)=N(k,l) when k !≡ l (mod 2); iterate to fixpoint
    changed = True
    while changed:
        changed = False
        for k in range(2, KMAX + 1):
            for l in range(1, k):
                if (k - l) % 2 == 0:
                    continue  # k ≡ l: no collapse
                a, b = (k, l), (k, l + 1)
                if a in val and b not in val:
                    put(k, l + 1, val[a], f"parity<-{src[a]}")
                    changed = True
                elif b in val and a not in val:
                    put(k, l, val[b], f"parity<-{src[b]}")
                    changed = True
                elif a in val and b in val and val[a] != val[b]:
                    print(f"PARITY CONFLICT {a}={val[a]} {b}={val[b]}",
                          file=sys.stderr)
                    sys.exit(1)

    # monotonicity sanity: N(k,l) nondecreasing in l
    for k in range(2, KMAX + 1):
        prev = None
        for l in range(1, k + 1):
            if (k, l) in val:
                if prev is not None and val[(k, l)] < prev:
                    print(f"MONOTONICITY VIOLATION row k={k}", file=sys.stderr)
                    sys.exit(1)
                prev = val[(k, l)]

    out = {f"N({k},{l})": {"value": val[(k, l)], "source": src[(k, l)]}
           for (k, l) in sorted(val)}
    with open(os.path.join(ROOT, "results", "table.json"), "w") as f:
        json.dump(out, f, indent=1)

    lines = ["| k \\ l | " + " | ".join(str(l) for l in range(1, KMAX + 1)) + " |",
             "|---" * (KMAX + 1) + "|"]
    for k in range(2, KMAX + 1):
        row = [f"| **{k}** "]
        for l in range(1, KMAX + 1):
            if l > k:
                row.append("| ")
            elif (k, l) in val:
                mark = {"this-work": "**", }.get(src[(k, l)], "")
                base = src[(k, l)].split("<-")[-1]
                mark = "**" if base == "this-work" else ""
                row.append(f"| {mark}{val[(k,l)]}{mark} ")
            else:
                row.append("| ? ")
        lines.append("".join(row) + "|")
    with open(os.path.join(ROOT, "results", "table.md"), "w") as f:
        f.write("\n".join(lines) + "\n\nBold = new values certified in this "
                "work (witness + DRAT). '?' = unknown.\n")
    print("\n".join(lines))
    print("\nsources:")
    for (k, l) in sorted(val):
        print(f"  N({k},{l}) = {val[(k,l)]:>5}  [{src[(k,l)]}]")


if __name__ == "__main__":
    main()
