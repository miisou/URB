# Running things

## Numbers to plan with

- One simulated day on `ingolstadt_custom2`: about 8 s with 4 routes, 12.5 s with 12 routes, on one core.
- Tabular IQL, 1000 days: 2.5 h with 4 routes, 3.5 h with 12. All-or-nothing, 600 days: 1.5–2.2 h.
- A smoke run (25 days): about 9 minutes including route generation.
- A run needs 2 CPUs and well under 12 GB. No GPU.
- When the node is busy, jobs wait in the queue; twelve submitted at once started over about three hours.

## Setup that works

- SUMO container `sumo1_26_0patched.sif`, Python 3.10 inside, `routerl-nightly`, CPU-only torch.
- Virtual environment and raw results on the node-local disk; only `exp_config.json`, `BenchmarkMetrics.csv`,
  and the end of the log come back to `lab/runs/<run>/`.
- Raw results keep per-day trip logs (`episodes/ep*.csv`, every fifth day: travel time, route, observation,
  reward per vehicle) and `routes.csv` (routes as lists of road segments with free-flow times). These made the
  analyses in findings F2–F6 possible. They live only on the node-local disk and are not backed up.

## Failures met and their fixes

| Symptom | Cause | Fix |
| --- | --- | --- |
| Job hangs for minutes before any output | Building a virtual environment on the network home directory | Build it on the node-local disk |
| Job exits with code 2 and "Stale file handle" after the simulation finished | A later submission rewrote the shared copy of a script that bash was still reading | Each job copies the code to the node-local disk and runs from the copy (in `lab/cluster/run_one.sh`) |
| Runs marked failed although metrics exist | Same as above; the error came after the metrics were written | `collect` trusts the presence of metrics, not the exit code |
| `collect` or `submit` says the cluster is unreachable | The VPN dropped; it does so roughly hourly | Reconnect and repeat; running jobs are unaffected |
| A helper `srun` never starts | The node has no free cores | Do not rely on interactive helpers while a batch is running; put the analysis in the job or wait |
| Per-arena table overwrote the default table | A path was not made arena-specific | Fixed; the default table rebuilds from `lab/runs/` at any time |

## Habits

- Smoke every new candidate before a full run, and check it locally first with `lab/tests/toy_check.py`. The toy
  model catches crashes and test-time behaviour; its numbers say nothing about SUMO.
- Submit at most twelve runs at a time.
- After a batch: `collect` for each arena, read the table, update `lab/memory/`.
- Analysis scripts that read raw logs are not in the repository yet; the logic is described in findings.
