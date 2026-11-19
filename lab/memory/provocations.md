# Provocations for the hypothesis generator

Written 17 November 2026 by the provocateur role. **Nothing here is a result or a recommendation.** Each item is a
candidate imported from another field, with the cheapest test that would kill it. The hypothesis generator decides
what, if anything, enters `hypotheses.md`; the critic reviews it there, not here.

Read against `system.md`, `findings.md` (including its corrections section, which overrides earlier wording),
`idea_map.md`, `literature.md`, `open_questions.md`, `hypotheses.md` (R1–R9), and against `RouteRL/routerl/environment/observations.py`.

**References.** Bibliographic data (authors, year, venue, DOI) of every reference below was checked against Crossref on
17 November 2026. The one-sentence summaries of what each paper shows are from the papers as I know them, not re-read.

**Feasibility numbers (my own checks, seed 40, packed logs, not results).** Used only to show a test is possible:

- Logged days are identical across method logs (days 5, 10, …, 1000).
- `tabular_q_port` vs `regret_matching`, remaining humans, same day number: identical route choice on 100% of
  human-trips in every phase. Same-day travel-time difference at identical route choice: exactly 0 in the human phase;
  on test days median 0.017 min, 90th percentile 0.150 min, 23% of human-trips differ by more than 0.05 min
  (training days: 0.283 and 30%).
- Of the 414 CAVs, 299 have at least one remaining human in their origin–destination pair, 279 at least three, 222 at
  least ten.
- The `trip_info_eta` observation includes **humans** of the same pair (no filter on kind in `agent_observations`), and
  its reset value carries each route's free-flow time.
- Reference algorithm config: learning rate 0.2, epsilon 0.5 → 0.40 over 600 days.

---

## P1. Eleven parallel worlds: measure interaction from the runs you already have

*Field: causal inference under interference.*

- **Source.** When one unit's treatment changes another's outcome, the usual "no interference" assumption fails, and
  effects must be defined over the assignment of the whole group; Hudgens and Halloran split them into direct and
  spillover effects estimable from designed group assignments. The enabling condition is that the counterfactual worlds
  differ only in the assignment. Hudgens & Halloran (2008), *Toward causal inference with interference*, JASA 103:832–842,
  https://doi.org/10.1198/016214508000000292.
- **Mapping.** The simulator is deterministic and humans draw identical routes on the same day number in every run of a
  seed (findings, corrections). So for a remaining human *h* on day *d*, the logs of the 11 four-route methods are 11
  worlds where *h*'s own choice and every other human's choice are identical and only the CAV arrangement differs. The
  difference in *h*'s travel time between two worlds is an exact, noise-free spillover of the arrangement difference
  onto *h* (feasibility: 23% of human test trips differ by more than 0.05 min between two worlds). Regress, across
  worlds and days, *h*'s time on the counts of CAVs per (pair, route) in that world on that day. The coefficients form a
  pair-to-pair interaction matrix without any road geometry. The same works for CAVs that sit on the same route in two
  worlds.
- **Why it might matter.** It answers the open question "how much do routes of different pairs interact?" and R7's
  missing link-level data at zero runs. It also turns R3 (distant oracle, 1 run) into a check of a prediction made from
  the matrix rather than from a (CAV, route) table. **Why it might not.** F4/F11: per-vehicle effects average to about
  zero; the matrix may be a few large entries in noise from the every-fifth-day sampling (200 logged days).
- **Cheapest test.** No run. On `lab/diag/trips/*` (4 routes, 11 methods, test and training days separately): fraction
  of variance of human same-day, same-route travel time across worlds explained by the CAV count regressors, with a
  held-out set of days.
- **Kill.** Out-of-sample R² of the arrangement model below 0.10 on held-out days, *or* fewer than 5 (pair, route) →
  (pair, route) entries significant after a Bonferroni correction. Then cross-pair interaction at ×1 is not
  structured enough to model, and P4 goes with it.
- **Wildness: adjacent.** Ignoring it means paying runs (R3, R4) for an interaction measurement that the existing logs
  already contain in exact counterfactual form.

## P2. Humans are free explorers: learn from them instead of exploring

*Field: behavioural ecology, social learning.*

