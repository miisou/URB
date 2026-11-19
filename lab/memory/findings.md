# Findings

All on `ingolstadt_custom2`, sampling humans, tabular learners with 600 learning days, unless stated.
"Reference" is `ref_tabular_iql` (`scripts/iql_tabular.py`, `config_ing_short`). Times in minutes.

## F1. Stochastic humans explain the tabular-IQL advantage (15 Nov, 12 runs, seeds 40–42)

`Effect_of_change` medians: IQL 1.037 with sampling humans, 0.9999 with deterministic humans; all-or-nothing
1.024 and 0.974. CAV time is 4.30 and 4.26 in the two settings. Evidence: branch
`study/stochastic-humans-cav-advantage`. Confidence: good for this network and share; the deterministic verdict
passed its rule by a hair (one seed at 0.99992).

## F2. The reference is a per-vehicle bandit and already near its own optimum (16 Nov, seed 40)

From the per-day trip logs of the reference run:

- In the test phase every CAV uses one route. Its own time varies day to day by a median 0.04 min.
- By late-training averages, 12% of CAVs are not on their best route; switching them would save about **0.3%** of fleet time.
- The gap between a CAV's best and second-best route is a median 0.30 min; for 29% of CAVs it is below 0.1 min.

Confidence: one seed; the 0.3% rests on noisy averages taken during exploration.

## F3. Today's observation carries no usable signal (16 Nov, seed 40)

Within a CAV, the correlation between the anomaly of today's estimate for its route and the anomaly of its own
travel time is 0.003. The estimate is also biased low by about 1.1 min. This matches the upstream study in which
dynamic ETA did not help neural IQL. A method that reacts to the same-day observation has nothing to react to
in this setting.

## F4. CAVs barely affect each other (16 Nov, seed 40)

In pairs of 8 or more CAVs, one more fleet CAV on the same pair and route adds a median 0.012 min (mean 0.020;
largest 0.24). That is about twenty times smaller than the typical gap between routes. Coordination inside a pair
therefore has little to gain. Cross-pair effects on shared road segments were not measured.

## F5. Where learning beats all-or-nothing (16 Nov, seed 40)

Only 25% of CAVs end on a route other than the shortest. They produce 83% of the gain; five pairs produce 71%.
CAVs that did not move still gain 17% of the total from the others moving. Humans gain about as much in total as
the unmoved CAVs.

## F6. Pooled methods lose about 1% because they do not individualise (16 Nov, seed 40)

`hedge_group` against the reference, per CAV: 82% of its loss is in pairs with more than 10 CAVs. In those pairs
the reference puts 22% of CAVs on a route other than the pair's most common one, and in 29% of pairs of 8+ early
and late departures prefer different routes. A method that sets shares per pair cannot express that.

## F7. More routes help CAVs more than any algorithm change so far (16 Nov, seed 40)

Reference with 12 routes per pair instead of 4: `t_CAV` 4.211 → 4.106 (−2.5%). Upstream saw the same on another
network (4.012 → 3.975 → 3.893 for 4, 12, 20 routes, one run each). Side effects with sampling humans: humans slow
down before any CAV appears (4.51 → 4.68), the whole system is slower in absolute terms (4.384 → 4.433), and
learning costs more (2.64 → 3.25). Which of the 12 routes are used was not checked.

## F8. Standings by arena (seed 40; negative = slower than the reference)

| Method | 4 routes, 40% | 12 routes, 40% | 4 routes, 60% | Cost of learning, 4 routes |
| --- | ---: | ---: | ---: | ---: |
| `ref_tabular_iql` | 4.211 | 4.106 | 4.238 | 2.64 |
| `marginal_cost_q` | +0.08% | −0.92% | −0.09% | 1.95 |
| `regret_matching` | −0.11% | running | — | 1.39 |
| `msa_switch` | −0.38% | running | — | 1.41 |
| `fleet_local_search` | −0.57% | — | −1.07% | 1.80 |
| `hedge_group` | −0.81% | −0.94% | −0.89% | 1.44 |
| `share_controller` | −0.84% | −2.03% | −1.44% | 1.38 |
| `ref_aon` | −3.19% | −5.26% | −4.64% | 1.16 |

