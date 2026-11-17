# minority_game

- **Idea:** Minority game: each CAV holds a few fixed random strategies, each a table from the pair's recent history (which route was fastest on the last days) to a route, plus one that always takes the shortest route; it plays whichever strategy would have earned the least time so far.
- **Changes relative to the reference:** there are no value estimates per route in the decision: the CAV selects among whole strategies, and strategies react to recent history. Heterogeneous strategy sets make the CAVs of a pair spread out without any coordination.
- **Why it may help:** route choice with congestion has the structure of the El Farol and minority games from econophysics, where the known result is that agents with diverse history-based strategies use the scarce resource better than agents that all learn the same thing.
- **Prediction:** uncertain. Either clearly worse (the history carries no signal, as the same-day observation did not) or a visible gain in large pairs.
- **Drop if:** `t_CAV` is not better than the reference on the screen seed.
