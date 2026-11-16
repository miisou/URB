#!/bin/bash
# Runs inside the SUMO container: repository at /app, node-local results at /app/results, venv at /venv.
set -e
cd /app
VENV=/venv/env; READY=/venv/.ready; LOCK=/venv/.lock
if [ ! -f "$READY" ]; then
    if mkdir "$LOCK" 2>/dev/null; then
        trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT
        rm -rf "$VENV"; python3 -m venv "$VENV"; source "$VENV/bin/activate"
        python -m pip install --upgrade pip setuptools wheel
        # Lab methods run on CPU: a CPU-only torch keeps the venv small.
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
if [ -f "results/$RUN_ID/metrics/BenchmarkMetrics.csv" ]; then echo "already finished: $RUN_ID"; exit 0; fi
rm -rf "results/$RUN_ID"   # an earlier attempt that did not finish
echo "--- $RUN_ID | $(date -Is) ---"
cat "lab/cluster/cmds/$RUN_ID.sh"
bash "lab/cluster/cmds/$RUN_ID.sh"
echo "--- done $(date -Is) ---"