Nothing beats the reference on `t_CAV` by a margin that would survive other seeds. Several methods match it within
0.4% at about half the cost of learning. Reference `t_CAV` on seeds 40–43 with 4 routes: 4.211, 4.338, 4.360, 4.332.

## F9. Fleet-level objectives did not help

Local search on the pair's mean time and an estimated marginal-cost signal both end at or slightly below the
reference, at 40% and at 60% CAVs. Consistent with F4. The marginal-cost idea already exists upstream as a task option.

## F10. A CAV's travel time is a function of its own route, not of what the fleet does (measured, 17 November)

Scope: seed 40, `ingolstadt_custom2`, arenas with 4 routes, 12 routes, and 60% CAVs; 11, 10 and 5 methods.
Script `lab/diag/static_check.py` on packed trip logs (`lab/diag/extract_trips.py`, every fifth day).

- **Method.** Build a table (CAV, route) → mean travel time from the runs of all methods except one. Predict the
  left-out method's `t_CAV` from the table and the routes its CAVs ended on. If times depended on the joint
  arrangement of the fleet, a table measured under other arrangements would not predict it.
- **Result, 4 routes.** Prediction error at most 0.36%, typically 0.1–0.2%; correlation of predicted and actual
  across methods 0.90. The mean time of one (CAV, route) cell differs across methods by 0.014 min (0.4%); the
  day-to-day noise of the same cell inside one run is 0.093 min.
- **Ceiling.** Every CAV on its table-best route gives 4.196 min against the reference's 4.211: 0.37% of room
  (0.35% with 12 routes, 0.03% at 60% CAVs). The table-best is picked on noisy means, so this is an upper bound
  on the room.
- **Why methods rank as they do.** The share of CAVs ending on their table-best route orders the methods: 88%
  for the reference, 76–82% for the pair-level methods. More than half of the CAVs off their best route sit on a
  route within 0.1 min of it.
- **Agreement.** All methods put the same CAV on the same route for only 53% of CAVs (40% with 12 routes): the
  routes differ but the times do not, because many CAVs have near-tied routes (a quarter have a gap under 0.08 min).
- **Not shown.** The table is measured near the arrangements these methods reach. It does not rule out a distant
  joint arrangement with different times, nor say anything about other networks, seeds, or adapting humans.
- **Direct check (run `static_oracle__screen_s40`).** Every CAV fixed on its table-best route, no learning:
  `t_CAV` 4.1939 against the predicted 4.1957 and the reference's 4.2114 (0.42% better). The prediction held to
  0.04%. Confound: the assignment was built from logs of the same seed, test days included, so this is a check of
  the table, not a method. Two further limits: the assignment coincides with the reference's final routes for
  88% of CAVs, so the check is local and says nothing about distant arrangements; and the run has 10 training
  days, so its test days are 311–410, not the 901–1000 of the other runs (humans are frozen, but the day-level
  random draws differ). Remaining humans: 4.4996, unchanged.

## F11. CAVs do not slow humans in this setting; with 12 routes humans slow themselves (measured, 18 November)

Scope: seed 40, reference runs with 4 and 12 routes. Same individuals compared before and after CAVs appear
(days 251–300 against test days), which the table columns do not do: `t_pre` mixes future CAVs and future humans.

| Routes | Remaining humans, before | Remaining humans, test | Future CAVs, before | CAVs, test |
| --- | --- | --- | --- | --- |
| 4 | 4.508 | 4.499 | 4.447 | 4.211 |
| 12 | 4.677 | 4.651 | 4.593 | 4.106 |

- The remaining humans get slightly faster once CAVs learn (0.2% and 0.6%), under every method tried
  (range 4.489–4.507 with 4 routes).
- With 12 routes humans are 3.7% slower before any CAV exists: the stochastic choice rule spreads them over
  more and worse routes. The larger `CAV_advantage` with 12 routes comes from this, not from CAVs harming humans.
- Consequence: a penalty on CAVs for delaying humans has nothing to act on here. An earlier statement that
  CAVs slow humans by 0.1–0.5% compared different groups of people and was wrong.

