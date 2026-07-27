"""Exponent trend for S(N): log S(N)/log N over the certified exact table
plus certified lower bounds at larger N. Writes results/fit.json.

Honest framing: at these N the data cannot distinguish N^{1-o(1)} from
N^c with c<1; we report point exponents and a least-squares slope of
log S vs log N over the exact tail, plus the same for lower bounds
(which only bound the true exponent from below).
"""

import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))


def lsq_slope(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den, my - (num / den) * mx


def main():
    recs = [json.loads(l) for l in open(os.path.join(ROOT, "results",
            "chain.jsonl")) if l.strip()]
    S = {r["n"]: r["S"] for r in recs}
    Nstar = recs[-1]["n"]

    lbs = {}
    lbp = os.path.join(ROOT, "results", "lb.jsonl")
    if os.path.exists(lbp):
        for l in open(lbp):
            if l.strip():
                r = json.loads(l)
                lbs[r["n"]] = max(lbs.get(r["n"], 0), r["lower_bound"])
    for r in json.load(open(os.path.join(
            ROOT, "results", "lb_prior_verified.json"))).values():
        if r["n"] > Nstar:
            lbs[r["n"]] = max(lbs.get(r["n"], 0), r["lower_bound"])

    exact_pts = [{"n": n, "S": S[n],
                  "exponent": round(math.log(S[n]) / math.log(n), 4)}
                 for n in sorted(S) if n >= 10]
    lb_pts = [{"n": n, "S_lower_bound": v,
               "exponent_lb": round(math.log(v) / math.log(n), 4)}
              for n, v in sorted(lbs.items())]

    tail = [p for p in exact_pts if p["n"] >= Nstar // 2]
    slope_exact, _ = lsq_slope([math.log(p["n"]) for p in tail],
                               [math.log(p["S"]) for p in tail])
    out = {"exact_range": [1, Nstar],
           "S_at_frontier": S[Nstar],
           "point_exponents_exact_tail": exact_pts[-15:],
           "lsq_slope_logS_logN_exact_tail_from": Nstar // 2,
           "lsq_slope_logS_logN_exact_tail": round(slope_exact, 4),
           "lower_bound_points": lb_pts,
           "reference_exponents": {
               "alon_erdos_lower": 2 / 3,
               "conjectured": "1 (as N^{1-o(1)})"},
           "caveat": ("Point exponents log S/log N drift down over the "
                      "certified range; lower-bound exponents at larger N "
                      "only bound the truth from below. Data at this scale "
                      "cannot distinguish N^{1-o(1)} from a power N^c, "
                      "c<1; the Croot-Mao-Yip bound N^{1-c/loglog N} is "
                      "consistent with the observed slow drift.")}
    with open(os.path.join(ROOT, "results", "fit.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items()
                      if k != "point_exponents_exact_tail"}, indent=1))


if __name__ == "__main__":
    main()
