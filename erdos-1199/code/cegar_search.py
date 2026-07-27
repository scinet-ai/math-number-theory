#!/usr/bin/env python3
"""Counterexample-guided (lazy-clause) threshold search for larger k.

For k >= 4 the full CNF has C(n/2, k) sumset constraints and becomes huge,
but only a small fraction are ever active.  This driver keeps a growing pool
of k-subsets A (the "discovered constraints") per k:

  repeat:
    build a CNF from the pooled constraints applicable at this n
    kissat  -> UNSAT: done. The pooled clauses are a SUBSET of the true
               constraint set, and each clause is a genuine constraint, so
               unsatisfiability already proves every 2-colouring of [1..n]
               contains a monochromatic A+A: n(k) <= n.  (A DRAT proof for
               this reduced CNF is a complete certificate.)
            -> SAT: the model is checked against ALL constraints by the
               independent clique-based checker.  If no violation, it is a
               genuine avoiding colouring: n(k) > n.  Otherwise add up to
               `batch` violated subsets to the pool and iterate.

The pool is shared across n (a constraint valid at n is valid at n' >= n),
stored in results/pool_k{k}.json, so the binary search reuses everything.
All decisions are appended to results/search_log.jsonl.

Usage: cegar_search.py k [n_cap] [batch]
"""
import json
import os
import subprocess
import sys
import time
from itertools import combinations_with_replacement

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "results")
LOG = os.path.join(RESULTS, "search_log.jsonl")

sys.path.insert(0, HERE)
from check_coloring import iter_mono_sets  # noqa: E402


def log_entry(entry):
    entry["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def sumset(A):
    return sorted({a + b for a, b in combinations_with_replacement(A, 2)})


class Pool:
    def __init__(self, k):
        self.k = k
        self.path = os.path.join(RESULTS, f"pool_k{k}.json")
        self.subsets = []
        self.seen = set()
        if os.path.exists(self.path):
            for A in json.load(open(self.path)):
                self.add(tuple(A))

    def add(self, A):
        A = tuple(sorted(A))
        if A not in self.seen:
            self.seen.add(A)
            self.subsets.append(A)
            return True
        return False

    def save(self):
        with open(self.path, "w") as f:
            json.dump(sorted(self.subsets), f)


def write_pool_cnf(pool, n, path):
    lines = []
    for A in pool.subsets:
        if 2 * A[-1] <= n:
            S = sumset(A)
            lines.append(" ".join(map(str, S)) + " 0\n")
            lines.append(" ".join(str(-s) for s in S) + " 0\n")
    with open(path, "w") as f:
        f.write(f"c lazy Owings instance n={n} k={pool.k} "
                f"(subset of the full constraint set)\n")
        f.write(f"p cnf {n} {len(lines)}\n")
        f.writelines(lines)
    return len(lines)


def solve_lazy(pool, n, batch, quiet=False):
    """Decide instance (n, k) lazily; returns ('SAT', bits) or ('UNSAT', None)."""
    k = pool.k
    cnf = os.path.join(RESULTS, f"lazy_k{k}_n{n}.cnf")
    rounds = 0
    t_start = time.time()
    while True:
        rounds += 1
        nclauses = write_pool_cnf(pool, n, cnf)
        proc = subprocess.run(["kissat", "-q", cnf],
                              capture_output=True, text=True)
        if proc.returncode == 20:
            log_entry({"k": k, "n": n, "status": "UNSAT", "method": "lazy",
                       "pool_clauses": nclauses, "rounds": rounds,
                       "seconds": round(time.time() - t_start, 2)})
            return "UNSAT", None
        if proc.returncode != 10:
            raise RuntimeError(f"kissat exit {proc.returncode}")
        model = {}
        for line in proc.stdout.splitlines():
            if line.startswith("v "):
                for tok in line[2:].split():
                    lit = int(tok)
                    if lit:
                        model[abs(lit)] = 1 if lit > 0 else 0
        colours = [model.get(i, 0) for i in range(1, n + 1)]
        added = 0
        for A, _c in iter_mono_sets(colours, k, limit=batch):
            if pool.add(tuple(A)):
                added += 1
        if added == 0:
            bits = "".join(map(str, colours))
            wit = os.path.join(RESULTS, f"witness_k{k}_n{n}.txt")
            with open(wit, "w") as f:
                f.write(bits + "\n")
            log_entry({"k": k, "n": n, "status": "SAT", "method": "lazy",
                       "pool_clauses": nclauses, "rounds": rounds,
                       "witness": os.path.basename(wit),
                       "independent_recheck": "AVOIDING",
                       "seconds": round(time.time() - t_start, 2)})
            return "SAT", bits
        if not quiet and rounds % 25 == 0:
            print(f"    ... n={n} round {rounds}, pool={len(pool.subsets)}",
                  flush=True)


def find_threshold(k, n_cap, batch):
    pool = Pool(k)
    known = {}
    if os.path.exists(LOG):
        for line in open(LOG):
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("k") == k and e.get("status") in ("SAT", "UNSAT"):
                known[e["n"]] = e["status"]

    def decide(n):
        if n in known:
            return known[n]
        t0 = time.time()
        st, _ = solve_lazy(pool, n, batch)
        pool.save()
        print(f"  k={k} n={n}: {st} (pool={len(pool.subsets)}, "
              f"{time.time()-t0:.1f}s)", flush=True)
        known[n] = st
        return st

    lo, hi = 2 * k, None
    if decide(lo) == "UNSAT":
        raise RuntimeError("unexpected UNSAT at minimal n")
    n = lo
    while hi is None:
        n = min(2 * n, n_cap) if n < n_cap else n_cap
        if decide(n) == "UNSAT":
            hi = n
        else:
            lo = n
            if n >= n_cap:
                print(f"k={k}: SAT at cap {n_cap}; n({k}) > {n_cap}")
                log_entry({"k": k, "event": "cap_reached", "cap": n_cap,
                           "conclusion": f"n({k}) > {n_cap}"})
                return None
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if decide(mid) == "UNSAT":
            hi = mid
        else:
            lo = mid
    print(f"n({k}) = {hi}  (SAT witness at {lo}, UNSAT at {hi})")
    log_entry({"k": k, "event": "threshold", "n_of_k": hi, "sat_below": lo,
               "method": "lazy"})
    return hi


if __name__ == "__main__":
    k = int(sys.argv[1])
    n_cap = int(sys.argv[2]) if len(sys.argv) > 2 else 4096
    batch = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    find_threshold(k, n_cap, batch)
