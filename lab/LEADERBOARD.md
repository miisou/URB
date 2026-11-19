# Lab leaderboard

Generated 2026-11-19T12:57 by `lab/labctl.py table`. Do not edit by hand.

- **Arena:** `ing2_selfish40_v1`: network `ingolstadt_custom2`, task `selfish_40`, environment `config_ing_short`
- **Primary metric:** `t_CAV` (lower is better). Δ columns are the improvement in percent over the reference on the same seed; positive is better.
- **Rule:** screen on seed(s) [40]; promote at Δ ≥ 1.0%; confirm on seeds [41, 42, 43], which no candidate was screened on.
- **Candidates tried so far:** 15 (every one is listed, including dropped ones).

| Candidate | Role | Stage | Seeds | t_CAV | Δ vs `ref_tabular_iql` % | Δ vs `ref_aon` % | t_test | Effect_of_change | cost_of_learning | avg_time_lost | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ref_aon | reference | all | 40, 41, 42, 43 | 4.431 | -2.81 | 0.00 | 4.468 | 1.010 | 1.180 | -1.758 | reference |
| ref_tabular_iql | reference | all | 40, 41, 42, 43 | 4.310 | 0.00 | 2.72 | 4.405 | 1.038 | 2.132 | 1.203 | reference |
| static_oracle | candidate | screen | 40 | 4.194 | 0.42 | 3.50 | 4.377 | 1.075 | 0.313 | -2.299 | dropped at screen |
| surrogate_fill | candidate | screen | 40 | 4.207 | 0.11 | 3.20 | 4.381 | 1.072 | 1.854 | -9.633 | dropped at screen |
| tabular_q_decay | candidate | screen | 40 | 4.207 | 0.11 | 3.20 | 4.383 | 1.072 | 1.839 | -8.564 | dropped at screen |
| annealed_revision | candidate | screen | 40 | 4.208 | 0.09 | 3.18 | 4.380 | 1.071 | 1.645 | -12.244 | dropped at screen |
| marginal_cost_q | candidate | screen | 40 | 4.208 | 0.08 | 3.17 | 4.381 | 1.071 | 1.948 | 0.869 | dropped at screen |
| regret_matching | candidate | screen | 40 | 4.216 | -0.11 | 2.98 | 4.384 | 1.069 | 1.387 | -13.452 | dropped at screen |
| msa_switch | candidate | screen | 40 | 4.227 | -0.38 | 2.73 | 4.384 | 1.066 | 1.413 | -12.878 | dropped at screen |
| pheromone_v2 | candidate | screen | 40 | 4.228 | -0.40 | 2.71 | 4.391 | 1.066 | 1.652 | -10.860 | dropped at screen |
| minority_game | candidate | screen | 40 | 4.231 | -0.46 | 2.64 | 4.390 | 1.065 | 1.388 | -12.155 | dropped at screen |
| fleet_local_search | candidate | screen | 40 | 4.235 | -0.57 | 2.54 | 4.398 | 1.064 | 1.798 | -2.731 | dropped at screen |
| hedge_group | candidate | screen | 40 | 4.245 | -0.81 | 2.31 | 4.401 | 1.062 | 1.440 | -11.103 | dropped at screen |
| pheromone | candidate | screen | 40 | 4.247 | -0.84 | 2.28 | 4.397 | 1.062 | 1.652 | -10.743 | dropped at screen |
| share_controller | candidate | screen | 40 | 4.247 | -0.84 | 2.28 | 4.401 | 1.061 | 1.376 | -11.578 | dropped at screen |
| aon_fixed | check | screen | 40 | 4.364 | -3.63 | -0.42 | 4.463 | 1.033 | 1.312 | -3.865 | check: differs by 3.63% |
| minority_game_v2 | candidate | screen | 40 | 4.452 | -5.71 | -2.44 | 4.496 | 1.013 | 1.635 | 1.816 | dropped at screen |
| static_distant | candidate | screen | 40 | 4.811 | -14.25 | -10.71 | 4.668 | 0.937 | 0.429 | 4.028 | dropped at screen |
| tabular_q_port | check | screen | 40 | 4.211 | 0.00 | 3.09 | 4.384 | 1.070 | 2.637 | 1.746 | check: differs by 0.00% |

## Runs

