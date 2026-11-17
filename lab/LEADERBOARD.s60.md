# Lab leaderboard

Generated 2026-11-16T16:57 by `lab/labctl.py table`. Do not edit by hand.

- **Arena:** `ing2_selfish60_s60`: network `ingolstadt_custom2`, task `selfish_60`, environment `config_ing_short`
- **Primary metric:** `t_CAV` (lower is better). Δ columns are the improvement in percent over the reference on the same seed; positive is better.
- **Rule:** screen on seed(s) [40]; promote at Δ ≥ 1.0%; confirm on seeds [41, 42, 43], which no candidate was screened on.
- **Candidates tried so far:** 4 (every one is listed, including dropped ones).

| Candidate | Role | Stage | Seeds | t_CAV | Δ vs `ref_tabular_iql` % | Δ vs `ref_aon` % | t_test | Effect_of_change | cost_of_learning | avg_time_lost | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ref_aon | reference | all | 40 | 4.435 | -4.64 | 0.00 | 4.468 | 1.015 | 0.929 | -0.653 | reference |
| ref_tabular_iql | reference | all | 40 | 4.238 | 0.00 | 4.44 | 4.341 | 1.062 | 1.941 | 1.740 | reference |
| marginal_cost_q | candidate | screen | 40 | 4.242 | -0.09 | 4.35 | 4.342 | 1.061 | 1.934 | 1.713 | dropped at screen |
| hedge_group | candidate | screen | 40 | 4.276 | -0.89 | 3.58 | 4.362 | 1.053 | 1.581 | -15.719 | dropped at screen |
| fleet_local_search | candidate | screen | 40 | 4.284 | -1.07 | 3.41 | 4.366 | 1.051 | 1.710 | -4.611 | dropped at screen |
| share_controller | candidate | screen | 40 | 4.299 | -1.44 | 3.06 | 4.377 | 1.047 | 1.215 | -13.812 | dropped at screen |

## Runs

| Run | Job | t_CAV | Reference, same seed | Δ % | Note |
| --- | --- | --- | --- | --- | --- |
| s60.fleet_local_search__screen_s40 | 573747 | 4.2835 | 4.2381 | -1.07 | FAILED |
| s60.hedge_group__screen_s40 | 573749 | 4.2759 | 4.2381 | -0.89 | FAILED |
| s60.marginal_cost_q__screen_s40 | 573746 | 4.2419 | 4.2381 | -0.09 | FAILED |
| s60.ref_aon__screen_s40 | 573745 | 4.4349 | 4.2381 | -4.64 | FAILED |
| s60.ref_tabular_iql__screen_s40 | 573744 | 4.2381 | 4.2381 | 0.00 | FAILED |
| s60.share_controller__screen_s40 | 573748 | 4.2990 | 4.2381 | -1.44 | FAILED |
