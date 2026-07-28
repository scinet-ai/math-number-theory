#!/usr/bin/env python3
"""merge218.py -- merge/verify CERT1 shard output from erdos218 (Erdős #218).

Reads CERT1 lines from the files given on argv (or stdin), sorts windows by
lo, then verifies:
  1. windows are disjoint and contiguous (hi_k == lo_{k+1});
  2. stitch check: next= of window k equals first= of window k+1 (both are
     independently computed actual primes, so shard boundaries cannot drop
     or double-count a triple silently);
  3. per-window invariant primes == gt + eq + lt.

If coverage starts at lo=2, prints the cumulative convergence table: at each
window boundary x,  N = pi(x)  (n <= N indexes gaps d_n vs d_{n+1} with
first prime p_n <= x),  rho_>(N), rho_=(N), rho_<(N), rho_>=(N), E(N).

Usage: merge218.py [--every K] [file ...]
"""
import re
import sys

PAT = re.compile(
    r"^CERT1 lo=(\d+) hi=(\d+) primes=(\d+) first=(\d+) last=(\d+) "
    r"next=(\d+) gt=(\d+) eq=(\d+) lt=(\d+)\s*$"
)


def main():
    args = sys.argv[1:]
    every = 1
    if args and args[0] == "--every":
        every = int(args[1])
        args = args[2:]
    lines = []
    if args:
        for f in args:
            lines += open(f).read().splitlines()
    else:
        lines = sys.stdin.read().splitlines()

    wins = []
    for ln in lines:
        if not ln.startswith("CERT1"):
            continue
        m = PAT.match(ln)
        if not m:
            sys.exit("malformed CERT1 line: %r" % ln)
        wins.append(tuple(int(x) for x in m.groups()))
    if not wins:
        sys.exit("no CERT1 lines found")
    wins.sort()

    errors = 0
    for k, w in enumerate(wins):
        lo, hi, primes, first, last, nxt, gt, eq, lt = w
        if primes != gt + eq + lt:
            print("ERROR window [%d,%d): primes != gt+eq+lt" % (lo, hi))
            errors += 1
        if k + 1 < len(wins):
            lo2 = wins[k + 1][0]
            first2 = wins[k + 1][3]
            if hi != lo2:
                print("ERROR coverage gap/overlap: [.,%d) then [%d,.)" % (hi, lo2))
                errors += 1
            elif first2 and nxt != first2:
                print(
                    "ERROR stitch: next=%d of [%d,%d) != first=%d of next window"
                    % (nxt, lo, hi, first2)
                )
                errors += 1
    if errors:
        sys.exit("%d verification error(s)" % errors)
    print(
        "# verified %d windows, coverage [%d,%d), no gaps, stitch OK"
        % (len(wins), wins[0][0], wins[-1][1])
    )

    cum_p = cum_gt = cum_eq = cum_lt = 0
    if wins[0][0] != 2:
        print("# coverage does not start at 2: printing merged totals only")
        for w in wins:
            cum_p += w[2]
            cum_gt += w[6]
            cum_eq += w[7]
            cum_lt += w[8]
        print(
            "MERGED lo=%d hi=%d primes=%d gt=%d eq=%d lt=%d"
            % (wins[0][0], wins[-1][1], cum_p, cum_gt, cum_eq, cum_lt)
        )
        return

    print(
        "%16s %16s %12s %12s %12s %12s %10s" % ("x", "N=pi(x)", "rho_>", "rho_=", "rho_<", "rho_>=", "E(N)")
    )
    for k, w in enumerate(wins):
        cum_p += w[2]
        cum_gt += w[6]
        cum_eq += w[7]
        cum_lt += w[8]
        if (k + 1) % every and k + 1 != len(wins):
            continue
        print(
            "%16d %16d %12.9f %12.9f %12.9f %12.9f %10d"
            % (
                w[1],
                cum_p,
                cum_gt / cum_p,
                cum_eq / cum_p,
                cum_lt / cum_p,
                (cum_gt + cum_eq) / cum_p,
                cum_eq,
            )
        )


if __name__ == "__main__":
    main()
