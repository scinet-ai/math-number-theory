"""Shared exact-arithmetic primitives for the Erdős #993 forest computation.

Everything here is exact Python big-integer arithmetic; no floating point.
Independence sequences are lists of nonnegative ints, index = independent-set
size, trimmed so the last entry is nonzero.
"""


def conv(a, b):
    """Exact convolution (polynomial product) of two coefficient lists."""
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def is_unimodal(s):
    """True iff s never strictly dips and then strictly rises."""
    i = 0
    n = len(s)
    while i + 1 < n and s[i + 1] >= s[i]:
        i += 1
    while i + 1 < n and s[i + 1] <= s[i]:
        i += 1
    return i == n - 1


def first_valley(s):
    """Return (a, b, c) with s[a] > s[b] < s[c], a < b < c, or None if unimodal."""
    n = len(s)
    i = 0
    while i + 1 < n and s[i + 1] >= s[i]:
        i += 1
    # i is the first peak; find a strict dip then strict rise
    j = i
    while j + 1 < n and s[j + 1] <= s[j]:
        j += 1
    if j == n - 1:
        return None
    # s[j] < s[j+1]: strict rise after a dip. Find a < j with s[a] > s[j].
    a = max(k for k in range(j) if s[k] > s[j])
    return (a, j, j + 1)


def is_log_concave(s):
    """True iff s has no internal zeros and s[i]^2 >= s[i-1]*s[i+1] everywhere.

    For all-positive sequences (independence sequences and their products)
    the internal-zero condition is automatic; we still check it.
    """
    n = len(s)
    if any(x < 0 for x in s):
        raise ValueError("negative coefficient")
    # support must be an interval for strong unimodality
    nz = [i for i, x in enumerate(s) if x > 0]
    if nz and nz[-1] - nz[0] + 1 != len(nz):
        return False
    for i in range(1, n - 1):
        if s[i] * s[i] < s[i - 1] * s[i + 1]:
            return False
    return True


def independence_sequence(parents):
    """Exact independence sequence of the tree given by round-1 parent arrays.

    parents: list of length n, parents[j-1] = parent of vertex j (1-indexed),
    parents[0] = 0 marks the root (vertex 1). Guaranteed parents[j-1] < j.
    Iterative two-state DP (exclude/include), processing vertices in reverse
    index order, which is a valid topological order since parent < child.
    """
    n = len(parents)
    assert parents[0] == 0
    for j in range(2, n + 1):
        p = parents[j - 1]
        assert 1 <= p < j, f"parent array not topologically ordered at {j}"
    exc = {v: [1] for v in range(1, n + 1)}      # v excluded
    inc = {v: [0, 1] for v in range(1, n + 1)}   # v included
    for v in range(n, 1, -1):
        p = parents[v - 1]
        both = [x + y for x, y in zip_pad(exc[v], inc[v])]
        exc[p] = conv(exc[p], both)
        inc[p] = conv(inc[p], exc[v])
        del exc[v], inc[v]
    seq = [x + y for x, y in zip_pad(exc[1], inc[1])]
    while seq and seq[-1] == 0:
        seq.pop()
    return seq


def zip_pad(a, b):
    m = max(len(a), len(b))
    for i in range(m):
        yield (a[i] if i < len(a) else 0), (b[i] if i < len(b) else 0)


def brute_force_sequence(n, edges):
    """Independence sequence by enumerating all 2^n subsets. n <= ~22."""
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    seq = [0] * (n + 1)
    for mask in range(1 << n):
        ok = True
        m = mask
        while m:
            v = (m & -m).bit_length() - 1
            if adj[v] & mask:
                ok = False
                break
            m &= m - 1
        if ok:
            seq[bin(mask).count("1")] += 1
    while seq and seq[-1] == 0:
        seq.pop()
    return seq


def parents_to_edges(parents):
    """0-indexed edge list from a round-1 parent array."""
    return [(j - 1, parents[j - 1] - 1) for j in range(2, len(parents) + 1)]


def load_round1_nonlogconcave(round1_results_dir):
    """Load the 149 non-log-concave trees banked by round 1.

    Returns list of dicts {n, par, seq} in file order
    (order26_exceptions, order28, order29, order30).
    """
    files = [
        "order26_exceptions.txt",
        "order28_nonlogconcave_trees.txt",
        "order29_nonlogconcave_trees.txt",
        "order30_nonlogconcave_trees.txt",
    ]
    out = []
    for f in files:
        with open(f"{round1_results_dir}/{f}") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                assert line.startswith("NONLOGCONCAVE ")
                fields = dict(tok.split("=", 1) for tok in line.split()[1:])
                n = int(fields["n"])
                par = [int(x) for x in fields["par"].split(",")]
                seq = [int(x) for x in fields["seq"].split(",")]
                assert len(par) == n
                out.append({"n": n, "par": par, "seq": seq})
    return out
