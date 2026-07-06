"""
Produce the master results table for Erdos #273 bounded non-existence.

For each admissible bound M (at each new admissible modulus up to --max), reduce
the admissible set <= M to its local-density CORE and record the verdict:

  * core empty                      -> NO covering (search-free)
  * core reciprocal sum < 1         -> NO covering (root-prune / reciprocal-sum
                                       certificate on the reduced core)
  * core reciprocal sum >= 1        -> reduction inconclusive; exact search over
                                       Z/lcm(core) required (frontier)

Writes results_table.md and prints a summary. Deterministic; rerunnable.
"""
import sys
from admissible import admissible_moduli, reduce_local_density, lcm


def main():
    MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    Sfull = admissible_moduli(MAX)
    rows = []
    last_nocover_M = None
    first_search_M = None
    # step through each admissible modulus as the running bound M
    for idx, M in enumerate(Sfull):
        S = Sfull[:idx + 1]
        sfull = sum(1.0 / m for m in S)
        core, log = reduce_local_density(S)
        csum = sum(1.0 / m for m in core)
        L = lcm(core) if core else 1
        if not core or csum < 1.0:
            verdict = "NO covering (search-free)"
            last_nocover_M = M
        else:
            verdict = "needs exact search"
            if first_search_M is None:
                first_search_M = M
        rows.append((M, len(S), sfull, len(core), csum, L, verdict))

    # write markdown table (sample rows to keep it readable)
    lines = ["| M (max modulus) | #admissible | sum 1/m (full) | #core | "
             "sum 1/m (core) | lcm(core) | verdict |",
             "|---:|---:|---:|---:|---:|---:|:---|"]
    for i, (M, ns, sf, nc, sc, L, v) in enumerate(rows):
        prev_v = rows[i - 1][6] if i > 0 else None
        transition = (v != prev_v)
        keep = (M <= 100 or M % 100 == 0 or transition
                or M == last_nocover_M or M == first_search_M)
        if keep:
            lines.append(f"| {M} | {ns} | {sf:.4f} | {nc} | {sc:.4f} | "
                         f"{L:,} | {v} |")
    with open("results_table.md", "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Swept admissible bounds up to M={MAX} ({len(Sfull)} admissible moduli).")
    print(f"Naive full-set reciprocal sum first reaches 1 at M="
          f"{next(M for (M, _, sf, *_ ) in rows if sf >= 1)}.")
    print(f"Largest M with search-free NON-EXISTENCE (core empty or core sum<1): "
          f"M = {last_nocover_M}.")
    print(f"First M needing exact search (core sum>=1): M = {first_search_M} "
          f"(lcm(core) = {next(L for (M,_,_,_,_,L,v) in rows if v=='needs exact search'):,}).")
    print("Wrote results_table.md")


if __name__ == "__main__":
    main()
