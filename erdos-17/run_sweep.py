#!/usr/bin/env python3
"""Driver for the cluster-prime sweep (Erdős #17).

Dispatches blocks to ./cluster (3 worker threads), appends CSV lines to
results.csv (checkpoint: completed blocks are skipped on restart), stops
dispatching at the wall-clock deadline. Blocks are dispatched in ascending
order so the certified region is a contiguous prefix (up to in-flight tail).

Usage: run_sweep.py <deadline_epoch_seconds>
"""
import subprocess, sys, threading, time, os

WD = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(WD, "results.csv")
LOG = os.path.join(WD, "sweep.log")
BIN = os.path.join(WD, "cluster")
DEADLINE = float(sys.argv[1])

def schedule():
    blocks = []
    blocks.append((0, 10**7))
    blocks.append((10**7, 10**8))
    blocks.append((10**8, 10**9))
    for lo in range(10**9, 10**11, 10**9):          # 99 x 1e9
        blocks.append((lo, lo + 10**9))
    for lo in range(10**11, 10**12, 2 * 10**10):    # 45 x 2e10
        blocks.append((lo, lo + 2 * 10**10))
    for lo in range(10**12, 2 * 10**13, 10**10):    # 1e10 blocks incl. extension
        blocks.append((lo, lo + 10**10))
    return blocks

done = set()
if os.path.exists(RESULTS):
    for line in open(RESULTS):
        f = line.strip().split(",")
        if len(f) > 3:
            done.add((int(f[0]), int(f[1])))

queue = [b for b in schedule() if b not in done]
qlock = threading.Lock()
wlock = threading.Lock()
t_start = time.time()

def log(msg):
    with wlock:
        with open(LOG, "a") as fh:
            fh.write("%.1f %s\n" % (time.time() - t_start, msg))

def worker(wid):
    while True:
        with qlock:
            if not queue or time.time() > DEADLINE:
                return
            blk = queue.pop(0)
        lo, hi = blk
        r = subprocess.run([BIN, str(lo), str(hi)], capture_output=True, text=True)
        if r.returncode != 0:
            log("FATAL block %d %d rc=%d err=%s" % (lo, hi, r.returncode, r.stderr[:200]))
            os._exit(3)
        with wlock:
            with open(RESULTS, "a") as fh:
                fh.write(r.stdout)
                fh.flush(); os.fsync(fh.fileno())
        log("done %d %d (w%d)" % (lo, hi, wid))

threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
for t in threads: t.start()
for t in threads: t.join()
log("ALL-STOP queue_remaining=%d" % len(queue))
print("sweep finished/stopped; remaining blocks:", len(queue))