- **Source.** In producer–scrounger games some individuals pay to search and others exploit what they find; the
  equilibrium share of scroungers is set by how much information producers leak (Barnard & Sibly 1981, *Producers and
  scroungers*, Animal Behaviour 29:543–550, https://doi.org/10.1016/S0003-3472(81)80117-0). In a tournament of
  social-learning strategies the winners copied almost exclusively, because the demonstrators had already filtered
  behaviour by its payoff (Rendell et al. 2010, Science 328:208–213, https://doi.org/10.1126/science.1184719).
- **Mapping.** Producers = remaining humans of the CAV's pair, who redraw a route every day by `exp(beta × cost)`
  (61% switch between test days): they sample all four routes for free, every day, and their choice frequencies are
  weighted by their own Gawron estimates. Scrounger = the CAV. What a CAV can legally see: the `trip_info_eta` entries
  of its pair (humans included) from vehicles that departed no later than it and have already arrived. Two signals:
  (a) per-route mean time of same-pair humans; (b) the humans' modal route (a filtered choice, as in the tournament).
- **Why it might matter.** The reference's training excess is its own exploration (4.127 vs 5.008 min on and off its
  final route). A CAV that never explores and still lands on its table-best route would cut training time to the
  pre-CAV level or below without losing test time: criterion (ii) with a structural reason (the human rule is an
  exploration engine paid by humans anyway). **Why it might not.** F6: in 29% of large pairs early and late departures
  prefer different routes, so humans at other departure times mislead; 115 CAVs have no same-pair human at all; the
  observation is biased low by about 1.1 min (F3); `regret_matching` and `msa_switch` already get most of the training
  gain from shared CAV estimates (training 4.224 and 4.236).
- **Cheapest test.** No run. For each CAV with ≥3 same-pair humans: route ranking from (a) all same-pair human trips
  in days 251–300 (privileged upper bound), (b) only trips the observation could have shown it during training days
  (departed no later, arrived before its departure). Compare the top route with the CAV's table-best route (split-half
  table, as in the corrections) and with the reference's final route.
- **Kill.** Variant (b) picks the table-best route for fewer CAVs than the shortest route does (all-or-nothing's
  agreement), *or* variant (a) agrees with the table-best less often than the reference's final routes (88%).
- **Wildness: adjacent.** Ignoring it means treating the noisy human population only as background, when in this
  benchmark it is the only agent that explores at no cost to the fleet.

## P3. Read the distance to saturation from today's fluctuations

*Field: queueing theory (heavy traffic) and critical transitions.*