## F12. The four routes of a pair are variants of one path, and demand is thin (measured, 18 November)

Scope: seed 40, `ingolstadt_custom2`, routes generated by JanuX with `number_of_paths` 4, `num_samples` 10, beta −5.

- 1035 vehicles depart over 30 minutes between 306 origin–destination pairs; the median pair has one vehicle.
  152 pairs contain CAVs; 46% of CAVs are in pairs of ten or more.
- Two routes of the same pair share 75% of their road segments (median; quartiles 60–87%). The second-shortest
  route is 13% longer than the shortest in free-flow time.
- Realised travel time is 1.9 times the free-flow time of the chosen route, for humans and CAVs alike. Most of
  the time is therefore not free driving; whether it is signals or queues is not separated yet. This is a mean
  of per-trip ratios against the route actually driven; F14's "1.6 min against 4.2–4.5 min" (a factor of about
  2.6) divides the mean realised time by the median shortest-path time over pairs, which weights the many
  one-vehicle short pairs equally. The two figures use different denominators and are not in conflict, but
  neither was re-derived after the review.
- Reading (inferred): this explains F4 and F10. Moving a vehicle between two routes of its pair changes the load
  only on the quarter of the path where they differ; the shared three quarters carry the pair's whole flow
  whatever is chosen. The choice set offers no way to relieve a shared bottleneck, so choices barely interact.
- Consequence for design: a route set with routes that genuinely avoid each other (low overlap) is the setting
  where coordination and human-impact terms could start to matter. Overlap should be reported with any route-set
  result.

## F13. The metrics table already carries fairness columns (read in the output, 18 November)

`BenchmarkMetrics.csv` contains, besides the leaderboard columns: `t_HDV_pre` (the remaining humans before CAVs,
so `Effect_of_remaining = t_HDV_pre / t_HDV_test` compares the same people), the spread and Gini coefficient of
travel times before and at test with their ratios, the longest trip before and at test (`rawlsian_fairness_ratio`),
total system travel time (`utilitarian_fairness_ratio`), mean speed and mileage. For the `static_oracle` run:
Gini 0.1886 to 0.1908, longest trip 10.54 to 10.64 min, total time down 2.4%. Earlier notes saying URB lacks
same-people and inequality measures were wrong; what is missing is per-street load and the share of people made worse off.

## Corrections after an independent review (18 November)

A separate reviewer re-derived the numbers from the trip logs and read the code. The two points marked
"checked" were re-verified in the code afterwards; the rest are the reviewer's results and are not re-run here.

