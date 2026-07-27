#!/usr/bin/env python3
"""driver.py — orchestrate the Erdős #693 sweep with 3 worker processes.

Job plan (deterministic):
  k=2: dense n=3..2000; log grid (20/decade) 2240..100000; landmarks
       (10/decade) 125900..1000000.
  k=3: dense n=3..500; log grid 562..5012; landmarks 6310, 7943, 10000.

Results append to data/results.csv (atomic O_APPEND line writes from sieve.c):
  n,k,G,gap_start,gap_end,count,seconds
Restart-safe: completed (n,k) pairs are skipped; big single-n jobs also
checkpoint inside sieve.c every 30 s (checkpoints/ck_{k}_{n}.txt).
"""
import csv, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
SIEVE = os.path.join(HERE, "sieve")
RESULTS = os.path.join(HERE, "data", "results.csv")
CKDIR = os.path.join(HERE, "checkpoints")
LOGDIR = os.path.join(HERE, "logs")
MAX_WORKERS = 3

K2_GRID = [2240, 2510, 2820, 3160, 3550, 3980, 4470, 5010, 5620, 6310,
           7080, 7940, 8910, 10000, 11220, 12590, 14130, 15850, 17780,
           19950, 22390, 25120, 28180, 31620, 35480, 39810, 44670, 50120,
           56230, 63100, 70790, 79430, 89130, 100000]
K2_LAND = [125900, 158500, 199500, 251200, 316200, 398100, 501200,
           631000, 794300, 1000000]
K3_GRID = [562, 631, 708, 794, 891, 1000, 1122, 1259, 1413, 1585, 1778,
           1995, 2239, 2512, 2818, 3162, 3548, 3981, 4467, 5012]
K3_LAND = [6310, 7943, 10000]


def done_set():
    done = set()
    if os.path.exists(RESULTS):
        with open(RESULTS) as f:
            for row in csv.reader(f):
                if len(row) >= 7:
                    done.add((int(row[0]), int(row[1])))
    return done


def build_jobs(done):
    jobs = []  # (cost, argv)

    def single(n, k):
        if (n, k) in done:
            return
        ck = os.path.join(CKDIR, f"ck_{k}_{n}.txt")
        jobs.append((float(n) ** k,
                     [SIEVE, "single", str(n), str(k),
                      "--append", RESULTS, "--ckpt", ck]))

    def rng(lo, hi, k):
        # restart from first missing n (results within a range appear in order)
        start = lo
        while start <= hi and (start, k) in done:
            start += 1
        if start > hi:
            return
        cost = sum(float(n) ** k for n in range(start, hi + 1))
        jobs.append((cost, [SIEVE, "range", str(start), str(hi), str(k),
                            "--append", RESULTS]))

    rng(3, 2000, 2)
    rng(3, 500, 3)
    for n in K2_GRID + K2_LAND:
        single(n, 2)
    for n in K3_GRID + K3_LAND:
        single(n, 3)
    jobs.sort(key=lambda j: -j[0])  # longest first
    return [argv for _, argv in jobs]


def main():
    os.makedirs(os.path.dirname(RESULTS), exist_ok=True)
    os.makedirs(CKDIR, exist_ok=True)
    os.makedirs(LOGDIR, exist_ok=True)
    jobs = build_jobs(done_set())
    print(f"[driver] {len(jobs)} jobs queued", flush=True)
    running = []  # (proc, argv, logfh)
    t0 = time.time()
    ji = 0
    while ji < len(jobs) or running:
        while ji < len(jobs) and len(running) < MAX_WORKERS:
            argv = jobs[ji]
            tag = "_".join(argv[1:5]).replace("/", "-")
            logf = open(os.path.join(LOGDIR, f"job_{tag}.log"), "a")
            p = subprocess.Popen(argv, stdout=logf, stderr=logf)
            running.append((p, argv, logf))
            print(f"[driver] +{time.time()-t0:7.1f}s start: {' '.join(argv[1:5])}",
                  flush=True)
            ji += 1
        time.sleep(2)
        still = []
        for p, argv, logf in running:
            rc = p.poll()
            if rc is None:
                still.append((p, argv, logf))
            else:
                logf.close()
                stat = "done" if rc == 0 else f"FAILED rc={rc}"
                print(f"[driver] +{time.time()-t0:7.1f}s {stat}: "
                      f"{' '.join(argv[1:5])}", flush=True)
                if rc != 0:
                    print(f"[driver] see {logf.name}", flush=True)
        running = still
    print(f"[driver] all jobs finished in {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
