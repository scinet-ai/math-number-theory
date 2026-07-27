#!/usr/bin/env python3
"""Independent validator for packing witnesses produced by packer.c.

For every sampled witness line it re-checks, with networkx (a completely
separate code path from the C solver), that:
  * the label string assigns every edge of K_n to exactly one tree size
    2..n (so the packing is an exact edge-disjoint decomposition),
  * for each size k, the edges labeled k form a tree on k vertices that is
    ISOMORPHIC to the family's chosen unlabeled tree T_k (index from the
    witness line; the top tree's index is the chunk number).

Usage: check_witnesses.py n trees_dir results_dir [max_lines_per_file]
Exits nonzero on any failure.
"""

import sys
from pathlib import Path

import networkx as nx

n = int(sys.argv[1])
trees_dir = Path(sys.argv[2])
results_dir = Path(sys.argv[3])
max_lines = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9

DIGITS = "0123456789ab"
m = n * (n - 1) // 2

edge_of_index = []
for u in range(n):
    for v in range(u + 1, n):
        edge_of_index.append((u, v))
assert len(edge_of_index) == m

trees = {}
for k in range(2, n + 1):
    trees[k] = []
    for line in (trees_dir / f"trees_{k:02d}.txt").read_text().splitlines():
        parents = list(map(int, line.split()))
        g = nx.Graph((i + 1, p) for i, p in enumerate(parents))
        g.add_node(0)
        assert g.number_of_nodes() == k
        trees[k].append(g)

checked = 0
failures = 0
for sample_path in sorted(results_dir.glob("sample_*.txt")):
    top_index = int(sample_path.stem.split("_")[1])
    for lineno, line in enumerate(sample_path.read_text().splitlines()):
        if lineno >= max_lines:
            break
        parts = line.split()
        fam_idx, code = int(parts[0]), int(parts[1])
        if code >= 2:  # no packing claimed for unsat/undecided lines
            continue
        idxs = list(map(int, parts[2 : 2 + (n - 2)]))  # sizes n-1 .. 2
        labels = parts[-1]
        assert len(labels) == m, (sample_path, fam_idx, "bad label length")
        family = {n: top_index}
        for j, k in enumerate(range(n - 1, 1, -1)):
            family[k] = idxs[j]
        by_size = {k: [] for k in range(2, n + 1)}
        ok = True
        for e, ch in enumerate(labels):
            k = DIGITS.index(ch)
            if k < 2 or k > n:
                ok = False
                break
            by_size[k].append(edge_of_index[e])
        if ok:
            for k in range(2, n + 1):
                edges = by_size[k]
                if len(edges) != k - 1:
                    ok = False
                    break
                g = nx.Graph(edges)
                if (
                    g.number_of_nodes() != k
                    or not nx.is_connected(g)
                    or not nx.is_isomorphic(g, trees[k][family[k]])
                ):
                    ok = False
                    break
        if not ok:
            failures += 1
            print(f"FAIL {sample_path.name} family {fam_idx}")
        checked += 1

print(f"witness check: n={n} files={len(list(results_dir.glob('sample_*.txt')))} "
      f"witnesses_checked={checked} failures={failures}")
sys.exit(1 if failures or checked == 0 else 0)
