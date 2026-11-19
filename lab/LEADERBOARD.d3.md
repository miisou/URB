# Lab leaderboard

Generated 2026-11-19T12:58 by `lab/labctl.py table`. Do not edit by hand.

- **Arena:** `ing2x3_selfish40_d3`: network `ingolstadt_custom2_d3`, task `selfish_40`, environment `config_ing_short`
- **Primary metric:** `t_CAV` (lower is better). Δ columns are the improvement in percent over the reference on the same seed; positive is better.
- **Rule:** screen on seed(s) [40]; promote at Δ ≥ 1.0%; confirm on seeds [41, 42, 43], which no candidate was screened on.
- **Candidates tried so far:** 1 (every one is listed, including dropped ones).

| Candidate | Role | Stage | Seeds | t_CAV | Δ vs `ref_tabular_iql` % | Δ vs `ref_aon` % | t_test | Effect_of_change | cost_of_learning | avg_time_lost | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ref_aon | reference | all | 40 | 16.683 | n/a | 0.00 | 16.308 | 0.798 | 31.168 | 151.366 | reference |
| ref_tabular_iql | reference | - | - | n/a | n/a | n/a | n/a | n/a | n/a | n/a | reference |
| tabular_q_decay | candidate | - | - | n/a | n/a | n/a | n/a | n/a | n/a | n/a | no finished run |
| tabular_q_port | check | smoke | 40 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | smoke ok |

## Runs

| Run | Job | t_CAV | Reference, same seed | Δ % | Note |
| --- | --- | --- | --- | --- | --- |
| d3.ref_aon__screen_s40 | 576607 | 16.6826 | n/a | n/a |  |
| d3.tabular_q_port__smoke_s40 | 575749 | ran | - | - | smoke: numbers not comparable |

## Not finished

| Run | Job | Status | Note |
| --- | --- | --- | --- |
| d3.ref_tabular_iql__screen_s40 | 576606 | running |  |
| d3.tabular_q_decay__screen_s40 | 576608 | running |  |
