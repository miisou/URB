# annealed_revision

- **Idea:** Log-linear learning with a cooling temperature: each day a fraction of CAVs reconsiders and picks a route with probability proportional to `exp(-estimated time / temperature)`; the temperature falls geometrically to near zero.
- **Changes relative to the reference:** revisions are asynchronous and temperature-driven instead of ε-greedy; early on CAVs accept worse routes often, late almost never. Same estimates as `msa_switch`.
- **Why it may help:** in potential games, which congestion games are, this dynamic concentrates on the minimiser of the potential as the temperature falls, and the annealing lets the fleet leave poor local arrangements. It is simulated annealing from statistical physics applied to route choice.
- **Prediction:** `t_CAV` within ±1% of the reference.
- **Drop if:** `t_CAV` is not better than the reference on the screen seed.
