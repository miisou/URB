# pheromone_v2

- **Idea:** Ant-colony routing as in `pheromone` (shared evaporating trail per pair and route, times a personal attraction to routes the CAV found fast, proportional choice during training), with one fix: at test each CAV takes the route with the highest final weight instead of a random draw from its weights.
- **Changes relative to `pheromone`:** only `start_test`. The independent review found that v1 freezes every CAV on a randomly drawn route for all test days, so its test `t_CAV` measured the luck of one draw, not what the colony learned. Hyperparameters unchanged.
- **Changes relative to the reference:** shared, decaying memory per pair; proportional choice while learning; greedy at test.
- **Why it may help:** the trail spreads what one CAV found to the rest of its pair; the attraction term keeps individual differences (F6 says individualisation matters).
- **Prediction:** `t_CAV` clearly better than `pheromone` v1, ending between −0.4% and +0.1% against `ref_tabular_iql` on seed 40. Risk: greedy test herds a whole pair onto one route where trails dominate the attraction; that would show as a loss concentrated in pairs of more than 10 CAVs. On the toy model (`lab/tests/toy_check.py`, strong invented congestion) this happened: test 5.65 against v1's 4.87; the toy's congestion is far steeper than F4 measured in SUMO.
- **Drop if:** `t_CAV` is not better than the reference on the screen seed by the arena threshold (as every candidate).
