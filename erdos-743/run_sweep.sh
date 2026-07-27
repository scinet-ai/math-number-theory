#!/bin/bash
# Full exhaustive sweep for board size n, split across WORKERS processes.
# Chunk = one choice of the top tree T_n. Resumable: chunks whose result file
# already exists are skipped, so a killed run restarts where it left off.
# Usage: ./run_sweep.sh <n> [workers] [sample_stride] [node_cap]
set -u
cd "$(dirname "$0")"
N="${1:?usage: run_sweep.sh n [workers] [sample_stride] [node_cap]}"
WORKERS="${2:-4}"
STRIDE="${3:-50000}"
CAP="${4:-1000000000}"
OUT="results/n${N}"
mkdir -p "$OUT"
NCHUNKS=$(wc -l < "trees/trees_$(printf '%02d' "$N").txt" | tr -d ' ')

worker() {
  local w="$1"
  for ((i = w; i < NCHUNKS; i += WORKERS)); do
    chunk_file=$(printf '%s/chunk_%03d.txt' "$OUT" "$i")
    [ -f "$chunk_file" ] && continue
    ./packer "$N" "$i" trees "$OUT" "$STRIDE" "$CAP" \
      >> "$OUT/worker_${w}.log" 2>&1
    rc=$?
    if [ "$rc" -ne 0 ]; then
      echo "chunk $i exited $rc" >> "$OUT/worker_${w}.log"
    fi
  done
}

for ((w = 0; w < WORKERS; w++)); do worker "$w" & done
wait
echo "sweep n=$N done: $(ls "$OUT"/chunk_*.txt 2>/dev/null | wc -l | tr -d ' ')/$NCHUNKS chunks"
