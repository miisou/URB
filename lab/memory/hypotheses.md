# Hypotheses for the congested setting (demand ×2 and ×3 on `ingolstadt_custom2`)

First written 17 November 2026; **revised the same day after an independent critic's review** (see
"Revision log" at the end: what was accepted, how it was checked, and where this file still disagrees).
Nothing here is a result; every entry is a prediction with the number that would refute it.

Built on `findings.md` as corrected by its own review section, `system.md`, `idea_map.md`, `literature.md`; on code
read in `RouteRL/routerl/environment/{simulator,environment,observations}.py` (`routerl-nightly`); and on checks run
on the packed 4-route trip logs in `lab/diag/trips/` (seed 40, every fifth day; `tabular_q_port` stands in for the
reference, which it reproduces to four decimals).

## What is already known and constrains these hypotheses

- At ×1 a CAV's time is mostly set by its own route (F10, narrowed): arrangement effects are about 0.2%, the same
  size as differences between methods. Per extra same-pair CAV on a route: 0.003 min (review's fixed-effects estimate).
- Realised trips are 1.9 × free-flow (F12).
- **Reference training time is its own exploration (checked).** Days 301–900: when a reference CAV drives its
  eventually-final route its mean time is 4.127 min (58% of CAV-days); on the other 42% it is 5.008 min. The critic
  also reports that the same CAV on its final route differs between training and test by −0.003 ± 0.0055 min, i.e.
  at ×1 exploring CAVs do not slow non-exploring ones measurably.
- **Exploration does reach humans a little at ×1 (checked).** Humans are 0.027 ± 0.007 min (0.6%) slower on days
  when the reference trains than on the same day numbers when `regret_matching` trains (paired by day, 120 logged
  days, regret's human mean 4.497).
- **Humans re-draw every day (checked).** Between neighbouring logged test days 61% of humans change route. What is
  identical is the choice on the *same day number* across different runs of a seed (100%): common random numbers
  across methods, not frozen choices across days.
- **The `trip_info_eta` observation (read in code, `observations.py`).** For each route: an exponential moving
  average (alpha = 2/(k+1)) over the last at most 10 travel times of vehicles of the same pair that departed no later
  than the CAV *and have already arrived*, started from the route's free-flow time. With 4-minute trips and departures
  spread over 30 minutes, most CAVs see few or no arrived same-pair vehicles.
- **All-or-nothing is not paired by day.** `ref_aon` uses `config1` of the baseline script, `training_eps` 200
  (checked: its logs end on day 600), so its test days 501–600 have different human draws from the reference's
  901–1000. Any day-paired comparison with AON needs AON re-run with 600 training days.
- **No noise floor for a second algorithm seed exists.** Same seeds reproduce to four decimals; the spread from a
  second algorithm seed on the same environment seed has not been measured. Until it is, differences below about 1%
  between methods refute nothing.
- `marginal_cost_coefficient_beta` appears in upstream task configs but no use of it was found in `routerl/`.

## Stuck-vehicle removal (read in code, counted in logs)

RouteRL's default (`use_sumo_teleport: false`) removes a vehicle after `stuck_time` = 600 consecutive simulation
steps at zero speed and records its trip as `simulation_timesteps / 60`; URB scripts set `simulation_timesteps` to the
latest departure, about 1798 s, so every removed vehicle gets ≈ 29.97 min. Removal also clears the jam.

**It already happens at ×1 (checked):** 21 such trips in the packed logs, in 5 events of 3 to 5 vehicles, each event
on one day (days 375, 430, 515, 515, 765), all on training days, departures late in the window (about 1385–1694 s).
The unit is therefore an *event* (a local gridlock removing a cluster of vehicles), not a trip. One 5-vehicle event
adds about 0.06 min to that day's `t_CAV` if two of them are CAVs.

---

## Kept hypotheses, in revised rank order

### R1 (was H1). Gridlock events decide the ranking at ×3

**Statement.** At ×3 (4 routes, 40% CAVs, seed 40) there is at least one removal event per test day on average, and
removal events account for at least half of the test-phase `t_CAV` difference between the reference and a day-paired
all-or-nothing run.

- **Mechanism.** Events at ×1 already occur late in the departure window, where load peaks. More vehicles in the same
  window make local gridlocks more frequent; each one costs ≈ 30 min per removed vehicle and clears the jam, a flat
  penalty that is an artefact of the simulator setting, not traffic.
- **Cheapest test.** Smoke at ×2 and ×3 (counts events per day directly). Then, on the ×3 base runs: events per day
  and per phase; a per-day decomposition of the reference-vs-AON `t_CAV` difference into removed-trip and
  normal-trip parts. **Needs one AON run with 600 training days** per demand level to be paired by day. Extra runs: 1
  (+ smokes).
- **Refuted if.** Fewer than 0.1 events per test day, or removed trips explain less than 20% of the paired difference.
- **Worth.** Validity gate for anything at ×3 (and at ×2 if events appear there). A benchmark-pitfall result of the
  kind the group publishes: a flat removal penalty can decide congested rankings.
- **Main way to mislead.** The demand-scaling procedure (duplicated agents departing in the same second can create
  insertion queues); one seed; the counter only catches full stops, so stop-and-go queues escape it.

### R2 (was H3, restated). Under congestion the reference's exploration costs humans more

**Statement.** At ×2 the remaining humans are at least 2% slower, paired by day, while the reference trains than
while `regret_matching` trains (0.6% ± 0.15% at ×1), and a reference whose epsilon reaches 0.05 by day 450 cuts that
penalty by at least half.

- **Mechanism.** At ×1 exploration is a private cost (the explorer pays 5.008 vs 4.127 min) with a small spillover
  to humans (0.6%) and none measurable to other CAVs. Exploration puts about 40% of reference CAVs on a random route
  each day. Under congestion that load lands on alternatives near capacity, so the private cost becomes a cost
  imposed on others, growing with the slope of the delay curve. The measured ×1 spillover is the baseline the
  prediction scales from; the CAV-side gap (6% in training) is *not* claimed to be interaction.
- **Cheapest test.** The fast-decay reference at ×1 first (1 run): the critic's rough estimate is that it stays about
  3% slower than regret matching in training; this run measures that and the human spillover with the schedule
  removed. Then the same at ×2 (1 run) next to the ×2 base set. Measured: day-paired human time over training days,
  CAV training time split by on-final/off-final route, and the same-CAV-on-final-route training-vs-test shift (the
  direct test of spillover onto other CAVs). Extra runs: 2.
- **Refuted if.** At ×2 the paired human penalty is under 1%, or the on-final-route CAV time in training is no worse
  than in test (no spillover), or the fast-decay reference leaves the penalty unchanged (then it is not exploration).
- **Opposite outcome that must stay visible (from provocation P5, "hot stove").** One removal event drops a reference
  Q-value from about −4.1 to −9.3 (lr 0.2, read in `config/algo_config/iql_tabular/config_ing_short.json`); about 13
  further visits are needed to come back within 0.3 min, roughly 130 days at epsilon 0.4 and more than the whole
  training at 0.05. Running-mean estimators (`regret_matching`, `msa_switch`, `annealed_revision`, read in their
  cards) dilute one event instead. So if events are common at ×2–×3, the fast-decay reference can end *worse* on test
  `t_CAV` than the slow one. Report as a separate result: fast-decay test `t_CAV` minus slow-decay test `t_CAV`, and,
  among CAVs hit by a removal in training, the share whose test route differs from their best route on non-event
  days. A positive difference beyond the noise floor with a high burned share confirms P5 and limits R2's
  recommendation. At ×1 (checked, all five events in the packed logs): of 11 hit CAVs, 1 was clearly burned (a
  `hedge_group` CAV at 60% share left its non-event-best route for good, cost 0.28 min); none of the reference's 2 hit
  CAVs was on its best route.
- **Worth.** Criterion (ii) in its honest form: a method family (shared estimates, no random exploration) that is
  already no worse in the standard setting and whose advantage to *others* grows with congestion. For a paper: "who
  pays for a fleet's learning". If the fast-decay reference removes most of it, the finding is about the upstream
  schedule, still reportable.
- **Main way to mislead.** `cost_of_learning` is a spread, not time lost; use day-paired means from logs. Logs keep
  every fifth day. Humans at ×2 may not have settled by day 300 (see R5), which makes "before" a moving target; the
  regret-paired comparison avoids that window.

### R3 (new; was the control inside H2). The distant oracle at ×1, with an interval written beforehand

**Statement.** At ×1 an assignment chosen from the (CAV, route) table that differs from the reference's final routes
for at least 40% of CAVs lands inside a prediction interval written before the run, of half-width 0.3%.

- **Mechanism.** F10 says time is set by the own route near the arrangements reached; the review notes that the
  `static_oracle` check was local (88% overlap with the reference). A distant assignment is the only clean refutation.
  Caveat to record with the prediction: cells for routes a CAV rarely ended on are measured almost only on days when
  the reference explored, i.e. under exploration load, so the table itself may be biased for distant cells.
- **Cheapest test.** `lab/diag/make_oracle.py` with a distance constraint; the prediction and its interval go into the
  ledger first (interval from the cell standard errors plus the 0.2% arrangement effect). 1 run.
- **Refuted if.** The run lands outside the interval (then F10 is local even at ×1, and the ×2 test must be designed
  differently).
- **Worth.** Settles F10 before it is used as the ×1 baseline for R4. Without it, "interaction appears at ×2" has no
  clean ×1 reference.
- **Main way to mislead.** Exploration-load bias of distant cells (above); a distant assignment may put many CAVs on
  long routes and itself create congestion, which is fine for the test but means the interval must be honest.

### R4 (was H2). At ×2 the fleet's arrangement starts to matter

**Statement.** At ×2 the distant oracle (built as in R3 from the ×2 base runs) misses its written interval by more
than 1%, and the fixed-effects externality per extra same-pair CAV on a route is at least 0.03 min (0.003 at ×1).

The previous rule ("the leave-one-method-out error exceeds 1% for at least one of five methods") is dropped: picking
the worst of five is asymmetric and has no matching refutation. Leave-one-out errors are still reported, for all
methods, as description.

- **Mechanism.** Doubling flow pushes the non-shared parts of routes up the steep part of the delay curve; used
  routes then equalise (Wardrop) and a vehicle's best route depends on who else took it. The price of anarchy on real
  networks is largest at intermediate demand and falls again at very high demand (Youn, Gastner and Jeong, 2008,
  from memory), so ×3 may compress differences; check only after R1.
- **Cheapest test.** The ×2 base set (`ref_tabular_iql`, `ref_aon` with 600 training days, `regret_matching`,
  `msa_switch`, `hedge_group`; assumed run anyway) plus the ×2 distant oracle (1 extra run).
- **Refuted if.** The ×2 oracle lands inside its interval and the externality stays below 0.01 min.
- **Sharpened by P3 (pre-registered here, before any ×2 log exists).** A ×1 "near-saturation" index per
  (origin, destination, route) cell: rank-average of the within-vehicle day-to-day SD, skewness, and within-day lag-1
  correlation of successive trips, from all vehicles in days 201–300 of the reference log (human-only phase), cells with
  at least 40 trips (90 cells). Its Spearman correlation with the cell's mean time is 0.26, so it is not just the mean.
  Prediction: Spearman ≥ 0.2 between this index and the ×2/×1 mean-time ratio per cell, and better than the ×1 mean
  alone. Top 30 cells as (origin index, destination index, route index), highest first:
  (8,9,1) (4,2,3) (16,9,1) (0,2,0) (0,2,1) (1,10,2) (4,5,3) (0,5,0) (21,10,3) (4,5,2) (7,1,0) (4,3,0) (11,4,3)
  (1,10,1) (4,20,0) (7,9,0) (1,10,0) (11,3,0) (0,2,2) (1,1,1) (7,10,0) (7,10,2) (7,4,0) (11,5,1) (11,2,0) (0,3,3)
  (0,5,1) (8,9,3) (4,3,3) (7,10,1). Killed if Spearman < 0.2 or no better than the ×1 mean.
- **Zero-run companion (P1 at ×2).** Repeat the P1 analysis below on the ×2 base logs (5 worlds). At ×1 it failed
  its own kill criterion; at ×2 an out-of-sample R² ≥ 0.10 would be independent support for R4.
- **Worth.** The gate for coordination, marginal-cost and fleet-assignment ideas (R6, R7). Positive or negative, it
  is criterion (i): whether vehicles interact, tied to demand level, by the same diagnostic.
- **Main way to mislead.** Same exploration-load bias as R3, now stronger; removal events (R1); one seed.

### R5 (was H5, Gini dropped). Under congestion a selfish fleet slows the remaining humans

**Statement.** At ×2, under the reference, the same remaining humans are at least 1.0% slower on test days than on
the last 50 human-only days, and at least 10% of them are more than 5% slower.

The Gini criterion is dropped: Gini rises when CAVs get faster and humans do not change (`static_oracle`: humans
4.4996 unchanged, Gini 0.1886 → 0.1908), so it does not measure harm to humans.

- **Mechanism.** Humans keep their day-300 estimates; CAVs leaving a congested shortest route move onto alternatives
  that humans of other pairs also use. Near capacity, each move delays them (arXiv 2409.12839 for the two-route case;
  arXiv 2510.11410 found about 0.4% on a thin real network).
- **Cheapest test.** No extra runs: same-people comparison from F11 on the ×2 base logs; share of humans worse by
  more than 5%. **Settling check first:** slope of human mean time over days 200–300 at ×2; if it has not flattened
  (slope above 0.1% per 10 days), lengthen the human phase or use the AON-paired comparison instead of "before".
- **Refuted if.** Remaining humans change by less than 0.5% and fewer than 5% are made worse by 5%, or the day-paired
  AON run harms them as much.
- **Worth.** High for the group's stated theme; precondition for R6.
- **Main way to mislead.** Unsettled humans at day 300 (above); removal events falling on humans; standard error of
  the same-people comparison at ×1 was 0.013 min and may be larger at ×2.

### R6 (was H4). Pair-level share methods close their gap

**Statement.** At ×2 the `t_CAV` deficit of `hedge_group` and `share_controller` against the reference (about 0.8%
at ×1) shrinks below the measured second-algorithm-seed noise floor, or reverses.

- **Mechanism.** At ×1 the right object is each CAV's best route and pooled methods lose by not individualising (F6).
  Under congestion it becomes a flow split across routes (Wardrop), which is what these methods learn.
- **Prerequisite.** A noise floor: a second algorithm seed on environment seed 40 for the reference and one candidate,
  at ×1 and ×2 (4 runs). Without it the 0.2–0.6% thresholds in the earlier version refute nothing.
- **Cheapest test.** `hedge_group` is in the base set; `share_controller` is 1 extra run. Plus the noise-floor runs if
  not done already.
- **Refuted if.** Both still trail by more than twice the noise floor.
- **Worth.** A ranking reversal explained by a change of objective is a strong criterion-(i) result; not an innovation.
- **Main way to mislead.** The reference itself may get worse at ×2 through exploration (R2); compare against the
  oracle and the paired AON too.

### R7 (was H6). A link-level marginal-cost learner

**Statement.** A tabular learner whose reward adds an estimate of the delay it imposes on all vehicles sharing its
route's segments reduces `t_test` by at least 1.0% at ×2 against the reference, keeps `t_CAV` within 0.5%, and ties at ×1.

- **Mechanism.** Marginal-cost pricing moves a selfish equilibrium to the system optimum (Pigou, Beckmann; toll-based
  Q-learning, `literature.md`). The existing `marginal_cost_q` sees only same-pair, same-route CAVs.
- **Cost, restated.** Several days of implementation: the logs hold whole-trip times only, so per-segment loads and
  delay slopes must come either from SUMO edge-data output (new simulator option, larger raw results) or from a
  regression of trip times on segment loads reconstructed from `routes.csv`. Then 2 runs (×2, ×1) plus a second seed
  of the ×2 run. Only after R4 or R5 is positive.
- **Cheaper data paths to try first (provocations P4, P7).** P7, network tomography: per-segment times by
  nonnegative least squares from per-(pair, route) mean times and the path–segment incidence in `routes.csv` (not in
  this checkout; must be fetched), checked by leave-one-pair-out prediction (kill: median error above 0.30 min or
  best-route agreement no better than the shortest route). P4: if a few cells carry most of the externality (top 10%
  of cells ≥ 40% at ×2), the marginal-cost term is needed only on those. Both are zero-run analyses that may cut R7's
  implementation cost; neither is ranked separately.
- **Refuted if.** `t_test` improves by less than 0.5% at ×2, or `t_CAV` loses more than 1%.
- **Worth.** The most direct answer to criterion (ii) if it holds: no loss in the standard setting, gain under
  congestion, no extra routes. Worthless if R4 and R5 are negative.
- **Main way to mislead.** Segment slopes mix signal delay and queues; mis-estimated slopes can oscillate; a gain in
  `t_test` may come from avoiding removal events (R1); tuning the weight on seed 40 and reporting seed 40.

### R8 (was H8). With adapting humans under congestion, tracking methods beat averaging ones

**Statement.** With `should_humans_adapt: true` at ×2, `msa_switch` with a constant step (or `annealed_revision`) beats
the reference's `t_CAV` by at least 1.0% on two algorithm seeds, while at ×1 with adapting humans the difference is
below the noise floor.

- **Mechanism.** Adapting humans respond to CAV moves; under congestion the response is large and the CAVs' target
  drifts; day-to-day route choice with strong congestion can oscillate (Horowitz 1984; Cascetta 1989; from memory).
- **Cost, restated.** New arena variant; reference and `msa_switch` at ×1 and ×2, `annealed_revision` at ×2 (5 runs),
  each on a second algorithm seed (5 more): 10 runs, plus checking that human adaptation behaves sanely in a smoke.
  Common random numbers break once humans adapt differently under different methods, so the second seed is not optional.
- **Refuted if.** At ×2 the tracking methods are within the noise floor of the reference, or humans settle within
  50 days after CAVs appear.
- **Worth.** Opens the never-measured non-stationary setting; strong for a paper.
- **Main way to mislead.** Test `t_CAV` depends on how far humans have moved; compare matched windows; the human
  learning rate is a free environment parameter, report and do not tune it.

### R9 (was H7, rewritten and moved last). Same-day information at ×2

**Statement.** At ×2, among CAVs that have at least three arrived same-pair vehicles on their chosen route before they
depart, the within-CAV correlation between the day's ETA anomaly and the CAV's own travel-time anomaly is at least
0.2, on test days as well as training days.

- **What changed.** The first version assumed humans repeat their choices on test days, so days would not differ at
  test; that was wrong (61% of humans change route between neighbouring logged test days). Days do differ, so if
  congestion makes those differences matter, the signal could exist at test too. The counter-weight is the
  observation itself: only *arrived* same-pair vehicles count, so the eligible group is small (large pairs, late
  departures).
- **Cheapest test.** No runs: F3's computation on the ×2 base logs, restricted to eligible CAV-days, reporting how
  many CAV-days are eligible.
- **Refuted if.** The correlation stays under 0.1, or fewer than 10% of CAV-days are eligible (then the observation
  cannot drive a method whatever it contains).
- **Worth.** A design decision about observation-using methods; small direct value.
- **Main way to mislead.** The ETA starts from free-flow and is biased low by about 1.1 min (F3); take anomalies within
  CAV and route; logs every fifth day.

## Dropped candidates (unchanged reasoning)

Departure-time pooling (follow-up to R6); different route sets for humans (4) and CAVs (12) (environment change, first
in line once R4 shows interaction; it answers the maintainer's objection to F7-type gains); a fleet controller that
avoids gridlocking routes (conditional on R1, risks optimising an artefact); 60% CAVs at ×2 (second confound).

---

## Ranking by expected value per run

Base set at ×2 and ×3 is assumed to be run anyway; "extra runs" counts beyond it. Run time at ×2/×3 is unknown
(8 s per day at ×1); a smoke run gives it.

| Rank | Hypothesis | Extra runs | Why here |
| ---: | --- | ---: | --- |
| 1 | R1 gridlock events at ×3 | 1 paired AON per level + smokes | Validity gate; events already exist at ×1 |
| 2 | R2 exploration spills onto humans, with the P5 reversal kept visible | 2 (fast-decay reference ×1, ×2) | ×1 baseline already measured (0.6%); best fit to criterion (ii); P5 says which way it can fail |
| 3 | R3 distant oracle at ×1 | 1 | Makes F10 a clean baseline; P1 showed the existing runs cannot replace it |
| 4 | Noise floor (second algorithm seed) | 4 (×1 and ×2) | Needed before any threshold under 1% means anything; P1 shows identical human choices still differ by 0.22 min SD per trip between runs |
| 5 | R4 arrangement matters at ×2, with the P3 list pre-registered | 1 (×2 oracle) | Gate for R6–R7; P3 adds a "where" prediction at no cost |
| 6 | R5 humans pay at ×2 | 0 | Free on base logs, after the settling check |
| 7 | R6 share methods close the gap | 1 | Needs the noise floor |
| 8 | R7 link-level marginal cost | 3 + days of code (P7/P4 may shorten it) | Only if R4 or R5 is positive |
| 9 | R8 adapting humans | 10 + new arena | New but costliest and most confounded |
| 10 | R9 same-day information | 0 | Cheap but small value, and the observation is thin by construction |

## The three to run first

1. **R1** with events per day as the unit and a day-paired AON. Free apart from the AON re-run, and it protects every
   ×3 number.
2. **R2** with the fast-decay reference, at ×1 first. One run separates the upstream schedule from the method family,
   and the ×1 human spillover it measures is the baseline for the ×2 prediction.
3. **R3**, the distant oracle at ×1 with an interval written first. One run turns F10 from a local check into a clean
   baseline, so that R4 at ×2 has something to differ from.

This is the critic's order, accepted. Where this file still differs is in the next section.

## Where this file disagrees with the critic, and why

- **Submission order vs reading order.** R3 at ×1 does not depend on any ×2 run, and the queue (twelve runs start
  over about three hours) dominates wall time. R3 and the ×2 base set should be submitted in the same batch; only
  the *interpretation* of R4 has to wait for R3.
- **R2 is still about interaction, at the level where it shows.** The critic is right that the CAV-side training gap
  at ×1 is the reference's own exploration, and the file no longer claims otherwise. But the 0.6% day-paired human
  penalty shows that exploration already reaches others at ×1; the hypothesis is that this spillover scales with
  congestion. The critic's "about 3% slower with fast decay" is an estimate, not a measurement, so R2 keeps its rank
  until the fast-decay run exists.
- **R9 is weakened in one way and strengthened in another.** The arrived-only rule makes the observation thinner than
  assumed; daily human re-drawing makes days differ at test, which the first version wrongly denied. Net: kept, last.
- **The noise floor deserves its own slot.** The critic flagged the missing second-seed noise; this file promotes it
  to a ranked step (4 runs), because R4–R8 all depend on it.

## Response to `provocations.md` (17 November 2026)

Each mapping was checked against code or the packed 4-route logs (seed 40) before a verdict. Analyses were run from
scripts outside the repository; numbers are this session's, not reviewed yet.

Code checks: `agent_observations` filters on same pair, earlier-or-equal departure and not-self, with no filter on
kind, and reads `travel_times_list`, which holds every arrived vehicle, so **humans are in the observation** (P2's
premise holds). Reference lr 0.2, epsilon 0.5 with decay 0.99963 (P5's arithmetic holds).

| Provocation | Verdict | Reason | Number computed |
| --- | --- | --- | --- |
| P1 interaction from 11 existing worlds | Zero-run analysis only; **killed at ×1** | Spillovers onto humans with identical choices are real but not predictable from CAV counts per (pair, route): out-of-sample R² below its 0.10 kill line in both phases. Kept as a ×2 companion to R4 | Training days: 32% of human trips differ by > 0.05 min between a world and the cross-world mean, SD 0.25 min; ridge R² on held-out days ≤ 0.015 (own-cell count alone 0.007). Test days: 28%, SD 0.22 min; leave-one-world-out R² 0.03–0.08 |
| P2 learn from same-pair humans instead of exploring | **Reject** as a learner; not ranked | Fails its own kill criterion: even the privileged version agrees with the table-best route less often than the reference does | 153 CAVs with ≥ 3 same-pair humans and ≥ 2 observed routes. Agreement with split-half table-best: reference 69%, privileged human mean (days 251–300) 51%, observable-only (arrived before departure, training days) 46%, shortest route 43%. Time on the other half-table: reference 4.692, observable 4.791 (+2.1%), privileged 4.813, shortest 4.851 min. At most a warm start |
| P3 near-saturation index | Adopted as a zero-run pre-registration inside R4 | Cheap, makes R4 say *where*, and can only be tested once ×2 logs exist, so it must be written now | 90 cells; index vs ×1 mean time Spearman 0.26; top 30 listed in R4 |
| P4 superspreader cells | Zero-run analysis only, attached to R7 | Its ×1 input (P1's matrix) failed; can be retried at ×2 with the fixed-effects externality | — |
| P5 hot stove after removal events | Adopted as a sharpening of R2 (and read on R1's logs) | The arithmetic holds and it predicts the opposite of R2 under heavy congestion; R2's report now includes that outcome | At ×1: 11 CAVs hit; 1 clear burn (`hedge_group`, 60% share, 0.28 min); reference's 2 hit CAVs were not on their best route |
| P6 crossover / invasion fleets | **Reject for now** | Its kill criterion needs the noise-floor runs first; P1 shows run-to-run differences are per-trip butterfly effects rather than shared day shocks, which a crossover does not remove. Revisit after the noise floor, as a mixed-fleet question | — |
| P7 network tomography | Zero-run analysis only, attached to R7 | Needs `routes.csv` from the cluster; a possible cheap route to R7's link data | — |

**Answers to the provocateur's three questions.**

1. *What would rank the fast-decay reference below the slow one?* A test `t_CAV` worse for the fast-decay reference by
   more than the noise floor at ×2 or ×3, together with a high share of removal-hit CAVs left off their non-event-best
   route. R2 now reports exactly that difference and that share, so the outcome can be seen; the earlier refutation
   rule could not show it.
2. *Why does measuring interaction need new runs?* It was tried now at zero runs (P1). The 11 worlds are exact
   counterfactuals for humans, and they show that arrangement moves each human trip by about 0.22 min SD. But a linear
   model in CAV counts per (pair, route) predicts almost none of it out of sample (R² ≤ 0.08). The spillovers look
   like high-dimensional, butterfly-type sensitivity of the microsimulation, not a stable pair-to-pair matrix. R3 still
   needs its run; P1 at ×2 is kept as an independent companion.
3. *Why build the ranking on a learner that explores?* Because P2 was tested and failed: same-pair humans point to
   the table-best route for 46–51% of CAVs, against 69% for the exploring reference and 43% for the shortest route.
   Human choices are filtered by noisy, frozen, departure-mixed estimates (F6), which makes them a weak demonstrator.
   They might serve as a starting prior; exploration is still needed.

**One new fact from P1 that changes the noise-floor slot.** Common random numbers make human *choices* identical
across runs, not their *times*: about 30% of human trips differ by more than 0.05 min between runs, symmetric around
zero. Averaged over 621 humans and 20 test days this is small, but it means day-paired comparisons have per-trip noise
the earlier plan did not budget for. The second-seed runs measure it directly.

## Questions for the critic

1. **Does ×2 create queueing on the non-shared parts of routes?** Check from the first ×2 logs: realised/free-flow
   ratio (1.9 at ×1) and whether trip-time differences between routes of a pair grow. If not, R4–R7 lose most value.
2. **Are humans settled by day 300 at ×2?** R2 avoids the "before" window by pairing with regret matching, but R5
   does not. Check the slope of human mean time over days 200–300 in the ×2 smoke or base run.
3. **Does the day-pairing survive demand scaling?** Check that two ×2 runs of different methods have identical human
   choices on the same day number and the same CAV set. If not, every paired comparison above (R1, R2) loses its
   main defence against one-seed noise.

## Revision log (17 November 2026)

Critic's points and how each was checked before acceptance:

| Point | Check | Verdict |
| --- | --- | --- |
| Humans change route between test days (61%) | `lab/diag/trips`, reference: 0.611 between neighbouring logged test days; same-day agreement with regret 1.00 | Accepted; H7 rewritten as R9 and moved last |
| ETA counts only arrived same-pair vehicles, EMA over ≤10 from free-flow | `observations.py`, `get_ema` and `agent_observations` | Accepted |
| Reference on/off final route 4.127 / 5.008 min, 42% off | Days 301–900 of the reference log: 4.1268 / 5.0080, 42.4% | Accepted; H3 restated as R2 |
| Humans 0.027 ± 0.007 min slower while reference trains vs regret | Paired by day, 120 days: 0.0271 ± 0.0072 | Accepted; used as R2's ×1 baseline |
| Same CAV on final route, training vs test −0.003 ± 0.0055 | Not re-derived | Taken as the critic's number |
| 21 removed trips, 5 events, training days only | All packed logs: 21 trips, 5 events (3–5 vehicles), days 375–765, none on test days | Accepted; unit changed to events |
| AON test days are different day numbers | Baseline `config1` has `training_eps` 200; AON logs end on day 600 | Accepted; paired AON run added |
| H2 rule asymmetric; distant oracle first, at ×1 | Reasoning | Accepted; R3 added, R4's rule replaced |
| Gini rises with faster CAVs alone | `findings.md` F10/F13 `static_oracle` numbers | Accepted; Gini dropped from R5 |
| Unsettled humans at ×2 bias "before" | Reasoning; not checkable before ×2 runs | Accepted as a check in R5 |
| Thresholds of 0.2–0.6% refute nothing without a noise floor | No second-algorithm-seed run exists in `lab/runs/` | Accepted; noise floor ranked as its own step |
| H6 and H8 costs understated | Logs hold whole-trip times only (no per-segment data) | Accepted; costs restated |
