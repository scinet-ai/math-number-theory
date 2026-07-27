#!/bin/bash
# Checkpointed sweep worker for an arbitrary order.
#
# Usage: ./run_sweep_worker.sh ORDER CHUNK_COUNT WORKER_ID NUM_WORKERS
#
# Same contract as run_order30_worker.sh: gentreeg res/mod partitions the
# trees on ORDER vertices into CHUNK_COUNT disjoint classes; worker w handles
# chunks c with c mod NUM_WORKERS == w; a finished chunk is banked as
# logs/chunk<ORDER>_<c>.done and skipped on re-run.
set -u
cd "$(dirname "$0")"

ORDER=$1
CHUNK_COUNT=$2
WORKER_ID=$3
NUM_WORKERS=$4

for (( c=WORKER_ID; c<CHUNK_COUNT; c+=NUM_WORKERS )); do
    done_file="logs/chunk${ORDER}_${c}.done"
    [ -f "$done_file" ] && continue
    out_file="logs/chunk${ORDER}_${c}.out"
    err_file="logs/chunk${ORDER}_${c}.err"
    ./gentreeg_independence -q ${ORDER} ${c}/${CHUNK_COUNT} > "$out_file" 2> "$err_file"
    status=$?
    if [ $status -eq 0 ] && grep -q "^CHECK trees=" "$err_file"; then
        mv "$err_file" "$done_file"
        echo "worker ${WORKER_ID}: order ${ORDER} chunk ${c} done: $(grep '^CHECK' "$done_file")"
    else
        echo "worker ${WORKER_ID}: order ${ORDER} chunk ${c} FAILED (exit ${status})"
        mv "$err_file" "logs/chunk${ORDER}_${c}.failed" 2>/dev/null
    fi
done
echo "worker ${WORKER_ID}: order ${ORDER}: all assigned chunks processed"