| Run | Job | t_CAV | Reference, same seed | Δ % | Note |
| --- | --- | --- | --- | --- | --- |
| annealed_revision__smoke_s40 | 574083 | ran | - | - | smoke: numbers not comparable |
| annealed_revision__screen_s40 | 574101 | 4.2077 | 4.2114 | 0.09 |  |
| annealed_revision__screen_s40_a1040 | 575519 | 4.2173 | 4.2114 | -0.14 |  |
| aon_fixed__smoke_s40 | 575750 | ran | - | - | smoke: numbers not comparable |
| aon_fixed__screen_s40 | 576090 | 4.3642 | 4.2114 | -3.63 |  |
| fleet_local_search__smoke_s40 | 573367 | ran | - | - | smoke: numbers not comparable |
| fleet_local_search__screen_s40 | 573376 | 4.2354 | 4.2114 | -0.57 | no metrics file |
| hedge_group__smoke_s40 | 573369 | ran | - | - | smoke: numbers not comparable |
| hedge_group__screen_s40 | 573378 | 4.2453 | 4.2114 | -0.81 | no metrics file |
| hedge_group__screen_s40_a1040 | 575521 | 4.2364 | 4.2114 | -0.59 |  |
| marginal_cost_q__smoke_s40 | 573368 | ran | - | - | smoke: numbers not comparable |
| marginal_cost_q__screen_s40 | 573377 | 4.2081 | 4.2114 | 0.08 | no metrics file |
| minority_game__smoke_s40 | 574084 | ran | - | - | smoke: numbers not comparable |
| minority_game__screen_s40 | 574103 | 4.2309 | 4.2114 | -0.46 |  |
| minority_game_v2__smoke_s40 | 575508 | ran | - | - | smoke: numbers not comparable |
| minority_game_v2__screen_s40 | 576089 | 4.4518 | 4.2114 | -5.71 |  |
| msa_switch__smoke_s40 | 574081 | ran | - | - | smoke: numbers not comparable |
| msa_switch__screen_s40 | 574097 | 4.2272 | 4.2114 | -0.38 |  |
| pheromone__smoke_s40 | 574085 | ran | - | - | smoke: numbers not comparable |
| pheromone__screen_s40 | 574105 | 4.2465 | 4.2114 | -0.84 |  |
| pheromone_v2__smoke_s40 | 575507 | ran | - | - | smoke: numbers not comparable |
| pheromone_v2__screen_s40 | 575534 | 4.2282 | 4.2114 | -0.40 |  |
| ref_aon__screen_s40 | - | 4.3458 | 4.2114 | -3.19 | study run humdet_aon_sto_s40 |
| ref_aon__confirm_s41 | - | 4.4466 | 4.3377 | -2.51 | study run humdet_aon_sto_s41 |
| ref_aon__confirm_s42 | - | 4.4151 | 4.3598 | -1.27 | study run humdet_aon_sto_s42 |
| ref_aon__confirm_s43 | 573115 | 4.5169 | 4.3319 | -4.27 |  |
| ref_tabular_iql__screen_s40 | - | 4.2114 | 4.2114 | 0.00 | study run humdet_iql_sto_s40 |
| ref_tabular_iql__confirm_s41 | - | 4.3377 | 4.3377 | 0.00 | study run humdet_iql_sto_s41 |
| ref_tabular_iql__confirm_s42 | - | 4.3598 | 4.3598 | 0.00 | study run humdet_iql_sto_s42 |
| ref_tabular_iql__confirm_s43 | 573113 | 4.3319 | 4.3319 | 0.00 |  |
| regret_matching__smoke_s40 | 574082 | ran | - | - | smoke: numbers not comparable |
| regret_matching__screen_s40 | 574099 | 4.2161 | 4.2114 | -0.11 |  |
| regret_matching__screen_s40_a1040 | 575518 | 4.2277 | 4.2114 | -0.39 |  |
| share_controller__smoke_s40 | 573370 | ran | - | - | smoke: numbers not comparable |
| share_controller__screen_s40 | 573379 | 4.2468 | 4.2114 | -0.84 | no metrics file |
| static_distant__smoke_s40 | 575506 | ran | - | - | smoke: numbers not comparable |
| static_distant__screen_s40 | 575533 | 4.8113 | 4.2114 | -14.25 |  |
| static_oracle__smoke_s40 | 575214 | ran | - | - | smoke: numbers not comparable |
| static_oracle__screen_s40 | 575215 | 4.1939 | 4.2114 | 0.42 |  |
| surrogate_fill__smoke_s40 | 574086 | ran | - | - | smoke: numbers not comparable |
| surrogate_fill__screen_s40 | 574107 | 4.2066 | 4.2114 | 0.11 |  |
| surrogate_fill__screen_s40_a1040 | 575520 | 4.2025 | 4.2114 | 0.21 |  |
| tabular_q_decay__smoke_s40 | 575505 | ran | - | - | smoke: numbers not comparable |
| tabular_q_decay__screen_s40 | 575532 | 4.2067 | 4.2114 | 0.11 |  |
| tabular_q_port__smoke_s40 | 573108 | ran | - | - | smoke: numbers not comparable |
| tabular_q_port__screen_s40 | 573112 | 4.2114 | 4.2114 | 0.00 |  |
| tabular_q_port__screen_s40_a1040 | 575517 | 4.2105 | 4.2114 | 0.02 |  |
