# msa_switch

- **Idea:** Method of successive averages: all CAVs start on the shortest route, and each day a shrinking share of them (about `1/(1 + day/step_scale)`) moves to the route its estimates currently say is fastest.
- **Changes relative to the reference:** no value learning and no random exploration. Estimates are the CAV's own running mean where it has driven, its pair's mean elsewhere, free-flow time for untried routes.
- **Why it may help:** this is the classical way to compute a traffic equilibrium in transport science; the shrinking step damps the oscillation that makes naive best response fail. It moves the whole fleet early and almost nobody late, so the cost of learning should be low.
- **Prediction:** `t_CAV` within ±1% of `ref_tabular_iql`; `cost_of_learning` at least 30% lower.
- **Drop if:** `t_CAV` is not better than the reference on the screen seed.
