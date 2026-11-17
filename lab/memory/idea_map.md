# Idea map

Status as of 17 November 2026. Results are `t_CAV` against the reference on seed 40, 4 routes, 40% CAVs,
unless stated. Cards and code are under `lab/candidates/<name>/`.

## Tried

| Idea | Field | Candidate | Result | Verdict and reason |
| --- | --- | --- | --- | --- |
| Marginal-cost learning signal | transport economics | `marginal_cost_q` | +0.08%; −0.9% with 12 routes | No gain. CAVs barely load each other (F4). Exists upstream. Cost of learning 26% lower |
| Local search on the joint assignment | optimisation | `fleet_local_search` | −0.6%; −1.1% at 60% | Slower. Optimising a pair's mean has no room (F4); one move per pair every two days is slow |
| Shared multiplicative weights per pair | online learning | `hedge_group` | −0.8% | Slower by the individualisation gap (F6). Cost of learning 45% lower |
| Proportional controller of route shares | control theory | `share_controller` | −0.8%; −2.0% with 12 routes | Same weakness as Hedge, worse with more routes. Cheapest learning (−48%) |
| Regret matching | game theory | `regret_matching` | −0.1%; −0.35% with 12 routes | Matches the reference at half the cost of learning with 4 routes (1.39 against 2.64). With 12 routes the cost advantage disappears (3.21 against 3.25) |
| Method of successive averages | transport science | `msa_switch` | −0.4%; −0.6% with 12 routes | Close to the reference, cost of learning 1.41 (3.03 with 12 routes) |
| Annealed log-linear revision | physics | `annealed_revision` | +0.09%; +0.08% with 12 routes | Ties the reference in both arenas, the only candidate not behind with 12 routes. Cost of learning 1.65 against 2.64 (2.51 against 3.25 with 12 routes) |
| Minority game with strategy tables | econophysics | `minority_game` | −0.5%; −1.8% with 12 routes | Slower, and degrades with more routes. Cheap learning (1.39) |
| Pheromone trails | biology | `pheromone` | −0.8%; −1.1% with 12 routes | Slower; pair-level trail shares the individualisation gap (F6) |
| Fitted load model, fill by departure order | operations research | `surrogate_fill` | +0.11%; −0.2% with 12 routes | Ties the reference with 4 routes (best single number so far, inside the 0.3% slack). Cost of learning 1.85 |
| Larger route set (12) | environment design | arena `p12` | −2.5% for the reference itself | The largest effect found. Not an algorithm; changes the human baseline too (F7) |
| Larger CAV share (60%) | environment design | arena `s60` | no method gains | Coordination ideas did not start to pay off |

## Not tried, with the current view of each

| Idea | View |
| --- | --- |
| React to the same-day observation | Dead in this setting: the observation has no signal (F3) |
| Recommender that hands out routes by lot | Same as the share controller in effect; would share its weakness |
| Pooled start, personal finish: learn pair-level estimates first, then let each CAV refine from them | Most direct answer to F6: aims at the reference's time with the pooled methods' learning cost. `regret_matching` and `msa_switch` already do a version of this through shared estimates for untried routes, which may be why they come closest |
| Link-level congestion model across pairs | Would capture what pair-level models miss (routes of different pairs share roads). Needs route geometry from `routes.csv`; heavier to build. Value unknown since cross-pair effects are unmeasured |
| Choosing or generating the route set as part of the method | Largest lever seen (F7). Needs care: it also moves the human baseline |
| LLM-written heuristics scored by the arena | A layer over this lab, not a method. Worth it once a setting with real headroom is found |
| Neural policies with the full observation | Upstream shows they end where the bandit ends; F3 says why |

## Design lessons

> Lessons 1, 3 and 9 and every "cost of learning" figure in this file were found wrong or unsupported by an
> independent review: see "Corrections after an independent review" in `findings.md` before using them.

1. **A CAV's problem here is "find my best of four routes".** Route gaps are large, interactions small, the day's
   information empty. Any sound learner ends within about 0.3% of the same answer.
2. **Individual estimates are necessary for the last 1%.** Pair-level decisions lose it, mostly in large pairs
   with spread-out departure times.
3. **Sharing estimates buys cheap learning.** Using the pair's experience for routes a CAV has not tried, and
   optimism for untried routes instead of random exploration, halves the cost of learning without losing final time.
4. **Starting from the shortest route is free.** 75% of CAVs end there anyway.
5. **A fleet objective needs fleet-sized interactions.** They are absent at 40% and still absent at 60%.
6. **The route set bounds everything.** A method cannot beat the best route it is offered.
8. **Ten distinct methods, one answer (17 November).** With 4 routes all ten candidates land between +0.11% and
   −0.84% of the reference; with 12 routes between +0.08% and −2.0%. Nothing reaches the 1% threshold on one seed.
   The spread between methods is smaller than the 2.5% from the route set and the 3% seed-to-seed spread. Another
   learner on the same route set is unlikely to win; the levers left are the route set and the setting.
9. **Cheap learning does not survive more routes.** Methods that halve the cost of learning with 4 routes
   (regret matching, MSA) lose that edge with 12; the annealed and pooled-share methods keep part of it.
7. **Frozen routes at test.** Every candidate fixes its routes before testing; exploration left on at test costs time.
