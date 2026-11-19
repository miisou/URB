#!/bin/bash
#SBATCH --job-name=urb-lab
#SBATCH --gres=gpu:0
# One lab run. Submitted by lab/labctl.py from the repository root on the cluster:
#   sbatch [options] lab/cluster/run_one.sh <run-id>
# The command to run is read from lab/cluster/cmds/<run-id>.sh.
# The venv and the raw results live on the node-local disk; only the settings, the metrics table,
# and the end of the log are copied back to lab/runs/<run-id>/.
set -euo pipefail
RUN_ID=$1
PATH_PROGRAM="${PATH_PROGRAM:-$PWD}"
CONTAINER="${PATH_SUMO_CONTAINER:-/shared/sets/singularity/sumo1_26_0patched.sif}"
LOCAL="${LOCAL_BASE:-/scratch/tmp/$USER/urb_lab}"
OUT="$PATH_PROGRAM/lab/runs/$RUN_ID"
mkdir -p "$LOCAL/venv" "$LOCAL/results" "$LOCAL/logs" "$OUT"
LOG="$LOCAL/logs/${RUN_ID}_${SLURM_JOB_ID}.txt"
echo "job $SLURM_JOB_ID on $(hostname): $RUN_ID, start $(date -Is)" > "$OUT/job.txt"
# Run from a private copy of the code on the local disk: later submissions rewrite the shared copy,
# and a script that is replaced while bash is still reading it fails with "Stale file handle".
SNAP="$LOCAL/code/${RUN_ID}_${SLURM_JOB_ID}"
mkdir -p "$SNAP/lab" "$SNAP/results"
# A submission that syncs while this copy runs replaces files under it ("replaced while being copied");
# retry until one copy goes through cleanly.
for attempt in 1 2 3 4 5 6; do
    if cp -r "$PATH_PROGRAM"/{scripts,config,analysis,baseline_models,networks,requirements.txt} "$SNAP/" &&
       cp -r "$PATH_PROGRAM"/lab/{fleet.py,arena.json,arenas,candidates,cluster} "$SNAP/lab/"; then
        break
    fi
    [ "$attempt" = 6 ] && { echo "code copy failed 6 times" >> "$OUT/job.txt"; exit 1; }
    sleep 20
done
set +e
singularity exec --cleanenv --env RUN_ID="$RUN_ID" \
    --bind "$SNAP":/app --bind "$LOCAL/results":/app/results --bind "$LOCAL/venv":/venv \
    "$CONTAINER" /bin/bash /app/lab/cluster/run_one_internal.sh > "$LOG" 2>&1
RC=$?
set -e
R="$LOCAL/results/$RUN_ID"
[ -f "$R/exp_config.json" ] && cp "$R/exp_config.json" "$OUT/" || true
[ -f "$R/metrics/BenchmarkMetrics.csv" ] && cp "$R/metrics/BenchmarkMetrics.csv" "$OUT/" || true
grep -vE "Downloading|Collecting|Using cached|Requirement already" "$LOG" | tr '\r' '\n' | tail -60 > "$OUT/log_tail.txt" || true
rm -rf "$SNAP"
echo "exit code $RC, end $(date -Is)" >> "$OUT/job.txt"
exit $RC
