#!/usr/bin/env python3
"""SAT-free confirmation of n(2) = 14 by direct enumeration.

Checks (a) every one of the 2^14 colourings of {1,...,14} contains a
2-element A with A+A monochromatic, and (b) at least one colouring of
{1,...,13} does not.  Uses only check_coloring.find_mono_set, which shares
no code with the CNF/SAT pipeline.
"""
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from check_coloring import find_mono_set  # noqa: E402


def all_colourings_hit(n, k):
    for mask in range(2 ** n):
        colours = [(mask >> i) & 1 for i in range(n)]
        if find_mono_set(colours, k) is None:
            return False, colours
    return True, None


ok14, _ = all_colourings_hit(14, 2)
ok13, avoiding = all_colourings_hit(13, 2)
assert ok14, "some colouring of [1..14] avoids monochromatic A+A: n(2) > 14?!"
assert not ok13, "no colouring of [1..13] avoids: n(2) < 14?!"
print("confirmed by exhaustive enumeration (no SAT): n(2) = 14")
print("example avoiding colouring of [1..13]:",
      "".join(map(str, avoiding)))
