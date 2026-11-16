# Results

The study was run following `studies/_template`: the hypothesis, metric, thresholds, seeds, and run limit in
[PROPOSAL.md](PROPOSAL.md) were fixed before the runs. The template's final report and independent review
were not written; this file is a plain summary.

## Runs

Twelve runs on `ingolstadt_custom2`, 40% selfish CAVs, seeds 40–42: tabular IQL (`config_ing_short`,
600 learning days) and the all-or-nothing baseline, each with sampling humans (`selfish_40`) and with
deterministic humans (`selfish_40_humdet`). All twelve finished; none was excluded or repeated.
Settings and metrics of each run are under `experiments/runs/`; the launch scripts and the package list
are under `experiments/server/`. RouteRL came from `routerl-nightly`, SUMO from the container
`sumo1_26_0patched.sif`.

One earlier job was cancelled before any simulation started, because building the Python environment on a
network file system hung. It was resubmitted unchanged.

## Main metric

`Effect_of_change = t_HDV_pre / t_CAV`, per seed.

| Method | Humans | Seed 40 | Seed 41 | Seed 42 | Median | `t_HDV_pre`, min | `t_CAV`, min |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Tabular IQL | sampling | 1.070 | 1.024 | 1.037 | 1.037 | 4.49 | 4.30 |
| Tabular IQL | deterministic | 1.014 | 0.971 | 0.9999 | 0.9999 | 4.24 | 4.26 |
| All-or-nothing | sampling | 1.037 | 0.999 | 1.024 | 1.024 | 4.49 | 4.40 |
| All-or-nothing | deterministic | 0.979 | 0.945 | 0.974 | 0.974 | 4.24 | 4.39 |

The last two columns are means over the three seeds.

## Outcome by the rules of the proposal

- Sampling humans: all three seeds and the median reach 1.02. The advantage is reproduced.
- Deterministic humans: two of three seeds and the median are below 1.00, so the rule for "supported" is met.

It is met by the narrowest margin: seed 42 gives 0.99992 and seed 40 is above 1.00. The supported reading
is that the advantage disappears (about 1.00 instead of about 1.04), not that CAVs become slower than
deterministic humans.

## What else the runs show

- Switching the human choice rule alone changes the human baseline from 4.49 to 4.24 minutes, about 6%.
  The CAVs' own time barely moves (4.30 and 4.26 minutes).
- The all-or-nothing baseline, which learns nothing, has a median `Effect_of_change` of 1.024 against
  sampling humans. A ratio above 1 in that setting is therefore not evidence of learning.
- Tabular IQL is faster than all-or-nothing in absolute time in both settings, by 2–3%.

## Not done

- The check whether deterministic humans had settled by day 300, listed in the proposal, was not computed.
- One network, one CAV share, one learner. Existing results suggest Provins behaves differently.
