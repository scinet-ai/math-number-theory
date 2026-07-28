#!/bin/bash
# Checkpointed worker for the exhaustive <=30-vertex forest sweep (Lane B).
#
# Usage: ./run_forest_worker.sh WORKER_ID
#
# Tasks (one per line "k res mod") live in tasks.txt; a worker claims task
# t atomically via mkdir logs/lock_<k>_<res>_<mod>, runs gentreeg_forest on
# residue class res/mod of the order-k tree stream with the order-k q-set,
# and banks the FCHECK summary as logs/task_<k>_<res>_<mod>.done plus any
# exception lines as .out.  Finished tasks are skipped on re-run, so the
# sweep is resumable after a kill.
set -u
cd "$(dirname "$0")"
WORKER_ID=$1

while read -r k res mod; do
    tag="${k}_${res}_${mod}"
    [ -f "logs/task_${tag}.done" ] && continue
    mkdir "logs/lock_${tag}" 2>/dev/null || continue   # atomic claim
    if [ -f "logs/task_${tag}.done" ]; then rmdir "logs/lock_${tag}"; continue; fi
    out="logs/task_${tag}.out"; err="logs/task_${tag}.err"
    if [ "$mod" -eq 1 ]; then
        QSET_FILE="qsets/qset_k${k}.txt" ./gentreeg_forest -q "$k" > "$out" 2> "$err"
    else
        QSET_FILE="qsets/qset_k${k}.txt" ./gentreeg_forest -q "$k" "${res}/${mod}" > "$out" 2> "$err"
    fi
    status=$?
    if [ $status -eq 0 ] && grep -q "^FCHECK k=" "$err"; then
        mv "$err" "logs/task_${tag}.done"
        [ -s "$out" ] || rm -f "$out"
        echo "worker ${WORKER_ID}: task ${tag} done: $(grep '^FCHECK' "logs/task_${tag}.done")"
    else
        echo "worker ${WORKER_ID}: task ${tag} FAILED (exit ${status})"
        mv "$err" "logs/task_${tag}.failed" 2>/dev/null
    fi
    rmdir "logs/lock_${tag}"
done < tasks.txt
echo "worker ${WORKER_ID}: queue drained"
