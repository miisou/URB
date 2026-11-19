# Lab leaderboard

Generated 2026-11-18T19:44 by `lab/labctl.py table`. Do not edit by hand.

- **Arena:** `ing2_selfish40_p12`: network `ingolstadt_custom2`, task `selfish_40`, environment `lab_ing_short_p12`
- **Primary metric:** `t_CAV` (lower is better). Δ columns are the improvement in percent over the reference on the same seed; positive is better.
- **Rule:** screen on seed(s) [40]; promote at Δ ≥ 1.0%; confirm on seeds [41, 42, 43], which no candidate was screened on.
- **Candidates tried so far:** 10 (every one is listed, including dropped ones).

| Candidate | Role | Stage | Seeds | t_CAV | Δ vs `ref_tabular_iql` % | Δ vs `ref_aon` % | t_test | Effect_of_change | cost_of_learning | avg_time_lost | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ref_aon | reference | all | 40 | 4.322 | -5.26 | 0.00 | 4.537 | 1.082 | 1.651 | -5.877 | reference |
| ref_tabular_iql | reference | all | 40 | 4.106 | 0.00 | 5.00 | 4.433 | 1.139 | 3.248 | 1.089 | reference |
| annealed_revision | candidate | screen | 40 | 4.103 | 0.08 | 5.07 | 4.428 | 1.140 | 2.510 | -24.392 | dropped at screen |
| surrogate_fill | candidate | screen | 40 | 4.113 | -0.18 | 4.83 | 4.439 | 1.137 | 2.976 | -20.855 | dropped at screen |
| regret_matching | candidate | screen | 40 | 4.120 | -0.35 | 4.67 | 4.443 | 1.135 | 3.212 | -25.539 | dropped at screen |
| tabular_q_decay | candidate | screen | 40 | 4.122 | -0.40 | 4.62 | 4.443 | 1.135 | 3.047 | -15.313 | dropped at screen |
| msa_switch | candidate | screen | 40 | 4.132 | -0.64 | 4.39 | 4.445 | 1.132 | 3.025 | -24.635 | dropped at screen |
| marginal_cost_q | candidate | screen | 40 | 4.144 | -0.92 | 4.13 | 4.453 | 1.129 | 3.214 | 1.609 | dropped at screen |
| hedge_group | candidate | screen | 40 | 4.144 | -0.94 | 4.11 | 4.453 | 1.129 | 2.228 | -24.865 | dropped at screen |
| pheromone | candidate | screen | 40 | 4.149 | -1.06 | 4.00 | 4.456 | 1.127 | 3.141 | -22.224 | dropped at screen |
| minority_game | candidate | screen | 40 | 4.181 | -1.83 | 3.26 | 4.463 | 1.119 | 2.163 | -23.055 | dropped at screen |
| share_controller | candidate | screen | 40 | 4.189 | -2.03 | 3.07 | 4.472 | 1.117 | 2.198 | -23.191 | dropped at screen |
| tabular_q_port | check | smoke | 40 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | smoke ok |

## Runs

| Run | Job | t_CAV | Reference, same seed | Δ % | Note |
| --- | --- | --- | --- | --- | --- |
| p12.annealed_revision__screen_s40 | 574102 | 4.1028 | 4.1058 | 0.08 |  |
| p12.hedge_group__screen_s40 | 573819 | 4.1444 | 4.1058 | -0.94 | FAILED |
| p12.marginal_cost_q__screen_s40 | 573821 | 4.1436 | 4.1058 | -0.92 |  |
| p12.minority_game__screen_s40 | 574104 | 4.1809 | 4.1058 | -1.83 |  |
| p12.msa_switch__screen_s40 | 574098 | 4.1321 | 4.1058 | -0.64 |  |
| p12.pheromone__screen_s40 | 574106 | 4.1493 | 4.1058 | -1.06 |  |
| p12.ref_aon__screen_s40 | 573817 | 4.3220 | 4.1058 | -5.26 | FAILED |
| p12.ref_tabular_iql__screen_s40 | 573816 | 4.1058 | 4.1058 | 0.00 | FAILED |
| p12.regret_matching__screen_s40 | 574100 | 4.1203 | 4.1058 | -0.35 |  |
| p12.share_controller__screen_s40 | 573820 | 4.1891 | 4.1058 | -2.03 |  |
| p12.surrogate_fill__screen_s40 | 574108 | 4.1132 | 4.1058 | -0.18 |  |
| p12.tabular_q_decay__screen_s40 | 575535 | 4.1222 | 4.1058 | -0.40 |  |
| p12.tabular_q_port__smoke_s40 | 573743 | ran | - | - | smoke: numbers not comparable |
