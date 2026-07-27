#!/usr/bin/env python3
"""Render results/table.md from results/results.jsonl."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")

recs = {}
for line in open(os.path.join(RES, "results.jsonl")):
    r = json.loads(line)
    recs[(r["r"], r["k"], r["n"])] = r

STATUS = {
    "kleitman": "validation (Kleitman 1968)",
    "frankl13": "validation (Frankl 2013)",
    "open": "OPEN — new",
}


def regime(r, k, n):
    s = k - 1
    if n == r * k:
        return STATUS["kleitman"]
    if n >= (2 * s + 1) * r - s:
        return STATUS["frankl13"]
    return STATUS["open"]


lines = [
    "# Certified values of f(n;r,k)\n",
    "| r | k | n | f(n;r,k) | conjecture | clique C(rk-1,r) | cover C(n,r)-C(n-k+1,r) | matches | cell status |",
    "|---|---|---|----------|------------|------------------|-------------------------|---------|-------------|",
]
new_cells = 0
for key in sorted(recs, key=lambda t: (t[0], t[1], t[2])):
    r = recs[key]
    if not r.get("certified_optimal"):
        continue
    st = regime(r["r"], r["k"], r["n"])
    if st == STATUS["open"]:
        new_cells += 1
    lines.append(
        f"| {r['r']} | {r['k']} | {r['n']} | **{r['f']}** | {r['conjectured']} "
        f"| {r['cand_clique']} | {r['cand_cover']} "
        f"| {'yes' if r['matches_conjecture'] else 'NO'} | {st} |")
lines.append(f"\nNewly determined open cells: **{new_cells}**.\n")
out = os.path.join(RES, "table.md")
open(out, "w").write("\n".join(lines))
print("\n".join(lines))
