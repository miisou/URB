# Literature: what is benchmarked, compared, and counted as a contribution

Read on 17 November 2026 from abstracts and partial full texts. "Summary only" marks numbers taken from an
automatic summary of a page and not checked against the PDF.

## Work on URB and RouteRL (the benchmark's own group)

| Work | Type of contribution | Setting | What is compared and measured |
| --- | --- | --- | --- |
| URB, NeurIPS 2025 D&B, arXiv 2505.17734 | Benchmark | St. Arnoult, Provins, Ingolstadt; 40% CAVs; 4 routes from JanuX; 200 human days, 6000 training days | IPPO, IQL, MAPPO, QMIX against Human, all-or-nothing, Random. Travel times (CAV, human, before), cost of training, win rate, speed and mileage change. No single ranking metric. Finding: MARL rarely beats humans, none beats all-or-nothing (summary only) |
| RouteRL, SoftwareX 2025, arXiv 2502.20065 | Framework | SUMO, day-to-day route choice | — |
| Position paper, arXiv 2502.13188 | Finding | 2-route toy network; Ingolstadt, 4 routes | Seven MARL algorithms; only IPPO and MAPPO converge; CAVs end slower than the human-only baseline (summary only) |
| Social awareness, arXiv 2510.11410 | Reward design | 2-route toy network, 22 agents; St. Arnoult | Reward = own time + bounded sum of counterfactual effects on others (re-simulation with the agent removed). Toy: CAV time 62–66 s to 57–58 s. St. Arnoult: about 0.4% for the CAV group (summary only) |
| Social impact of CAVs, Sci. Rep. 2025, arXiv 2409.12839 | Finding | Two-route bottleneck with an analytic delay function, no RL | Five fleet strategies; the selfish fleet's advantage reverses near a 25% share; humans can end worse off |
| Collective behaviours, arXiv 2509.22216 | Finding | DQN agents with six reward-defined behaviours | Effect on human times |
| Wardropian cycles, arXiv 2507.19675 | Theory and heuristic | Assignment that is optimal on average and fair over days | — |
| Exclusive clubs, arXiv 2510.12862; mediator games, arXiv 2608.09894 | Theory | Coalitions and competing routing services | — |
| OpenURB (archived October 2026) | Benchmark variant | CAV population changes during the run | Six MARL methods; adds switch cost and recovery metrics |
| Repository `HRL_leaderboard` | Method under development | Fork of URB | A feudal hierarchical script; no results published |

No paper from outside the group was found that reports a new method on URB. One AAMAS 2026 paper surfaced in the
search but could not be read.

## Other ways the same problem is benchmarked

| Line | Environment | Metric | Typical claim |
| --- | --- | --- | --- |
| MARL for traffic assignment (for example arXiv 2506.17029) | Analytic link delay functions; Sioux Falls, Anaheim; k-shortest routes, up to 6 | Relative gap to user equilibrium or system optimum | Agents redefined as origin–destination routers; gap 95% lower than Frank–Wolfe after 10 steps (summary only) |
| Sequential route recommendation for system optimum (arXiv 2505.20889) | Analytic | Total travel time against the known optimum | Design of the route action set strongly affects convergence and final quality |
| Toll-based Q-learning (Ramos, da Silva, Bazzan, 2018–2020) | Analytic route-choice games | Distance to system optimum | Marginal-cost tolls make selfish learners reach the optimum; about 9% less congestion |
| LLM agents in day-to-day dynamics (arXiv 2511.06260) | Analytic; Sioux Falls | Equilibrium gap, route shares | Behavioural realism, not performance |
| RESCO, FLOW | SUMO | Delay, throughput | Signal control and vehicle control, not route choice |

## What this implies for a contribution on URB

- **Two measuring sticks exist.** The assignment literature measures distance to a known optimum on analytic
  networks. URB measures realised travel times in a microsimulation with a human model and has no known optimum.
  A method paper on URB therefore needs its own reference point; finding F10 supplies one (the per-CAV table and
  its ceiling).
- **The group's published innovations are reward designs and findings, not learners.** Their own reward design
  gains about 0.4% on a real network, the same order as everything measured here. F4 explains it: CAVs barely load
  each other, so the term being added is close to zero.
- **Large gains in the literature come from settings with strong interaction:** two-route bottlenecks, analytic
  delay functions with steep congestion, 100% fleets. `ingolstadt_custom2` at 40% is not such a setting.
- **The route set is a recognised lever.** The route-recommendation work reports that the action set's design
  matters more than the learner; all URB rows use a fixed set of 4.
- **What would count as new:** (a) an explanation of why learners tie on URB networks, with the diagnostic that
  shows it; (b) a characterisation of which networks or shares have real interaction, so that coordination can
  matter; (c) a method that acts on the route set while humans keep theirs.