- **Source.** As a queue's utilisation ρ approaches 1, waiting time grows like 1/(1−ρ) and its distribution becomes
  approximately exponential, so its spread grows at the same rate as its mean (Kingman 1961, *The single server queue
  in heavy traffic*, Proc. Cambridge Phil. Soc. 57:902–904, https://doi.org/10.1017/S0305004100036094). Systems near
  a tipping point show rising variance and autocorrelation before the transition (Scheffer et al. 2009, *Early-warning
  signals for critical transitions*, Nature 461:53–59, https://doi.org/10.1038/nature08227).
- **Mapping.** Cell = (pair, route). At ×1, per cell: the within-cell, day-to-day standard deviation of trip time after
  removing a day fixed effect, its skewness (signal waiting is bounded by the red phase, queueing is right-skewed), and
  the within-day lag-1 correlation of excess times of successive same-cell trips ordered by `start_time` (queue
  persistence). The prediction is about ×2: cells ranked by this ×1 index slow down most from ×1 to ×2, and the ×1 and
  ×2 removal events (R1) fall in the top decile.
- **Why it might matter.** R4 asks *whether* arrangement starts to matter at ×2 but not *where*. A ranked list written
  before the ×2 logs exist is a pre-registered, structural prediction (criterion (i)) and tells R7 which links to
  model. **Why it might not.** F12: trips are 1.9 × free-flow at ×1, and if that excess is fixed-cycle signal delay,
  the ×1 spread is signal-phase noise unrelated to ρ; F10: own-route dominance may mean no cell is near the knee at ×1.
- **Cheapest test.** Now: compute the index from ×1 logs (humans, days 251–300 and AON test days) and write the ranked
  top 30 cells into the ledger. Then with the ×2 base logs (no extra run): Spearman correlation between the ×1 index
  and the ×2/×1 mean-time ratio per cell.
- **Kill.** Spearman below 0.2, *or* the ×1 index is no better a predictor than the cell's ×1 mean time alone (then
  the fluctuations carry nothing the mean does not).
- **Wildness: stretch.** Ignoring it means learning from ×2 that interaction appeared without a way to say in advance,
  on another network, where it will.

## P4. Superspreader routes: put the social term only where the externality is

*Field: epidemiology (individual variation in transmission).*

- **Source.** Individual reproductive numbers are strongly overdispersed: a small fraction of cases cause most
  transmission, so control targeted at the most infectious individuals beats population-wide control (Lloyd-Smith et al.
  2005, *Superspreading and the effect of individual variation on disease emergence*, Nature 438:355–359,
  https://doi.org/10.1038/nature04153).
- **Mapping.** "Infectiousness" of a (pair, route) cell = the summed delay one extra vehicle on it imposes on other
  vehicles, taken from P1's interaction matrix (or from the corrections' fixed-effects externality: median 0.017 min,
  90th percentile 0.067). Fit a dispersion parameter to the distribution over cells. "Targeted control" = a learner
  whose reward adds a marginal-cost term only for CAVs whose candidate route is a top cell; everyone else stays a plain
  selfish learner.
- **Why it might matter.** R7 costs days of code because it wants slopes on every road segment. If a handful of cells
  carry most of the externality, R7 shrinks to a short list read from the logs, and a "socially aware on few routes"
  learner can tie the reference on `t_CAV` (most CAVs untouched) while being a clean test of criterion (ii) at ×2.
  **Why it might not.** F11: at ×1 humans are not measurably slowed in total; `marginal_cost_q` gained nothing (F9),
  and the group's own social reward gained about 0.4% (`literature.md`). Overdispersion of something near zero is still
  near zero.
- **Cheapest test.** No run, after P1: share of total externality carried by the top 10% of cells, at ×1 now and on
  the ×2 base logs later.
- **Kill.** At ×2 the top 10% of cells carry less than 40% of the externality, *or* the total externality at ×2 is
  below 0.5% of `t_test` (then nothing worth targeting).
- **Wildness: stretch.** Ignoring it keeps R7 as an all-links model whose cost delays it behind every other hypothesis.

## P5. The hot stove: removal events burn routes for learners that stop exploring

*Field: organisational learning and the psychology of decisions from experience.*

- **Source.** An adaptive learner that samples options by their current estimate stops sampling an option after a bad
  draw, so its estimate is never corrected: learning itself produces avoidance of options with occasional bad outcomes
  (Denrell & March 2001, *Adaptation as information restriction: the hot stove effect*, Organization Science 12:523–538,
  https://doi.org/10.1287/orsc.12.5.523.10092). People choosing from experience underweight rare events they have
  not sampled and overreact to recent ones (Hertwig et al. 2004, Psychological Science 15:534–539,
  https://doi.org/10.1111/j.0956-7976.2004.00715.x).
- **Mapping.** Bad draw = a removal event: a ≈ 29.97-min trip where the route normally takes about 4. With learning
  rate 0.2, a reference CAV with Q ≈ −4.1 on its best route falls to about −9.3 after one event; to come back within
  the median best-to-second gap (0.30 min) it needs about 13 more visits (0.8^k × 5.2 < 0.3). Arithmetic only: at the
  reference's epsilon ≈ 0.4 (≈ 0.1 visits per day to a non-greedy route) that is about 130 days; at epsilon 0.05 it is
  about 1000 days, longer than training. The fast-decay reference would keep a burned route avoided into test; for
  `regret_matching`, `msa_switch` and `annealed_revision` it depends on their estimators (a 1/n average dilutes one
  event; a constant step does not), which should be read in their cards before the test. Humans hit in days ≤ 300 carry the burn for ever
  (Gawron estimate with alpha 0.2, frozen after day 300).
- **Why it might matter.** It predicts a ranking reversal at ×3 against R2's direction: the reference's "wasteful"
  exploration would be what repairs burns, so the fast-decay reference and the cheap-learning candidates fall behind
  it. That is a structural explanation of a ranking (criterion (i)), and a warning that R2's fix may not keep its edge.
  **Why it might not.** At ×1 there are only 5 events (21 trips), all in training; R1 may find fewer than 0.1 events
  per test day at ×3; a removal on a route may also be a correct signal that the route is gridlock-prone, so avoiding
  it is right, not a burn.
- **Cheapest test.** No extra run, on the ×2/×3 base logs: CAVs hit by a removal on route *r* in training; share of
  later training days on *r* against their own pre-event share; share of them whose test route differs from their
  table-best route (table built from non-event days), by method. Distinguish burn from correct avoidance: is *r*'s
  non-event mean time still the CAV's best?
- **Kill.** Fewer than 2% of CAVs are hit by a removal at ×3, *or* hit CAVs return to *r* at their pre-event rate in
  every method, *or* their *r* is no longer their best route on non-event days (avoidance is correct).
- **Wildness: stretch.** Ignoring it risks recommending (R2) the very schedule that loses once events are common.

## P6. Invasion fitness: run two methods in one fleet

*Field: evolutionary ecology (adaptive dynamics) and crossover experimental design.*

- **Source.** In a resident population at its own attractor, a rare mutant's fitness is its long-run growth rate in
  the environment the residents create; a strategy that no mutant can invade is evolutionarily stable (Metz, Nisbet &
  Geritz 1992, *How should we define 'fitness' for general ecological scenarios?*, Trends Ecol. Evol. 7:198–202,
  https://doi.org/10.1016/0169-5347(92)90073-K).
- **Mapping.** A lab wrapper candidate assigns the 414 CAVs to two methods by a fixed hash of id, stratified by pair
  size; run 1: A on arm 1, B on arm 2; run 2: swapped. Per CAV, the difference between its test time under A and
  under B, with humans' draws identical (common random numbers) and the rest of the fleet half-and-half in both runs.
  "Invasion": B on 10% of CAVs inside an A fleet, and the reverse.
- **Why it might matter.** The noise floor (rank 4, 4 runs) is about the variance of between-run comparisons. A
  crossover in which every CAV is its own control removes run-level shocks that hit both arms on the same day, which
  is exactly what removal events are at ×3 (R1). It also measures a setting the benchmark cannot express now (mixed
  fleets from different makers) and asks whether the reference is invadable at ×2. **Why it might not.** At ×1
  between-run noise comes mostly from each CAV's own exploration draws (F4, F10), which a crossover does not remove;
  then it costs a wrapper and 2 runs for the same precision as 2 seeds.
- **Cheapest test.** A wrapper (one file in `lab/candidates/`) and 2 runs at ×1 with A = reference, B = `regret_matching`.
- **Kill.** The crossover estimate of A − B has a standard error not at least 1.5 times smaller than the between-run
  difference estimated from a second algorithm seed (the noise-floor runs), *and* the B-arm CAVs' times do not differ
  between "next to A" and "next to B" by more than that standard error.
- **Wildness: long shot.** Ignoring it leaves the benchmark unable to say whether a method keeps its edge when other
  fleets on the road use other methods.

## P7. Network tomography: infer road-segment times from trip times

*Field: telecommunications (Internet measurement).*

- **Source.** Internal link delays of a network that cannot be instrumented are inferred from end-to-end measurements
  on paths that overlap, by inverting the path-link incidence matrix, with identifiability set by its rank (Coates,
  Hero, Nowak & Yu 2002, *Internet tomography*, IEEE Signal Processing Magazine 19(3):47–65,
  https://doi.org/10.1109/79.998081).
- **Mapping.** Paths = the 4 routes of each of 306 pairs (`routes.csv` from JanuX, seed 40); links = road segments
  (850 nodes of the JanuX graph) or turns, since the 1.9 × free-flow excess may sit at junctions; measurements = mean
  trip time per (pair, route) from all vehicles (humans in days 251–300 cover every route). Solve nonnegative least
  squares for per-segment times plus a per-pair offset, and predict held-out (pair, route) cells.
- **Why it might matter.** It gives the 119 CAVs alone in their pair (and the 115 with no same-pair human) a route
  ranking learned from other pairs' trips, with no exploration; it is also the cheap form of R7's link model (no SUMO
  edge-data output needed). **Why it might not.** F14: the shortest route is the generator's best for most pairs and
  alternatives mostly cost more, so a ranking that mostly returns the shortest route adds little over all-or-nothing;
  F6: time-of-day differences inside a pair are not in a static segment model; 61% average overlap may leave the
  system rank-deficient exactly on the segments that distinguish a pair's routes.
- **Cheapest test.** No run, but needs `routes.csv` of seed 40 from the cluster (it is not in this checkout; the critic
  hit the same gap). Leave-one-pair-out prediction of each held-out pair's route ranking; report the rank of the
  incidence matrix restricted to non-shared segments.
- **Kill.** Median absolute prediction error of held-out cells above 0.30 min (the median best-to-second gap, F2), *or*
  held-out best-route agreement with the table-best no higher than the shortest route's.
- **Wildness: stretch.** Ignoring it leaves lonely CAVs with exploration as their only source of information, and R7
  with its most expensive data path.

---

## Rejected on the way

| Idea (field) | Why dropped |
| --- | --- |
| Clonal selection and affinity maturation of a route repertoire (immunology) | Only a metaphor for route-set generation, already in `idea_map.md`; F14 says the network, not the generator, limits it |
| Response-threshold task allocation (swarm robotics) | Heterogeneous switching thresholds are annealed log-linear revision with per-CAV temperatures; tried |
| Optimal execution of a large order over time (market microstructure) | Splitting a large pair by departure time is `surrogate_fill`'s fill by departure order; tried |
| Locational marginal prices (power grids) | Marginal-cost signal under another name; `marginal_cost_q` and R7 |
| N-1 contingency and cascade analysis (power grids) | Removal events as cascades are R1; nothing measurable beyond it with trip-level logs |
| The fleet as balancing reserve for human fluctuations (power grids, demand response) | Needs today's human draws before choosing; F3 says the day's observation is nearly empty |
| Backpressure routing, random early detection (telecom) | Need real-time queue state (F3); RED's early probabilistic shedding is share control |
| Coupled multipath congestion control (telecom) | A pair splitting load across paths is `share_controller` and `hedge_group` |
| Fluctuation scaling, internal vs external drive (statistical physics) | Daily demand is fixed here, so the external term is trivial in count form; in time form it reduces to the day fixed effect used in P1 and P3 |
| Bet-hedging for geometric-mean fitness (ecology) | The benchmark scores arithmetic means; no payoff for variance reduction |
| Optimizer's curse (decision analysis) | The split-half table in the corrections already handles it |
| Knowledge gradient, best-arm identification (Bayesian optimisation) | A bandit rule; ten tied; room above the reference is 0.37% |
| Producer–scrounger among CAVs only (ecology) | Shared CAV estimates already in `regret_matching` and `msa_switch`; kept only the human version (P2) |
| Quorum sensing for collective commitment (swarm biology) | A pair-level decision; F6 says pair-level methods lose by not individualising |
| Bullwhip effect (supply chains) | Day-to-day oscillation with adapting humans is already R8 |
| Social influence destroys crowd wisdom (sociology) | Herding of a pair onto one route is the Hedge loss already found in the corrections |
| Top trading cycles, route swaps (mechanism design) | Nothing to trade when a CAV's time is set by its own route (F10) |
| Channel capacity of the observation (information theory) | Metaphor; F3 and R9 already measure the observation's content directly |
| Conformity norms, human noise as a dial (sociology) | F1 already compares sampling and deterministic humans |
| Reaction norms across pairs (evolutionary biology) | Function approximation over observation features; the neural learners already have them and tie |
| Postponement, decide when information arrives (supply chains) | That is the same-day observation; R9 |

---

## Three questions to the hypothesis generator

1. **R2 treats exploration as pure cost.** If removal events become common at ×2–×3 (R1), exploration is also what
   repairs an estimate after a 30-minute trip (P5: about 130 days at epsilon 0.4, about 1000 at 0.05). What result
   would make you rank the fast-decay reference *below* the slow one under congestion, and does R2's refutation rule
   allow that outcome to be seen?
2. **Why does measuring interaction need new runs?** R3 and R4 spend a run each on oracles, and R7 assumes link data do
   not exist. The 11 existing four-route runs are exact counterfactuals of each other for every human (identical draws,
   deterministic simulator; 23% of human test trips differ by more than 0.05 min between two of them). Should P1 run
   before R3, and would a positive P1 make R3 a check of a prediction rather than a discovery?
3. **Every hypothesis assumes a CAV learns only from its own trips or other CAVs'.** 279 of 414 CAVs have at least three
   same-pair humans who sample all four routes every day and whose trips are already in the observation. If P2's
   variant (b) passes, R2's "who pays for a fleet's learning" changes answer: nobody needs to. Why is the ranking built
   on a learner that explores at all?
