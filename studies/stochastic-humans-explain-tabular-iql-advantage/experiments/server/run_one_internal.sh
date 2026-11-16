#!/bin/bash
# Runs inside the SUMO container: repository at /app, node-local results at /app/results, venv at /venv.
set -e
cd /app
VENV=/venv/env; READY=/venv/.ready; LOCK=/venv/.lock
if [ ! -f "$READY" ]; then
    if mkdir "$LOCK" 2>/dev/null; then
        trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT
        rm -rf "$VENV"; python3 -m venv "$VENV"; source "$VENV/bin/activate"
        python -V; sumo --version | head -2 || true
        python -m pip install --upgrade pip setuptools wheel
        # The tabular learner and the baselines run on CPU: a CPU-only torch keeps the venv small.
        python -m pip install --no-cache-dir "torch>=2.6.0,<2.7.0" --index-url https://download.pytorch.org/whl/cpu
        python -m pip install --no-cache-dir -r requirements.txt
        python -m pip freeze > /venv/freeze.txt
        touch "$READY"
        rmdir "$LOCK"; trap - EXIT
    else
        while [ ! -f "$READY" ]; do [ -d "$LOCK" ] || { echo "venv setup failed" >&2; exit 1; }; sleep 5; done
    fi
fi
source "$VENV/bin/activate"
if [ -f "results/$EXP_ID/metrics/BenchmarkMetrics.csv" ]; then echo "already finished: $EXP_ID"; exit 0; fi
rm -rf "results/$EXP_ID"   # a previous attempt that did not finish
echo "--- $METHOD | $TASK_CONF | seed $SEED | $EXP_ID | $(date -Is) ---"
if [ "$METHOD" = "iql" ]; then
    python -u scripts/iql_tabular.py --id "$EXP_ID" --alg-conf config_ing_short --env-conf config_ing_short \
        --task-conf "$TASK_CONF" --net ingolstadt_custom2 --env-seed "$SEED" --torch-seed "$SEED"
elif [ "$METHOD" = "aon" ]; then
    python -u scripts/baselines.py --id "$EXP_ID" --alg-conf config1 --env-conf config_ing_short \
        --task-conf "$TASK_CONF" --net ingolstadt_custom2 --env-seed "$SEED" --model aon
else
    echo "unknown method $METHOD" >&2; exit 2
fi
echo "--- done $(date -Is) ---"
