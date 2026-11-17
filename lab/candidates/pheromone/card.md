# pheromone

- **Idea:** Ant-colony routing: each pair keeps a pheromone level per route; every CAV deposits pheromone on its route in proportion to how fast the trip was, pheromone evaporates, and CAVs choose routes with probability proportional to pheromone times a personal preference for routes they found fast.
- **Changes relative to the reference:** the memory is shared and decays; choice is proportional, not greedy. For testing each CAV draws its route once from its final weights and keeps it.
- **Why it may help:** ant-colony optimisation is the standard swarm method for path problems; evaporation forgets stale information and the shared trail spreads what one CAV found to the rest of its pair.
- **Prediction:** `t_CAV` within ±1% of the reference, with a risk of herding onto one route in large pairs, which would make it worse.
- **Drop if:** `t_CAV` is not better than the reference on the screen seed.
