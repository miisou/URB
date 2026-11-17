# regret_matching

- **Idea:** Regret matching (Hart and Mas-Colell): each CAV keeps, per route, the minutes it would have saved so far by having driven that route, and plays routes with probability proportional to the positive part.
- **Changes relative to the reference:** the choice rule. The reference picks the best average; this one mixes over every route that would have been better in hindsight and stops moving once none would. Times of routes not driven come from the same estimates as in `msa_switch`.
- **Why it may help:** its play converges to the set of correlated equilibria, which contains outcomes no independent best-average learner reaches; in congestion games those can be better than the equilibrium the reference finds. From game theory.
- **Prediction:** `t_CAV` within ±1% of the reference. A gain above 1% would mean the correlated outcomes matter here.
- **Drop if:** `t_CAV` is not better than the reference on the screen seed.
