# Lab leaderboard

Generated 2026-11-16T12:32 by `lab/labctl.py table`. Do not edit by hand.

- **Arena:** `ing2_selfish40_v1`: network `ingolstadt_custom2`, task `selfish_40`, environment `config_ing_short`
- **Primary metric:** `t_CAV` (lower is better). Δ columns are the improvement in percent over the reference on the same seed; positive is better.
- **Rule:** screen on seed(s) [40]; promote at Δ ≥ 1.0%; confirm on seeds [41, 42, 43], which no candidate was screened on.
- **Candidates tried so far:** 4 (every one is listed, including dropped ones).

| Candidate | Role | Stage | Seeds | t_CAV | Δ vs `ref_tabular_iql` % | Δ vs `ref_aon` % | t_test | Effect_of_change | cost_of_learning | avg_time_lost | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ref_aon | reference | all | 40, 41, 42, 43 | 4.431 | -2.81 | 0.00 | 4.468 | 1.010 | 1.180 | -1.758 | reference |
| ref_tabular_iql | reference | all | 40, 41, 42, 43 | 4.310 | 0.00 | 2.72 | 4.405 | 1.038 | 2.132 | 1.203 | reference |
| marginal_cost_q | candidate | screen | 40 | 4.208 | 0.08 | 3.17 | 4.381 | 1.071 | 1.948 | 0.869 | dropped at screen |
| fleet_local_search | candidate | screen | 40 | 4.235 | -0.57 | 2.54 | 4.398 | 1.064 | 1.798 | -2.731 | dropped at screen |
| hedge_group | candidate | screen | 40 | 4.245 | -0.81 | 2.31 | 4.401 | 1.062 | 1.440 | -11.103 | dropped at screen |
| share_controller | candidate | screen | 40 | 4.247 | -0.84 | 2.28 | 4.401 | 1.061 | 1.376 | -11.578 | dropped at screen |
| tabular_q_port | check | screen | 40 | 4.211 | 0.00 | 3.09 | 4.384 | 1.070 | 2.637 | 1.746 | check: differs by 0.00% |

## Runs

| Run | Job | t_CAV | Reference, same seed | Δ % | Note |
| --- | --- | --- | --- | --- | --- |
| fleet_local_search__smoke_s40 | 573367 | ran | - | - | smoke: numbers not comparable |
| fleet_local_search__screen_s40 | 573376 | 4.2354 | 4.2114 | -0.57 | no metrics file |
| hedge_group__smoke_s40 | 573369 | ran | - | - | smoke: numbers not comparable |
| hedge_group__screen_s40 | 573378 | 4.2453 | 4.2114 | -0.81 | no metrics file |
| marginal_cost_q__smoke_s40 | 573368 | ran | - | - | smoke: numbers not comparable |
| marginal_cost_q__screen_s40 | 573377 | 4.2081 | 4.2114 | 0.08 | no metrics file |
| ref_aon__screen_s40 | - | 4.3458 | 4.2114 | -3.19 | study run humdet_aon_sto_s40 |
| ref_aon__confirm_s41 | - | 4.4466 | 4.3377 | -2.51 | study run humdet_aon_sto_s41 |
| ref_aon__confirm_s42 | - | 4.4151 | 4.3598 | -1.27 | study run humdet_aon_sto_s42 |
| ref_aon__confirm_s43 | 573115 | 4.5169 | 4.3319 | -4.27 |  |
| ref_tabular_iql__screen_s40 | - | 4.2114 | 4.2114 | 0.00 | study run humdet_iql_sto_s40 |
| ref_tabular_iql__confirm_s41 | - | 4.3377 | 4.3377 | 0.00 | study run humdet_iql_sto_s41 |
| ref_tabular_iql__confirm_s42 | - | 4.3598 | 4.3598 | 0.00 | study run humdet_iql_sto_s42 |
| ref_tabular_iql__confirm_s43 | 573113 | 4.3319 | 4.3319 | 0.00 |  |
| share_controller__smoke_s40 | 573370 | ran | - | - | smoke: numbers not comparable |
| share_controller__screen_s40 | 573379 | 4.2468 | 4.2114 | -0.84 | no metrics file |
| tabular_q_port__smoke_s40 | 573108 | ran | - | - | smoke: numbers not comparable |
| tabular_q_port__screen_s40 | 573112 | 4.2114 | 4.2114 | 0.00 |  |
