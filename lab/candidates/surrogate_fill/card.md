# surrogate_fill

- **Idea:** Model-based assignment: fit, for each pair and route, a line from the number of the pair's CAVs on the route to the route's time, then assign CAVs in departure order, each to the route with the lowest predicted time plus the delay it adds to those already placed, plus a personal correction.
- **Changes relative to the reference:** the fleet is planned, not learned by trial. The first `explore_days` use random routes to identify the model; after that the plan is recomputed daily from the refitted model. The personal correction is each CAV's running deviation from the pair's model, which captures departure-time effects.
- **Why it may help:** surrogate-model optimisation is the standard answer in operations research when a simulator is expensive, and filling in departure order is online load balancing. With the personal correction it can individualise routes, which pooled methods so far could not.
- **Prediction:** `t_CAV` 0–1% better than the reference; `cost_of_learning` higher in the first 60 days and lower after.
- **Drop if:** `t_CAV` is not better than the reference on the screen seed.
