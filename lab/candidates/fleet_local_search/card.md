# fleet_local_search

- **Idea:** treat the fleet's routes as one joint assignment and improve it by local search: start from the all-or-nothing assignment, change one CAV's route per origin–destination group, and keep the change only if the group's mean travel time drops.
- **Changes relative to the reference:** no per-agent learning and no exploration schedule. Days alternate between the current assignment (to estimate its cost) and a proposal. A proposal must beat the current cost by `z` standard deviations on `confirmations` separate days before it is accepted.
- **Why it may help:** the leaderboard scores the fleet's mean time, and independent learners settle in an equilibrium that need not minimise it. Local search optimises the group's mean directly, and at test time the assignment is fixed, with no residual randomness. From combinatorial optimisation; with a noise-aware acceptance rule as in stochastic local search.
- **Prediction:** `t_CAV` 1–2% lower than `ref_tabular_iql` on the screen seed; `cost_of_learning` and `avg_time_lost` clearly lower, because at most one CAV per group deviates on a proposal day.
- **Drop if:** `t_CAV` is not at least 1% better than the reference on the screen seed. A result no better than `ref_aon` would also mean the search never left its start.
