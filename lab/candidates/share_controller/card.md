# share_controller

- **Idea:** for each origin–destination pair, a feedback controller sets the share of the pair's CAVs on each route and shifts share from slower routes to faster ones in proportion to the relative difference in travel time.
- **Changes relative to the reference:** nothing is sampled. Each day the pair's CAVs are split over routes by the current shares (largest remainder), keeping as many CAVs as possible on yesterday's route. After the day, each route's time estimate is updated from the CAVs that used it and the shares are multiplied by `exp(−gain × (route time − share-weighted mean) / mean)`. Unused routes keep their free-flow estimate until tried, so each is tried once. The final split is used for testing.
- **Why it may help:** it reaches the same equal-times split that learners look for, but deterministically: no exploration days and no sampling noise in the split. This is the proportional-switch adjustment known from day-to-day traffic dynamics and feedback route guidance.
- **Prediction:** `t_CAV` within ±1% of `ref_tabular_iql`; `cost_of_learning` at least 50% lower.
- **Drop if:** `t_CAV` is more than 1% worse than the reference on the screen seed, or `cost_of_learning` is not lower. Promotion on `t_CAV` needs the usual 1% improvement. Shares that keep oscillating at the end of training (reported in the log) would also end it at this gain.
