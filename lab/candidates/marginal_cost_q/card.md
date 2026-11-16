# marginal_cost_q

- **Idea:** keep the reference learner, but let each CAV learn from an estimate of its marginal cost to the fleet: its own travel time plus the delay it adds to the other fleet CAVs that share its route.
- **Changes relative to the reference:** the learner is the same stateless ε-greedy value learner with the reference's hyperparameters. Only the learning signal changes: `own time + slope × (CAVs of the same origin–destination pair on the same route − 1)`. The slope is fitted online, per pair and route, by regressing the route's mean time on the number of fleet CAVs using it; it is zero until the fit has enough varied data and is never negative.
- **Why it may help:** selfish learners converge to an equilibrium; pricing each choice at its marginal cost moves that equilibrium towards the fleet optimum (Pigou's argument, standard in transport economics). It is the cheapest test of whether equilibrium and fleet optimum differ on this network.
- **Prediction:** `t_CAV` about 1% lower than `ref_tabular_iql` on the screen seed. Pairs with a single CAV are unaffected, so the whole effect must come from the larger pairs.
- **Drop if:** `t_CAV` is not at least 1% better than the reference on the screen seed. Fitted slopes that stay at zero would mean the fleet's own load does not measurably change route times, which ends this family of ideas, not just this candidate.
