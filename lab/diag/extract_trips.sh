#!/bin/bash
#SBATCH --job-name=urb-diag
#SBATCH --gres=gpu:0
# [TRIPS_DIR=trips_smoke] sbatch -p rknodes --qos=quick --cpus-per-task=1 --mem=4G --time=00:30:00 lab/diag/extract_trips.sh [substring ...]
set -euo pipefail
LOCAL=/scratch/tmp/$USER/urb_lab
ls "$LOCAL/results" | head -200
singularity exec --cleanenv --bind "$PWD":/app --bind "$LOCAL/results":/res --bind "$LOCAL/venv":/venv \
  /shared/sets/singularity/sumo1_26_0patched.sif /venv/env/bin/python /app/lab/diag/extract_trips.py /res /app/lab/diag/${TRIPS_DIR:-trips} "$@"
