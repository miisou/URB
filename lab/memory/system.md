# How the environment works

Checked against URB `5457dcf` and RouteRL `routerl-nightly` (main at `ccf7212`), November 2026. *Read in code* unless marked.

## The decision

- Each vehicle has a fixed origin, destination, and departure time. They never change between days.
- One simulated day is one episode. A CAV makes **one decision per day**: the index of one of its pair's routes.
- There is no next state. The learning target of the repository's Q-learners is the reward itself.
- Days run in three phases: humans learn alone (300 days in current task configs), a share of humans becomes CAVs
  and learns (the algorithm's `training_eps`), then 100 test days. Humans are frozen after the first phase in every
  stored result (`should_humans_adapt` is false in all 581 upstream runs).
- Which humans become CAVs is drawn with the environment seed; the same seed gives the same CAV set across methods
  (*measured*: identical 414 ids in two runs on seed 40).

## Demand of `ingolstadt_custom2`

*Measured* from `networks/ingolstadt_custom2/agents.csv`.

- 1035 vehicles, 306 origin–destination pairs, departures spread over 30 minutes (seconds 5–1798).
- Pair sizes are very uneven: the median pair has 1 vehicle, 270 pairs have at most 2, but 725 vehicles sit in pairs of 5 or more.
- At 40% CAVs: 414 CAVs; 119 of them are alone in their pair, 182 are in pairs with more than 10 CAVs.

## Observation `trip_info_eta`

Seven numbers per CAV (3 + number of routes):

- one travel-time estimate per route for today: a running mean over vehicles of the same pair that departed earlier
  today and used that route, starting from the free-flow time;
- origin index, destination index, departure time. These three are constant for a CAV.

Travel times are in minutes (*measured*: values 3–6 in the logs).

## Reward

`a·own + b·group + c·others + d·all`, each a travel time (group = same kind, others = other kind), over vehicles of
the same pair. Coefficients by behaviour: selfish `(-1,0,0,0)`, collaborative `(-0.5,-0.5,0,0)`, social
`(-0.5,0,0,-0.5)`, competitive `(-2,0,1,0)`, altruistic `(0,0,0,-1)`, malicious `(0,0,1,0)`. Under `selfish`
the reward is minus the CAV's own travel time. Upstream also has `marginal_cost_coefficient_beta` in some task
configs; its implementation was not read.

## Humans (Gawron model)

- Each human keeps a cost estimate per route and updates the chosen one with learning rate `human_alpha`.
- `human_deterministic=true`: always takes the best-known route.
- `human_deterministic=false` (the default since June 2026): samples a route with probability proportional to
  `exp(beta × cost)`. It therefore keeps using routes it knows to be slower.

## Routes

- A CAV chooses among a fixed list of routes per pair; it cannot build a route.
- Without clustered routes, JanuX samples paths on the road graph, preferring short ones (`path_gen_beta`), and
  keeps `number_of_paths` distinct ones. Generation uses the environment seed, so **different seeds have different
  route sets**.
- With clustered routes, a pre-generated set under `networks/<net>/clustered_routes/` is used, with action masks
  for pairs that have fewer routes. These sets are the same for every seed.
- Every shipped environment config has `number_of_paths: 4`.
- *Measured*, seed 40, 4 routes: median free-flow time relative to the shortest is 1.00 / 1.13 / 1.26 / 1.39;
  two routes of a pair share a median 61% of their free-flow time (findings F14).

## Determinism

*Measured*: a run repeated with the same environment and algorithm seeds gives the same result to four decimals
(`tabular_q_port` against `ref_tabular_iql`, 4.2114 minutes both). Differences between methods on one seed are
therefore real for that seed. Variation between seeds is large (see findings).

## Metrics

From `analysis/metrics.py`; times in minutes.

- `t_CAV`, `t_HDV_test`, `t_test`: mean test travel time of CAVs, humans, everyone. `t_pre`, `t_HDV_pre`: before CAVs appear.
- `CAV_advantage = t_HDV_test / t_CAV`. `Effect_of_change = t_HDV_pre / t_CAV`. `Effect_of_remaining = t_HDV_pre / t_HDV_test`.
- `winrate`: 1 if `t_CAV < t_pre`. It compares CAVs with the whole system before them, not with humans after.
- `cost_of_learning`: *read in `analysis/metrics.py`*: for each vehicle, its slowest training day minus its fastest, averaged over vehicles. It is a spread, not time lost. For time lost during learning use `t_train` or the mean CAV time over training days from the trip logs.
- `t_train`: mean travel time of everyone during the learning phase.
- The leaderboard page averages reruns of the same configuration and can be sorted by any column.

## What the tabular learners really are

`iql_tabular.py` divides each observation entry by `bin_width` and floors it. With `bin_width` 100 (141 of 145
stored tabular-IQL runs) or 20 (the rest, and all tabular REINFORCE), travel times of 3–6 minutes all fall in one
bin, and the other three entries are constant. Each CAV has **one state and four values**: a multi-armed bandit
on its own travel times. The neural learners receive the full observation but behave the same way (see findings).

## Exploration schedule of the tabular reference (read in configs, 18 November)

`eps_decay` is applied once per day. Every upstream tabular config reaches epsilon 0.05 by the end of training
except `config_ing_short` (600 days), where epsilon only falls from 0.5 to 0.40. That config is the one behind the
Ingolstadt rows and this lab's reference. Test days are greedy, so test metrics are unaffected; anything measured
during training is.