- **`cost_of_learning` was misread (checked, `analysis/metrics.py`).** It is the mean over vehicles of
  (slowest training day − fastest training day), a spread, not time lost. Every statement above and in
  `idea_map.md` about "half the cost of learning" rests on the wrong reading. Mean CAV travel time over training
  days 301–900 (reviewer's numbers): before CAVs 4.447; reference 4.500; regret matching 4.224; MSA 4.236;
  annealed 4.244; Hedge 4.249. With 12 routes: before 4.593; reference 4.689; regret 4.149; MSA 4.178;
  annealed 4.201. So during training the reference is slower than the human baseline and the candidates are
  about 6% faster than the reference (12% with 12 routes). Lesson 8 in `idea_map.md` (numbered 9 before the renumbering) is wrong: the advantage
  grows with more routes.
- **The reference barely stops exploring (checked).** `eps_decay` 0.99963 is applied once per day, so epsilon
  goes from 0.5 to 0.40 over 600 days, not to 0.05 (that needs about 6000 days). In days 801–900 its CAVs drive a
  route other than their final one on 37% of days. Test days are greedy, so test `t_CAV` is affected only indirectly (through what was learned by day 900), but
  "nothing beats the reference" was measured against a reference with an exploration schedule made for a tenfold
  longer run.
- **Humans draw identical choices in every run of a seed** (100% agreement day by day). "Under every method"
  is therefore not a set of independent repetitions.
- **F10, narrower wording.** Near the arrangements reached, time is mostly set by the own route; arrangement
  effects of about 0.2% exist, the same size as the differences between methods. 10% of shared (CAV, route) cells
  differ by 0.32 min or more between methods. On a held-out half of the data the room above the reference is
  0.35% with 4 routes, about 0.1% with 12, none at 60% CAVs. The `static_oracle` assignment coincides with the
  reference's final routes for 88% of CAVs, so that check is local. Only a distant assignment with a prediction
  written beforehand can refute F10.
- **F6, partly wrong.** The table leaves 45% of Hedge's loss unexplained; its CAVs are slower on the same
  (CAV, route) cells by 0.009 min. Part of the loss comes from the whole pair gathering on one route, which is
  an interaction effect.
- **F12, conclusion not supported.** The 75% overlap contradicts 55% stated in `system.md` for the same seed, and
  "therefore vehicles do not interact" is contradicted by the shifts above.
- **F3, narrower wording.** The `trip_info_eta` observation is nearly empty here (a constant for the 119 CAVs
  alone in their pair and for first departures); this does not show that same-day information is useless.
- **F11.** The human change with 4 routes is −0.009 ± 0.013 min, not different from zero. A zero total does not
  mean each vehicle's effect is zero.
- **Lesson 1 is wrong as worded:** methods end up to 0.84% (4 routes) and 2.03% (12 routes) from the reference,
  not within 0.3%.
- **Candidates.** `minority_game` has no reward for the less crowded option, so it is not a minority game; its
  drop with 12 routes is probably an artefact of random strategy tables. `pheromone` loses at test because each
  CAV is frozen on a randomly drawn route. No candidate's hyperparameters were tuned; `marginal_cost_q` counts
  only CAVs of the same pair on the same route and keeps the reference's epsilon, a weak test of the idea.
- **Cheapest next checks:** the reference with epsilon decaying to 0.05 by day 450; a distant oracle with a
  prediction written first; a second algorithm seed on environment seed 40 for five methods.

## F14. The route generator is not the cause of similar routes (measured, 18 November)

Scope: seed 40, `ingolstadt_custom2`, all 306 pairs; script `lab/diag/route_alternatives.py` on the road graph
built by JanuX (850 road segments as nodes, 1426 connections, free-flow times).

- **How JanuX builds routes (read in code).** A random walk from the origin: at each junction the next segment is
  drawn with probability proportional to exp(beta × remaining free-flow time to the destination), beta −5. It
  repeats until 10 walks and 4 distinct routes exist, then draws 4 distinct routes weighted by how often each was
  sampled. Routes depend on the seed. Nothing in it looks at overlap between routes or at congestion.
- The generator's best route equals the true shortest path for most pairs (median ratio 1.00, upper quartile 1.06).
- Overlap between two of its routes, weighted by time: median 61% (quartiles 48–74%). The earlier 75% counted
  segments relative to the shorter route, and the 55% in `system.md` used another definition; 61% time-weighted
  is the figure to use. In 64% of pairs the generator already offers a route sharing under half of the shortest one.
- A route forced away from the shortest (its segments made three times slower) shares 19% with it but is 28%
  longer in free-flow time for the median pair. Only 35% of pairs (30% of CAVs) have such an alternative within
  +25%.
- Free-flow shortest time is 1.6 min (median) against realised trips of 4.2–4.5 min.
- Reading: the limit is the network and the demand, not the generator's settings. Dissimilar routes mostly cost
  more than the 13% gap to the second route, so they would rarely be chosen. F12's causal reading is withdrawn.

## F15. Away from the usual arrangement CAVs do load each other (measured, reviewed, 19 November)

Scope: environment seed 40, demand ×1, 4 routes, run `static_distant__screen_s40`: every CAV fixed on its
second-best route by the F10 table, 10 training days, test days 311–410.

- Prediction written before the run: `t_CAV` 4.6769 (4.685 if the route is picked on one half of the data and
  scored on the other). Measured 4.8113; 4.802 without the 4 removed vehicles. Error 2.9% against a tolerance of 0.3%.
- The short training window is not the reason: `static_oracle` was tested on the same days with the same human
  choices and met its own prediction.
- The gap grows with the number of fleet CAVs on the same pair and route: 0.05 min for one, 0.10 for 2–5,
  0.18 for 6–15, 0.26 for 16 or more. 10% of the CAVs carry 76% of it.
- Humans are 0.072 ± 0.018 min (1.6%) slower on the same days.
- Consequence: F10 ("time is set by the own route") is a local statement about arrangements near those the
  learners reach. It is not a property of the network.

## F16. Noise from the algorithm seed (measured, reviewed, 19 November)

Scope: environment seed 40, demand ×1, algorithm seeds 40 and 1040.

| Method | Δ vs reference, seed 40 | seed 1040 |
| --- | --- | --- |
| reference (`tabular_q_port`) | 0.00% | +0.02% |
| `surrogate_fill` | +0.11% | +0.21% |
| `annealed_revision` | +0.09% | −0.14% |
| `regret_matching` | −0.11% | −0.39% |
| `hedge_group` | −0.81% | −0.59% |

A second algorithm seed moves a method's gap by up to 0.3 points; four differences only, so the true noise may
be 0.1–0.5 points. A difference under about 0.4% is not a ranking. Hedge's deficit is stable; the others and
`tabular_q_decay` (+0.11%; −0.40% with 12 routes) tie the reference. So the reference's slow epsilon decay did
not hurt its test result. `pheromone_v2` −0.40% (was −0.84%); `minority_game_v2`, a real minority game, −5.71%.

## F17. Demand ×2: methods separate, but only same-day comparisons are valid (measured, reviewed, 19 November)

Scope: arena `d2` (network `ingolstadt_custom2_d2`, 2070 vehicles), environment seed 40, one algorithm seed,
trip logs every fifth day. CAV time minus the reference's on the same test days 901–1000:

| Method | Difference, min | Reading |
| --- | --- | --- |
| `tabular_q_decay` | +0.006 ± 0.024 | ties |
| `hedge_group` | +0.053 ± 0.119 | not distinguishable; deficit sits in a few bad days |
| `aon_fixed` | +0.226 ± 0.041 | real (about 4%) |
| `annealed_revision` | +0.331 ± 0.050 | real, worse than all-or-nothing; cause unknown |

- Reference `t_CAV` 5.694. Humans under all-or-nothing are 0.112 ± 0.040 min slower than under the reference.
- `annealed_revision` settles (2% route changes at the end) on a poor assignment. Possibly its estimates are
  damaged by the 29.97-min records of removed vehicles; it has the most removals during training. Not shown.
- Added delay from one more CAV of the same pair on the same route: 0.001–0.003 min at ×1, 0.008–0.024 min at
  ×2 depending on the run. Not a constant of the network; error bars ignore within-day dependence.
- Realised time over free-flow time (median): 1.92–1.96 at ×1, 2.39–2.44 at ×2, 4.18 at ×3.
- Removed vehicles at ×2: 2.0 per day before CAVs, 0 at test for both tabular learners, 0.3 for the others,
  1.05 for `ref_aon`. They add at most 0.01 min to means but mark jam days.
- The human phase at ×2 does not show a trend but 25-day blocks swing between 5.9 and 6.5 min. Before/after
  comparisons (`Effect_of_change`, `t_pre`) are not usable at ×2; the human baseline to use is humans under
  `aon_fixed` on the same days.
- Algorithm-seed noise at ×2 is not measured.

## Corrections after the third review (19 November)

- **Test-day window.** `ref_aon` tests on days 501–600, every 600-day method on 901–1000. At ×2 the same
  unchanged all-or-nothing gives 5.92 to 6.23 min depending on the 100-day block; the 5% gap between `ref_aon`
  and `aon_fixed` is entirely this. At ×1 their gap is 0.42%, probably the same effect.
- **F10 direct check.** `static_oracle`'s "+0.42% over the reference" compares days 311–410 with days 901–1000
  and is therefore not established. Its agreement with its own prediction stands. A rerun with 600 training
  days is submitted.
- **All "Δ vs `ref_aon`" columns** in the leaderboards compare different day windows; use `aon_fixed`.
