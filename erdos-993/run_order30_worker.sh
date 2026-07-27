#!/bin/bash
# Checkpointed worker for the exhaustive order-30 sweep.
#
# Usage: ./run_order30_worker.sh WORKER_ID NUM_WORKERS
#
# The 14,830,871,802 trees on 30 vertices are partitioned by gentreeg's
# res/mod mechanism into CHUNK_COUNT disjoint residue classes.  Worker w
# processes chunks c with c mod NUM_WORKERS == w, sequentially.  A finished
# chunk is banked as logs/chunk30_<c>.done (its CHECK summary line);
# re-running the script skips banked chunks, so the sweep is resumable.
set -u
cd "$(dirname "$0")"

WORKER_ID=$1
NUM_WORKERS=$2
ORDER=30
CHUNK_COUNT=240

for (( c=WORKER_ID; c<CHUNK_COUNT; c+=NUM_WORKERS )); do
    done_file="logs/chunk30_${c}.done"
    [ -f "$done_file" ] && continue
    out_file="logs/chunk30_${c}.out"
    err_file="logs/chunk30_${c}.err"
    ./gentreeg_independence -q ${ORDER} ${c}/${CHUNK_COUNT} > "$out_file" 2> "$err_file"
    status=$?
    if [ $status -eq 0 ] && grep -q "^CHECK trees=" "$err_file"; then
        mv "$err_file" "$done_file"
        echo "worker ${WORKER_ID}: chunk ${c} done: $(grep '^CHECK' "$done_file")"
    else
        echo "worker ${WORKER_ID}: chunk ${c} FAILED (exit ${status})"
        mv "$err_file" "logs/chunk30_${c}.failed" 2>/dev/null
    fi
done
echo "worker ${WORKER_ID}: all assigned chunks processed"
