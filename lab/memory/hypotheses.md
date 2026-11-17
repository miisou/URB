# Hypotheses for the congested setting (demand ×2 and ×3 on `ingolstadt_custom2`)

Written 17 November 2026 by the hypothesis-generating session. Nothing here is measured; every entry is a
prediction with the number that would refute it. Built on `findings.md` **as corrected by the independent review**
(its "Corrections" section overrides earlier wording), `system.md`, `idea_map.md`, `literature.md`, and on code read
in `RouteRL/routerl/environment/{simulator,environment}.py` (`routerl-nightly`).

## What is already known and constrains these hypotheses

- At ×1 a CAV's time is mostly set by its own route (F10, narrowed): arrangement effects are about 0.2%, the same
  size as differences between methods. Per extra same-pair CAV on a route: 0.003 min (review's fixed-effects
  estimate; F4's 0.012 is the cruder figure).
- Realised trips are 1.9 × free-flow (F12): most time is already not free driving at ×1.
- During training the reference is *slower than the human baseline* (CAVs 4.500 vs 4.447 before CAVs) while
  shared-estimate methods are about 6% faster than the reference (12% with 12 routes). Part of this is the
  reference's epsilon, which only falls 0.5 → 0.40 in 600 days (review, checked).
- Humans are frozen after day 300 and draw identical choices on identical days in every run of a seed (common random
  numbers). Day-to-day standard error of `t_CAV` is about 0.0015 min; seed-to-seed spread is about ±2%.
- Remaining humans do not get slower at ×1 (−0.009 ± 0.013 min).
- The `trip_info_eta` observation is nearly empty at ×1, which does **not** show that same-day information is useless.
- `marginal_cost_coefficient_beta` appears in upstream task configs but no use of it was found in `routerl/`
  (grep, 17 November); `marginal_cost_q` counts only same-pair, same-route CAVs and keeps the reference's epsilon.

## A code fact that shapes every ×3 result (read in code)

RouteRL's default (`use_sumo_teleport: false`) removes a vehicle after `stuck_time` = 600 consecutive simulation
steps at speed zero and records its travel time as `simulation_timesteps / 60`. URB scripts set
`simulation_timesteps` to the latest departure time, about 1798 s, so **every removed vehicle gets ≈ 29.97 min,
whatever happened to it**. Removal also clears the jam it was part of. Consequences: (a) one teleport weighs as much
as about seven normal trips in a mean; (b) the penalty is flat, so a route that jams badly and one that jams
mildly-but-long look alike; (c) if the demand scaling widens the departure window, the penalty changes with it.
The episode itself runs until every vehicle has arrived or been removed, so jams do not truncate the day.

## Candidates considered (14) and which were kept

| # | Candidate | Kept? | Reason if dropped |
| --- | --- | --- | --- |
| A | Teleports dominate method differences at ×3 | **H1** | |
| B | Arrangement starts to matter: the F10 table stops predicting | **H2** | |
| C | Price of anarchy is non-monotone in demand (×2 > ×3) | merged into H2 | Same runs and measurement |
| D | Used routes become near-tied (Wardrop), more CAVs leave the shortest route | merged into H2 | Secondary prediction of the same mechanism |
| E | Learning-time gap between reference and shared-estimate methods grows | **H3** | |
| F | Pair-level share methods (Hedge, share controller) close their gap | **H4** | |
| G | Remaining humans get slower under a selfish fleet; inequality rises | **H5** | |
| H | A link-level marginal-cost learner improves total time | **H6** | |
| I | Same-day ETA becomes informative during training, not at test | **H7** | |
| J | With adapting humans, tracking methods separate from averaging ones | **H8** | |
| K | Departure-time pooling within a pair beats per-pair pooling | dropped | Folded into H4 as a follow-up; needs H4's result first |
| L | Route sets that differ between humans (4) and CAVs (12) | dropped for now | Needs an environment change (per-kind masks); worth it only once H2 shows interaction. Directly answers the maintainer's objection to F7-type gains, so it is first in line after these |
| M | A fleet controller that keeps CAVs off gridlocking routes | dropped | Its value is entirely conditional on H1; risks optimising an artefact |
| N | 60% CAVs at ×2 | dropped | Same mechanism as H2 with a second confound (share); do after H2 |

---

## H1. At ×3, removed ("teleported") trips decide the ranking

**Statement.** At ×3 (4 routes, 40% CAVs, seed 40), at least 1% of test-day trips are removed after 600 s standing
still, and removing those trips from the means changes the `t_CAV` difference between the reference and
all-or-nothing by at least half.

- **Mechanism.** The flat ≈29.97 min penalty (code fact above) is about seven times a normal trip; at 1% of trips it
  shifts a mean by ~0.25 min, an order of magnitude more than the ×1 differences between methods. Gridlock in SUMO
  microsimulation at junctions with conflicting turns is common when demand exceeds capacity; teleporting is the
  standard and documented workaround, and it is an artefact, not traffic.
- **Cheapest test.** No extra runs. In the ×3 runs the implementer needs anyway (reference and `ref_aon`), count
  trips with travel time within 0.05 min of `simulation_timesteps/60` per day and per kind, and recompute `t_CAV`,
  `t_HDV_test` with those trips excluded and with them replaced by the time they had stood when removed (not
  available; report "excluded" and "as recorded" as two bounds). A smoke run (25 days, ~10 min at ×1, more at ×3)
  already shows whether teleports occur at all.
- **Refuted if.** Fewer than 0.2% of test trips are removed, or the reference–AON difference changes by less than
  20% when they are excluded.
- **Worth.** A validity gate: no ×3 claim is publishable without it. For a paper it is a benchmark-pitfall finding
  ("a flat removal penalty decides congested rankings"), which is the kind of contribution the group publishes.
- **Main way to mislead.** The demand-scaling procedure itself (duplicated agents departing in the same second can
  cause insertion queues that SUMO handles differently from road jams); one seed; the counter counts consecutive
  zero-speed steps, so stop-and-go queues that never fully stop for 600 steps escape it while still being severe.

## H2. Under ×2 the fleet's arrangement starts to matter: the own-route table stops predicting

**Statement.** At ×2, the leave-one-method-out prediction of `t_CAV` from the (CAV, route) table (`lab/diag/static_check.py`)
errs by at least 1.0% for at least one method (it errs by at most 0.36% at ×1), and the fixed-effects externality
per extra same-pair CAV on a route rises at least tenfold, from 0.003 to ≥ 0.03 min.

Secondary predictions of the same mechanism (Wardrop equalisation): the share of CAVs ending on a route other than
the shortest rises from 25% to ≥ 45%; the share of CAVs placed on the same route by all methods falls below 40%
(53% at ×1); and at ×3 the spread between methods is *smaller* than at ×2 (non-monotone price of anarchy).

- **Mechanism.** Interaction needs flow near capacity on the parts where routes differ. At ×1 trips are already 1.9 ×
  free-flow, but the differing quarter-to-half of each route (time-weighted overlap 61%, F14) is uncongested. Doubling
  the flow moves link loads up the steep part of the delay curve; under user equilibrium the used routes then
  equalise in time and a vehicle's best route depends on who else took it. On real networks the price of anarchy is
  near 1 at low and at very high demand and largest in between (Youn, Gastner and Jeong, Phys. Rev. Lett. 2008,
  from memory, not re-read), which is why ×3 may compress differences again.
- **Cheapest test.** The ×2 base set the implementer will run anyway: `ref_tabular_iql`, `ref_aon`, `regret_matching`,
  `msa_switch`, `hedge_group` (5 runs), plus one **distant oracle**: build the table from the five, pick the assignment
  that the table says is best *and* differs from the reference's final routes for at least 40% of CAVs, write its
  predicted `t_CAV` into the ledger before running it (1 run). Total 6 runs; only the oracle is extra. Then the same
  analysis on the ×3 base set (3 runs: reference, AON, regret) for the non-monotone part.
- **Refuted if.** Prediction error stays ≤ 0.5% for all methods *and* the distant oracle lands within 0.5% of its
  written prediction *and* the externality stays below 0.01 min.
- **Worth.** This is the gate for every coordination, marginal-cost and fleet-assignment idea. Positive: "vehicles
  interact at ×2 but not at ×1, measured by the same diagnostic" is criterion (i) — what works and why, tied to a
  structural property — and it defines the setting in which a new method can be judged. Negative: also publishable,
  and it saves building H6.
- **Main way to mislead.** The table is fitted on arrangements the methods reached; with stronger interaction the
  methods may still reach similar arrangements and the table can still predict (F10's "local" caveat). Only the
  distant oracle refutes cleanly. Teleports (H1) can inflate cell variance at ×2 if any occur; check first.
  Humans are frozen at their ×2 day-300 state, so any human re-sorting is excluded by design.

## H3. The learning-time gap grows with congestion

**Statement.** At ×2, the reference's mean CAV travel time over training days exceeds the pre-CAV baseline of the same
vehicles by ≥ 4% (1.2% at ×1), shared-estimate methods (`regret_matching`, `msa_switch`) stay at least 3% *below*
that baseline, and remaining humans are ≥ 1.5% slower during the reference's training than before CAVs (0.4% at ×1).

- **Mechanism.** The reference explores at epsilon 0.5 → 0.40: about 40% of CAVs drive a random route each day. At ×1
  a random route costs only its free-flow excess (13% for the second route). Under congestion a random route also
  dumps load onto alternatives that are near capacity, slowing whoever uses them, humans included; the cost of
  exploration becomes a cost imposed on others, which grows with the slope of the delay curve. Shared-estimate methods
  explore through the pair's experience and optimism for untried routes, so they do not load bad routes at random.
  Rests on the review's training-time numbers (4.500 vs 4.224) and its epsilon finding.
- **Cheapest test.** From the ×2 base-set logs (no extra run): mean CAV and remaining-human time over training days
  301–900, against the same vehicles in days 251–300. Plus **one extra run**: the reference with epsilon reaching
  0.05 by day 450, to separate "the reference's schedule" from "independent epsilon-greedy learning". Total 1 extra run.
- **Refuted if.** The reference's training excess over baseline at ×2 is under 2%, or the gap between reference and
  regret matching in training time is no larger (relative) than at ×1 (about 6%), or the fast-epsilon reference closes
  it to under 1%.
- **Worth.** This is the cleanest route to the maintainer's criterion (ii): an advantage that already exists in the
  standard setting (6% during training, measured) and is predicted to *grow* elsewhere, without changing route sets
  or human choice sets. A paper can frame it as "the cost of learning is borne by humans under congestion". If the
  fast-epsilon reference closes the gap, the finding is about the upstream schedule, still worth reporting.
- **Main way to mislead.** The metric: `cost_of_learning` in the table is a spread, not time lost; only the
  training-day means from trip logs answer this. The schedule confound (handled by the extra run). One seed. Logs
  keep every fifth day only.

## H4. Pair-level share methods close their gap under congestion

**Statement.** At ×2, `hedge_group` and `share_controller` end within 0.2% of the reference's `t_CAV` or better
(they trail by 0.81% and 0.84% at ×1).

- **Mechanism.** At ×1 the right object is "each CAV's best route" and pooled methods lose by not individualising
  (F6). Under congestion the right object becomes a *flow split* across routes of a pair (Wardrop): which individual
  takes which route matters less than how many do, and a share is exactly what these methods learn. The review found
  part of Hedge's loss was the whole pair gathering on one route, an interaction effect; congestion should punish
  gathering in the reference too. Follow-up if positive: split shares by departure-time bucket (candidate K).
- **Cheapest test.** Uses `hedge_group` from the base set plus `share_controller` (1 extra run). Compare with the
  reference on `t_CAV`; then the F6 decomposition (individualisation part vs interaction part).
- **Refuted if.** Both still trail by ≥ 0.6%.
- **Worth.** Criterion (i): a reversal in ranking explained by a structural change (from argmin to flow split) is
  the most persuasive form of "what works and why". Not an innovation on its own.
- **Main way to mislead.** The reference itself may get worse at ×2 because of exploration (H3), making the share
  methods look better by comparison; read `t_CAV` against the AON and against the oracle, not only the reference.
  One seed: differences under ~0.5% are within what a second seed can flip.

## H5. Under congestion a selfish fleet slows the remaining humans

**Statement.** At ×2, the same remaining humans are at least 1.0% slower on test days than in days 251–300 under the
reference (−0.2% ± 0.3% at ×1), and the test Gini of travel times rises by at least 0.005 over its pre-CAV value.

- **Mechanism.** Humans are frozen and cannot react; CAVs that leave a congested shortest route move onto
  alternatives that humans of other pairs also use. When those links are near capacity, every CAV that moves
  imposes delay on them. Published two-route analysis shows a selfish fleet's advantage reversing and humans ending
  worse off above a modest share (arXiv 2409.12839, `literature.md`); the counterfactual social reward
  (arXiv 2510.11410) found about 0.4% on a thin real network, consistent with there being nothing to fix at ×1.
- **Cheapest test.** No extra runs: from the ×2 base set, the same-people comparison already scripted for F11, the
  Gini and longest-trip columns of `BenchmarkMetrics.csv` (F13), and the share of humans made worse by more than 5%
  (missing metric, computable from logs).
- **Refuted if.** Remaining humans change by less than 0.5% under every method at ×2, or AON (which does not move
  CAVs) harms them as much as the reference does.
- **Worth.** High for the group's own agenda (social impact of CAVs is their stated theme) and a precondition for H6
  being worth anything. Gives URB a congested arena where its fairness columns finally move.
- **Main way to mislead.** Comparing different groups of people (the error F11 corrected): `t_pre` mixes future
  CAVs and humans, so only the same-people comparison counts. Teleports of humans
  (H1) can create a large change from a few vehicles; report with and without removed trips. Standard error at ×1 was
  0.013 min with 10 vs 20 logged days; at ×2 day noise may be larger.

## H6. A link-level marginal-cost learner improves total time under congestion and ties at ×1

**Statement.** A tabular learner whose reward adds an estimate of the delay it imposes on all vehicles sharing its
route's road segments reduces `t_test` (everyone) by ≥ 1.0% at ×2 against the reference, keeps `t_CAV` within 0.5%
of it, and is within ±0.1% on `t_CAV` at ×1.

- **Mechanism.** Marginal-cost pricing turns selfish equilibrium into the system optimum (Pigou, Beckmann; toll-based
  Q-learning, Ramos and others, in `literature.md`). It had nothing to act on at ×1 (F4, F9). The existing
  `marginal_cost_q` counts only same-pair, same-route CAVs and keeps epsilon 0.40, so it cannot see cross-pair load
  on shared segments, which is where congestion bites. Estimate the externality from the day's log: for each segment,
  flow × slope of the segment's time against its flow fitted over the past days (segment lists in `routes.csv`).
- **Cheapest test.** Only after H2 or H5 is positive. One implementation; then 2 runs (×2 and ×1, seed 40) plus the
  ×2 reference from the base set. Weight on the externality fixed in advance at 1 (textbook marginal cost); no tuning
  before the first result.
- **Refuted if.** `t_test` improves by less than 0.5% at ×2, or `t_CAV` loses more than 1% for it.
- **Worth.** Directly addresses criterion (ii) if it holds: no loss in the standard setting, a gain where congestion
  exists, no extra routes. For a paper it connects URB to the system-optimum literature with a mechanism, not a tuned
  reward. If H2 is negative, this is not worth building.
- **Main way to mislead.** Fitting segment slopes from realised times mixes signal delay with queueing (F12 left
  them unseparated); a mis-estimated slope can produce oscillation that looks like learning noise. A gain in
  `t_test` may come from CAVs absorbing teleports (H1). Weight tuning on seed 40 then reporting seed 40 would be
  in-sample; keep the weight fixed or tune on another seed.

## H7. Same-day information becomes informative during training, but not at test while humans are frozen

**Statement.** At ×2, among CAVs with at least three earlier same-pair departures on the day, the correlation between
the anomaly of the day's ETA for the chosen route and the anomaly of the CAV's own travel time is ≥ 0.2 over training
days (0.003 at ×1), and below 0.05 over test days.

- **Mechanism.** The ETA is a running mean over earlier same-pair vehicles today. It carries information only if
  today differs from other days. During training, other CAVs' exploration makes days differ, and congestion makes
  those differences propagate to travel time. At test everything is frozen and humans draw identical choices every
  day (review), so days barely differ and there is nothing to predict. If so, a reactive method can only help during
  learning, or in a setting where days genuinely differ (H8, demand noise).
- **Cheapest test.** No extra runs: the F3 computation on the ×2 base-set logs, split by phase and by number of
  earlier same-pair departures.
- **Refuted if.** Training-phase correlation stays under 0.1 at ×2 (the information stays empty even with
  interaction), or test-phase correlation exceeds 0.2 (then a reactive method is worth building at test too).
- **Worth.** Mostly a design decision: it tells whether to spend effort on observation-using (neural or reactive)
  methods, which upstream has invested in. A positive split result explains why observation-rich learners have not
  beaten bandits — criterion (i).
- **Main way to mislead.** The ETA is biased low by about 1.1 min (F3) and starts from free-flow for first departures;
  anomalies must be taken within CAV and route. Logs every fifth day only.

## H8. With adapting humans under congestion, tracking methods beat averaging ones

**Statement.** With `should_humans_adapt: true` at ×2, `msa_switch` with a constant step (or `annealed_revision`)
beats the reference's `t_CAV` by ≥ 1.0%, while with adapting humans at ×1 the difference stays under 0.3%.

- **Mechanism.** Frozen humans make the CAVs' problem stationary, so averaging learners are adequate. Adapting humans
  respond to CAV moves; under congestion the response is large, so the payoff of a route drifts while CAVs learn.
  Day-to-day route choice with strong congestion and fast learning can oscillate rather than settle (Horowitz 1984;
  Cascetta 1989; from memory). A learner that weights recent days, and one that revises gradually, should track the
  moving target; an epsilon-greedy running mean lags it. Never tested upstream (`open_questions.md`: all 581 stored
  runs have frozen humans).
- **Cheapest test.** New arena variant (task config flag only). Runs: reference and `msa_switch` at ×1 and ×2 with
  adapting humans (4 runs), plus `annealed_revision` at ×2 (1 run). Total 5 runs. Measure `t_CAV`, remaining-human
  time, and day-to-day route switching of humans in test.
- **Refuted if.** At ×2 with adapting humans the tracking methods are within 0.5% of the reference, or the system
  settles within 50 days after CAVs appear (no drift to track).
- **Worth.** Opens the non-stationary setting the benchmark has never measured; a method that wins only there is an
  innovation of type (ii) only if it also ties at ×1, which the design checks. Strong for a paper because it is new.
- **Main way to mislead.** Adapting humans also learn during the CAVs' test days, so `t_CAV` at test depends on how
  far humans have moved; compare at matched test windows. Common random numbers break once humans adapt differently
  under different methods, so one seed is weaker here than in frozen arenas. Human learning rate is a free parameter
  of the environment; report it and do not tune it.

---

## Ranking by expected value per run

Base set at ×2 (assumed to be run by the implementer anyway): `ref_tabular_iql`, `ref_aon`, `regret_matching`,
`msa_switch`, `hedge_group`. Base set at ×3: reference, AON, regret matching. "Extra runs" counts runs beyond these.
Run time at ×2 and ×3 is unknown: at ×1 a day takes about 8 s; with twice the vehicles and queues expect at least
twice that, so a 1000-day run may take 5 h rather than 2.5 h. A smoke run gives the number.

| Rank | Hypothesis | Extra runs | Why this rank |
| ---: | --- | ---: | --- |
| 1 | H1 teleports at ×3 | 0 (+1 smoke) | Free; invalidates or protects every ×3 number |
| 2 | H2 arrangement starts to matter | 1 (distant oracle) + ×3 base | Gate for H4–H6; positive or negative it decides the next month |
| 3 | H3 learning-time gap grows | 1 (fast-epsilon reference) | Free from base logs except one control; best fit to criterion (ii) as it stands |
| 4 | H5 humans pay | 0 | Free; strong for the group's agenda; precondition for H6 |
| 5 | H7 same-day information | 0 | Free; settles a design question, small direct value |
| 6 | H4 share methods close the gap | 1 | One run for a clean "ranking reverses because the objective changes" result |
| 7 | H6 link-level marginal cost | 2 + implementation | Highest payoff if H2/H5 are positive; worthless if not |
| 8 | H8 adapting humans | 5 + new arena | New and strong for a paper, but most runs and most confounds |

## The three to run first

1. **H1 (teleport audit) on the first ×3 smoke and base runs.** It costs nothing and every other ×3 statement depends
   on it. If removed trips are frequent, ×3 should be redefined (e.g. ×2.5, or `stuck_time` raised and the penalty
   reported separately) before any method is screened there.
2. **H2 with the distant oracle at ×2.** One extra run decides whether vehicles interact at all under congestion.
   Without that, coordination, marginal-cost and fleet-assignment families are guesses; with it, H4–H6 have a
   mechanism to act on. The prediction is written before the run, which is the only test the review accepts.
3. **H3 with the fast-epsilon reference at ×2.** One extra run turns an already-measured standard-setting advantage
   (shared-estimate methods about 6% faster during training) into either a congestion-amplified effect or a
   correction of the upstream schedule. Both outcomes are reportable, and it is the only hypothesis that fits the
   maintainer's criterion (ii) without new code.

H5 and H7 should be computed on the same logs at the same time, since they cost no runs.

## Questions for the critic

1. **Does ×2 actually create queueing on the parts where routes differ?** The ranking assumes that ×2 is the regime
   "interaction without gridlock". Check from the first ×2 logs: ratio of realised to free-flow time (1.9 at ×1) and,
   per pair, the time difference between routes' non-shared segments under ×1 vs ×2. If the ratio stays near 2 or
   the non-shared segments stay at free-flow speed, H2, H4, H5 and H6 drop sharply in value.
2. **Is the 6% training-time gap a method effect or the reference's epsilon schedule?** H3's rank rests on it being at
   least partly the former. A check that needs no run: in the ×1 reference logs, restrict to CAV-days where the
   reference took its eventually-final route and compare that mean with regret matching's training mean; if the gap
   vanishes, the effect is the schedule and H3 should be re-scoped as a correction, not a method finding.
3. **Is one seed enough at ×2 for differences of 0.5–1%?** The ranking treats single-seed results at ×2 as informative
   because humans draw identical choices across methods (common random numbers). Check whether that identity still
   holds after demand scaling (same CAV set, same human route draws across two ×2 runs), and whether the day-to-day
   standard error of `t_CAV` at ×2 is still near 0.0015 min. If either fails, every threshold above needs a second
   seed before it can refute anything.
