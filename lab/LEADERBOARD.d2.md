# Lab leaderboard

Generated 2026-11-19T12:57 by `lab/labctl.py table`. Do not edit by hand.

- **Arena:** `ing2x2_selfish40_d2`: network `ingolstadt_custom2_d2`, task `selfish_40`, environment `config_ing_short`
- **Primary metric:** `t_CAV` (lower is better). Δ columns are the improvement in percent over the reference on the same seed; positive is better.
- **Rule:** screen on seed(s) [40]; promote at Δ ≥ 1.0%; confirm on seeds [41, 42, 43], which no candidate was screened on.
- **Candidates tried so far:** 5 (every one is listed, including dropped ones).

| Candidate | Role | Stage | Seeds | t_CAV | Δ vs `ref_tabular_iql` % | Δ vs `ref_aon` % | t_test | Effect_of_change | cost_of_learning | avg_time_lost | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ref_aon | reference | all | 40 | 6.229 | -9.39 | 0.00 | 6.313 | 0.971 | 3.372 | 8.421 | reference |
| ref_tabular_iql | reference | all | 40 | 5.694 | 0.00 | 8.59 | 5.868 | 1.062 | 11.731 | 37.734 | reference |
| tabular_q_decay | candidate | screen | 40 | 5.700 | -0.10 | 8.50 | 5.868 | 1.061 | 8.892 | 6.761 | dropped at screen |
| hedge_group | candidate | screen | 40 | 5.747 | -0.93 | 7.73 | 5.975 | 1.052 | 11.975 | 2.703 | dropped at screen |
| aon_fixed | check | screen | 40 | 5.920 | -3.96 | 4.97 | 6.025 | 1.021 | 9.564 | 21.627 | check: differs by 3.96% |
| annealed_revision | candidate | screen | 40 | 6.025 | -5.82 | 3.27 | 6.084 | 1.004 | 23.769 | 75.489 | dropped at screen |
| regret_matching | candidate | - | - | n/a | n/a | n/a | n/a | n/a | n/a | n/a | failed |
| surrogate_fill | candidate | - | - | n/a | n/a | n/a | n/a | n/a | n/a | n/a | failed |
| tabular_q_port | check | smoke | 40 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | smoke ok |

## Runs

| Run | Job | t_CAV | Reference, same seed | Δ % | Note |
| --- | --- | --- | --- | --- | --- |
| d2.annealed_revision__screen_s40 | 576601 | 6.0254 | 5.6942 | -5.82 |  |
| d2.aon_fixed__screen_s40 | 576605 | 5.9197 | 5.6942 | -3.96 |  |
| d2.hedge_group__screen_s40 | 576604 | 5.7473 | 5.6942 | -0.93 |  |
| d2.ref_aon__screen_s40 | 576092 | 6.2290 | 5.6942 | -9.39 |  |
| d2.ref_tabular_iql__screen_s40 | 576091 | 5.6942 | 5.6942 | 0.00 |  |
| d2.tabular_q_decay__screen_s40 | 576093 | 5.6997 | 5.6942 | -0.10 |  |
| d2.tabular_q_port__smoke_s40 | 575509 | ran | - | - | smoke: numbers not comparable |

## Not finished

| Run | Job | Status | Note |
| --- | --- | --- | --- |
| d2.regret_matching__screen_s40 | 576602 | failed | FAILED |
| d2.surrogate_fill__screen_s40 | 576603 | failed | FAILED |
