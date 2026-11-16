# Hypothesis proposal

Written before the twelve runs, following `studies/_template/PROPOSAL.md`. The outcome is in [RESULTS.md](RESULTS.md).

## Study details

- **Study:** Stochastic human route choice explains the tabular-IQL advantage in Ingolstadt
- **Date proposed:** 2026-11-15
- **URB revision:** `5457dcf`, plus one new task configuration, `config/task_config/selfish_40_humdet.json` (a copy of `selfish_40.json` with `human_deterministic` set to `true`)
- **Keywords:** humans, deterministic, tabularql, ingolstadt, baselines

## Hypothesis

**In `ingolstadt_custom2` with 40% selfish CAVs, tabular IQL beats the learned human baseline only when humans sample their routes: with `human_deterministic=false` its `Effect_of_change` is at least 1.02, and with `human_deterministic=true`, everything else unchanged, it falls below 1.00.**

### Reason

With `human_deterministic=false`, a Gawron human samples a route with probability proportional to `exp(beta × cost)`, so it keeps taking routes it already knows to be slower. With `true` it always takes its best-known route. A CAV that learns one good fixed route can therefore beat sampling humans without routing better than a human who acts on the same knowledge.

Results already in `results/` point this way, but do not isolate the factor:

- April runs (`ingolstadt_custom`, deterministic humans, 200 human-learning days): `t_HDV_pre` ≈ 4.20 min, best CAV result 4.24 min (`iql`), CAV advantage 0.99.
- Runs since June (`ingolstadt_custom2`, sampling humans, 300 days): `t_HDV_pre` 4.47 min without clustered routes and 4.81–4.86 min with them; tabular IQL reaches `t_CAV` ≈ 4.32 min, CAV advantage 1.03.
- One `mappo_clusters` run on `ingolstadt_custom2` with deterministic humans and 200 days: `t_HDV_pre` 4.23 min, `t_CAV` 4.55 min, CAV advantage 0.94.

Between the first two groups the network, the human-learning length, the observation, the training length, and the human choice rule all changed together. This study changes the human choice rule alone.

### Main alternative explanation

The advantage comes from the learner and its training budget. Tabular IQL with `trip_info_eta` may find routes that are faster than what deterministic Gawron humans converge to, in which case the advantage survives the change of the human choice rule.

## Scope

- **Network and demand:** `ingolstadt_custom2` with its recorded demand
- **Task and CAV behaviour:** `selfish_40` (sampling humans) and `selfish_40_humdet` (deterministic humans); in both, humans learn for 300 days and do not adapt during CAV learning
- **CAV share:** 40%
- **Methods and observations:** Tabular IQL (`scripts/iql_tabular.py`, algorithm config `config_ing_short`, environment config `config_ing_short`: `trip_info_eta`, four JanuX routes, no clustered routes). The all-or-nothing baseline (`scripts/baselines.py --model aon`, same environment and task configs) is run as a reference
- **Training and testing:** 600 CAV-learning days for tabular IQL, 200 days for AON (its default), 100 test days
- **Not covered:** Other networks, CAV shares, behaviours, clustered routes, neural learners, adapting humans, other human models, and the separate effects of human-learning length or `human_beta`

## How the result will be judged

- **Main metric:** `Effect_of_change = t_HDV_pre / t_CAV` from `metrics/BenchmarkMetrics.csv`, per seed, for tabular IQL in each human condition
- **Smallest meaningful effect:** 0.02 in the ratio (the threshold used in `independent-tabular-iql-cannot-beat-humans-provins`)
- **Support the hypothesis if:** With sampling humans, at least two of three seeds and the median reach 1.02; and with deterministic humans, at least two of three seeds and the median are below 1.00
- **Falsify the hypothesis if:** With deterministic humans, at least two of three seeds and the median reach 1.02
- **Call the result inconclusive if:** Neither rule is met, the sampling-human condition fails to reproduce an advantage of at least 1.02, or a fair comparison cannot be completed

Other metrics may help explain the result, but they must not replace the main metric after the results are known.

The following are reported descriptively and do not change the assessment:

- `t_HDV_pre` in each human condition, to show how much the choice rule alone changes the human baseline.
- `t_CAV` in absolute minutes in each condition.
- `t_CAV` of tabular IQL against `t_CAV` of AON under the same seed and human condition. No baseline has yet been run in the post-June setting.
- Whether deterministic humans have settled by day 300: the spread of mean human travel time over the last 50 human-learning days, per seed.

## Experiment design

- **Changed factor:** `human_deterministic` (`false` in `selfish_40`, `true` in `selfish_40_humdet`)
- **Settings kept fixed:** Network, demand, route generation, CAV share, CAV behaviour, human model and its `alpha`, `beta`, and `beta_randomness`, human-learning length, observation, learner, learning parameters, test length, and metric calculation
- **Environment seeds:** 40, 41, and 42, matched between the two human conditions and between tabular IQL and AON
- **Model seeds:** 40, 41, and 42 respectively for tabular IQL; AON has no model seed
- **Number of repeat runs and why it is enough:** Three seeds per cell. Existing tabular results on this network vary by about 0.001–0.02 in CAV advantage across seeds, while the decision thresholds are 0.02 apart, so three seeds can separate the two outcomes if the effect is as large as the existing results suggest; anything smaller or mixed is called inconclusive
- **Reasons a run may be excluded:** Failure to finish, corrupt or missing output, or a verified implementation error unrelated to the tested condition. Poor performance, teleports, and unsettled human travel times are not exclusion reasons; unsettled humans are reported

## Run limit

Twelve runs: tabular IQL and AON, each under two human conditions and three seeds. A run that fails for a technical reason may be repeated once with the same seeds. No further conditions, seeds, or training budgets are added after the first result is seen.

## Known limits

- One network, one CAV share, one learner. The result does not show what drives the advantage in Provins, where existing results suggest CAVs are also faster in absolute minutes.
- Deterministic Gawron humans may oscillate between routes instead of settling. That would make their baseline worse for a reason other than the one tested; the settling check above reports it but cannot correct for it.
- Which human choice rule is the more realistic one is outside this study. A supported hypothesis says what the reported advantage measures; it does not say that either setting is wrong.
- The proposal was written after inspecting the existing results listed under "Reason". The twelve runs themselves have not been made.
- 600 CAV-learning days follow the existing short configuration. A longer budget might change the deterministic-human result and would be a separate hypothesis.
