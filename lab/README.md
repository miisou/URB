# Lab: from an idea to a row in the table

A small loop for trying many routing methods on URB cheaply and keeping only the ones that survive.
It sits in front of `studies/`: a candidate that is confirmed here is worth a full study; most are not.

What the runs have taught so far is kept in [`memory/`](memory/README.md). Read it before designing a candidate.

## The loop

1. **Card.** `python lab/labctl.py new <name>` creates `lab/candidates/<name>/`. Fill in `card.md` first:
   the idea, what changes relative to the reference, why it may help, a numeric prediction, and the result
   that ends the candidate. `submit` refuses a card with unfilled placeholders.
2. **Code.** Write `policy.py` against `lab/fleet.py` (one `build(ctx)` function) and put hyperparameters in
   `config.json`. A method that already has its own script uses `"kind": "script"` in `candidate.json` instead.
3. **Smoke.** `submit <name> --stage smoke`: 10 human days, 10 learning days, 5 test days. It only shows that
   the code runs and metrics are produced. Its numbers mean nothing.
4. **Screen.** `submit <name> --stage screen`: one full run on the screen seed, compared with the reference on
   the same seed. Promote at an improvement of at least `min_improvement_pct`; otherwise the candidate is dropped.
5. **Confirm.** `submit <name> --stage confirm`: the confirm seeds, which no candidate was screened on.
   Confirmed if the mean improvement reaches the threshold and at least two thirds of the seeds improve.
6. **Table.** `collect` fetches finished runs and rewrites `LEADERBOARD.md`. `ledger.csv` lists every run ever
   submitted, including failed and dropped ones.

## Rules

- **One arena.** `arena.json` fixes the network, task, environment config, seeds, primary metric, and threshold.
  Changing any of them starts a new arena with a new name and its own reference runs.
- **Paired comparison.** A candidate is compared with the reference on the same environment seed. Seed-to-seed
  spread of `t_CAV` is larger than the effects being looked for.
- **Screening selects on noise.** Picking the best of many one-seed runs overstates it. That is why confirmation
  uses different seeds, and why the table states how many candidates were tried.
- **The primary metric is absolute.** `t_CAV` in minutes. `CAV_advantage` and `Effect_of_change` are reported but
  depend on how the human baseline is configured (see the study `stochastic-humans-explain-tabular-iql-advantage`).
- **No tuning on confirm seeds.** If a confirmed candidate is changed, it is a new candidate and starts at screen.
- **Nothing is deleted.** A dropped candidate keeps its folder and its ledger rows.
- **One generated number per metric.** `LEADERBOARD.md` is rebuilt from `runs/`; it is never edited by hand.

## Where things run

Runs go to the GMUM cluster through `ssh` (VPN required for `submit`, `status`, `collect`). Each run is one
CPU-only Slurm job in the SUMO container. The virtual environment and raw simulator output stay on the
node-local disk; only `exp_config.json`, `BenchmarkMetrics.csv`, and the end of the log come back to
`lab/runs/<run-id>/`. Cluster settings are in the `cluster` block of `arena.json`; the login is read from `URB_LAB_HOST` or from the untracked file `lab/cluster.local.json` (`{"host": "user@gateway"}`).

## What this design takes from existing automated-research systems

| Source | Taken | Not taken |
| --- | --- | --- |
| Karpathy's autoresearch | A read-only evaluator, a small editable surface per candidate, one metric, a fixed budget, keep or drop | Its ratchet on a single run: here one run costs hours and is noisy, so keeping needs fresh seeds |
| FunSearch, AlphaEvolve | Candidates are programs scored by an automatic evaluator; a population of candidates, not one line of edits | Thousands of evaluations: the budget here is about a dozen full runs per night |
| AI Scientist, Agent Laboratory | Nothing structural | End-to-end autonomy and paper writing; independent audits report crashes, undocumented changes of the benchmark, and selection of which experiments to report |
| AI co-scientist | Generate, criticise, rank, with a person choosing what proceeds | The multi-agent debate; here the ranking is the arena |
| URB `studies/` | A prediction and a drop rule written before the run; independent review for what is promoted | The full proposal and report for every idea |

The audits of autonomous systems point at the same three failures: the agent changes what is measured, reports
a selected subset, and leaves no trace. The arena, the ledger, and the generated table are the answers to those.

## Open points

- The run-to-run noise at a fixed seed is not measured yet. The candidate `tabular_q_port` (the reference
  learner rewritten for the lab runner) measures it on the screen seed.
- The reference has no run on confirm seed 43 yet.
- One screen run takes about 2.5 hours on 2 CPUs. A cheaper screen (fewer days, or an emulator) would widen the loop.
