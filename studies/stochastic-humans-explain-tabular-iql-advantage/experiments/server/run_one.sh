#!/bin/bash
#SBATCH --job-name=urb-humdet
#SBATCH --partition=rknodes
#SBATCH --gres=gpu:0
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=studies/stochastic-humans-explain-tabular-iql-advantage/experiments/server/logs/slurm-%j.out
# One run of the study. Submit from the repository root:
#   sbatch <this file> <method: iql|aon> <task-conf> <seed> <exp-id>
# The venv and the raw results live on the node-local disk of bonk (/scratch); the home
# directory is on NFS, where building a venv hung. Compact evidence is copied back at the end.
set -euo pipefail
METHOD=$1; TASK_CONF=$2; SEED=$3; EXP_ID=$4
PATH_PROGRAM="${PATH_PROGRAM:-$HOME/URB-study}"
CONTAINER="${PATH_SUMO_CONTAINER:-/shared/sets/singularity/sumo1_26_0patched.sif}"
STUDY="$PATH_PROGRAM/studies/stochastic-humans-explain-tabular-iql-advantage/experiments"
SRV="$STUDY/server"
LOCAL="${LOCAL_BASE:-/scratch/tmp/$USER/urb_humdet}"
mkdir -p "$SRV/logs" "$LOCAL/venv" "$LOCAL/results" "$LOCAL/logs"
echo "job $SLURM_JOB_ID on $(hostname): $METHOD $TASK_CONF seed $SEED id $EXP_ID, start $(date -Is)"
set +e
singularity exec --cleanenv \
    --env METHOD="$METHOD" --env TASK_CONF="$TASK_CONF" --env SEED="$SEED" --env EXP_ID="$EXP_ID" \
    --bind "$PATH_PROGRAM":/app --bind "$LOCAL/results":/app/results --bind "$LOCAL/venv":/venv \
    "$CONTAINER" /bin/bash "$SRV/run_one_internal.sh" > "$LOCAL/logs/run_${EXP_ID}_${SLURM_JOB_ID}.txt" 2>&1
RC=$?
set -e
# Copy compact evidence back to the shared home: settings, metrics, losses, plots, and the log tail.
OUT="$STUDY/runs/$EXP_ID"; mkdir -p "$OUT"
R="$LOCAL/results/$EXP_ID"
for p in exp_config.json metrics losses plots; do [ -e "$R/$p" ] && cp -r "$R/$p" "$OUT/" || true; done
grep -vE "Downloading|Collecting|Using cached|Requirement already" "$LOCAL/logs/run_${EXP_ID}_${SLURM_JOB_ID}.txt" | tr '\r' '\n' | tail -200 > "$OUT/log_tail_${SLURM_JOB_ID}.txt" || true
[ -f "$LOCAL/venv/freeze.txt" ] && cp "$LOCAL/venv/freeze.txt" "$STUDY/server/pip_freeze.txt" || true
echo "exit code $RC, end $(date -Is)"
exit $RC
