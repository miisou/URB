# Open questions and where headroom may be

As of 16 November 2026.

## The goal and its two readings

The stated goal is first place in the `ingolstadt_custom2` leaderboard table, currently `CAV_advantage` 1.056.

- **By the column:** a 12-route run of the unchanged reference gives 1.133 on seed 40. Reachable now, but the
  number comes largely from the environment (see benchmark_pitfalls). Needs three seeds before it is submitted.
- **By substance:** the lowest `t_CAV` within one environment configuration. Here the reference is unbeaten.

## Not yet measured

| Question | Why it matters | Cheapest test |
| --- | --- | --- |
| Do the seed-40 standings hold on seeds 41–43? | Differences of 0.1–1% between methods may flip | Confirm stage for `regret_matching`, `msa_switch`, reference; references for 41–43 exist |
| How does everything rank in the top rows' own environment (clustered routes)? | Needed to compare with the current first place on equal terms | Third arena on a clustered env config; reference plus best candidates |
| Which of 12 routes do CAVs use? | Tells whether the 2.5% comes from a few better routes or from spreading load | Usage by free-flow rank from the `p12` reference logs |
| Is 20 routes better than 12, and where does it stop? | Finds the end of the largest lever | Arena with 20 routes |
| How much do routes of different pairs interact? | Decides whether a link-level fleet model is worth building | Overlap of road segments between pairs weighted by flow, from `routes.csv` and one day's log |
| Is there headroom on Provins? | Upstream numbers there look better in absolute minutes | Port the arena to `provins` |
| What happens when humans adapt? | Never tested upstream; the problem stops being stationary, and methods that track change may separate | Task config with `should_humans_adapt: true` |
| How much of the seed spread is the route set and how much the CAV draw? | Tells how many seeds a claim needs | Same seed with a fixed clustered route set |

## Directions that could need a genuinely new algorithm

- **Route-set construction as the method.** Everything else is bounded by the routes offered. A method that
  proposes routes (from the road graph, from observed link times) and prunes them by experience attacks the
  bound directly. Open design points: how to keep it comparable with table rows, and how to avoid winning by
  slowing humans.
- **Non-stationary settings.** With adapting humans or changing demand, the day's information may start to matter
  and tracking methods may beat averaging ones. Nothing here has been tested.
- **Cheap learning as the product.** Several methods reach the reference's time at half its cost of learning.
  With 12 or 20 routes the reference's cost grows; a method whose cost does not grow with the number of routes
  would win on a setting where routes are plentiful.
- **Cross-pair coordination.** Only worth it if the interaction measurement above shows shared bottlenecks.

## Things to settle with the benchmark's maintainers

- Which human choice rule is the intended baseline.
- Whether rows with different numbers of routes belong in one ranking.
- Whether all-or-nothing rows should accompany every configuration.
