# static_oracle

- **Idea:** a diagnostic, not a method. Every CAV drives one fixed route for the whole run: the route with the lowest mean travel time in a table (CAV, route) pooled from the trip logs of eleven earlier runs on the same seed (`lab/diag/make_oracle.py`).
- **Changes relative to the reference:** no learning and no exploration; ten nominal training days. The assignment uses information from other runs, including their test days, so this is not a leaderboard entry.
- **Why it may help:** finding F10 says a CAV's time depends on its own route only. If so, the table's prediction holds when all CAVs take their table-best routes at once.
- **Prediction:** `t_CAV` 4.196 on seed 40, that is 0.37% below `ref_tabular_iql`, give or take 0.2%. It may come out a little higher because the best route was picked on noisy means.
- **Drop if:** not applicable as a method. A `t_CAV` above the reference's 4.211 would contradict F10: the times would then depend on the joint arrangement.
