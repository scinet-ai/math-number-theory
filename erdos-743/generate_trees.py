#!/usr/bin/env python3
"""Generate all unlabeled trees on 2..MAX_N vertices for the tree packing sweep.

Output format (trees/trees_NN.txt): one tree per line, as a parent array.
A tree on k vertices is written as k-1 integers p1 .. p(k-1) where pi < i is
the parent of vertex i (vertex 0 is the root). This "connected order" is what
the C packer needs: every vertex after the first attaches to an earlier one.

Certification of isomorph-completeness:
  1. Trees come from networkx.nonisomorphic_trees (WROM algorithm).
  2. We independently compute an AHU canonical string (our own code, rooted at
     the tree centroid set) for every tree and check all strings are distinct.
  3. Counts are checked against the known values of OEIS A000055
     (unlabeled trees on n nodes): 1, 1, 2, 3, 6, 11, 23, 47, 106, 235.
  Distinct canonical forms + count equal to the known total => the list is a
  complete set of pairwise non-isomorphic trees on k vertices.
"""

import sys
from pathlib import Path

import networkx as nx

# OEIS A000055: number of unlabeled trees on n nodes, n = 2..11
EXPECTED = {2: 1, 3: 1, 4: 2, 5: 3, 6: 6, 7: 11, 8: 23, 9: 47, 10: 106, 11: 235}

MAX_N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
OUT_DIR = Path(__file__).resolve().parent / "trees"
OUT_DIR.mkdir(exist_ok=True)


def ahu_canonical(tree: nx.Graph) -> str:
    """AHU canonical string of an unrooted tree, rooted at its center(s)."""

    def rooted(v, parent):
        children = sorted(
            rooted(w, v) for w in tree.neighbors(v) if w != parent
        )
        return "(" + "".join(children) + ")"

    centers = nx.center(tree)  # 1 or 2 vertices
    return min(rooted(c, None) for c in sorted(centers))


def parent_array(tree: nx.Graph) -> list[int]:
    """Relabel to connected (BFS) order; return parents of vertices 1..k-1.

    Deterministic: BFS from the smallest-labeled vertex of maximum degree,
    visiting neighbors in ascending label order.
    """
    root = min(tree.nodes, key=lambda v: (-tree.degree(v), v))
    order = [root]
    new_label = {root: 0}
    parents = []
    queue = [root]
    while queue:
        v = queue.pop(0)
        for w in sorted(tree.neighbors(v)):
            if w not in new_label:
                new_label[w] = len(order)
                order.append(w)
                parents.append(new_label[v])
                queue.append(w)
    assert len(order) == tree.number_of_nodes()
    return parents


def main() -> None:
    for k in range(2, MAX_N + 1):
        trees = list(nx.nonisomorphic_trees(k))
        # completeness check 1: expected count (OEIS A000055)
        assert len(trees) == EXPECTED[k], (k, len(trees), EXPECTED[k])
        # completeness check 2: pairwise non-isomorphic via independent AHU code
        canon = [ahu_canonical(t) for t in trees]
        assert len(set(canon)) == len(trees), f"duplicate tree at k={k}"
        # sanity: each really is a tree on k vertices
        for t in trees:
            assert t.number_of_nodes() == k and t.number_of_edges() == k - 1
            assert nx.is_connected(t)
        lines = []
        for t in trees:
            pa = parent_array(t)
            # re-check the parent array encodes an isomorphic tree
            g = nx.Graph([(i + 1, p) for i, p in enumerate(pa)])
            g.add_node(0)
            assert nx.is_isomorphic(g, t)
            lines.append(" ".join(map(str, pa)))
        out = OUT_DIR / f"trees_{k:02d}.txt"
        out.write_text("\n".join(lines) + "\n")
        print(f"k={k:2d}: {len(trees):4d} trees -> {out.name}  (matches A000055)")


if __name__ == "__main__":
    main()
