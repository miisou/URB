# Where the leaderboard number misleads

Upstream `5457dcf`, November 2026.

## `CAV_advantage` depends on how slow the humans are

It is a ratio of human time to CAV time, so anything that slows humans raises it without any change in the CAVs.

| What changes the human baseline | Size | Evidence |
| --- | --- | --- |
| Humans sample routes instead of taking their best (`human_deterministic=false`) | humans 4.24 → 4.49 min, about 6% | controlled study, 12 runs, seeds 40–42 |
| 12 routes instead of 4, sampling humans | humans 4.51 → 4.68 min before any CAV | seed 40 |
| Clustered route sets | humans 4.85 min against 4.50 without | stored upstream runs |

Consequences seen:

- With deterministic humans the tabular-IQL advantage is about 1.00 instead of 1.04 (medians, three seeds).
- The all-or-nothing baseline, which learns nothing, scores 1.024 against sampling humans with 4 routes and 1.083
  with 12 routes. The current first place of the table is 1.056.
- The six top rows of the `ingolstadt_custom2` table (as of 16 November) use clustered routes: `t_CAV` 4.60 min,
  `CAV_advantage` 1.056. Tabular IQL below them has `t_CAV` 4.28 min and 1.047.

**Use `t_CAV` in minutes to compare methods, and only within one environment configuration.**

## Rows are not comparable across environment configs

The table mixes rows with different route sets, numbers of routes, human settings, and training lengths.
A row's rank says as much about its configuration as about its method.

## The jump above 1.0 in June 2026 was mostly a setup change

Between April and June the network, the human choice rule, the human-learning length, the observation, and the
training length changed together (commits `3483d2b`, `ad267e0`, `4432339`). CAV time in minutes did not improve
on Ingolstadt; the human baseline got slower. *Measured* for the choice rule alone; the other factors are not separated.

## `ingolstadt21`

Added 15 September, deleted 29 October and replaced by `ingolstadt21_10_30`. The name matches the RESCO
benchmark network (*inferred* from `networks/readme.md`, which lists RESCO networks).

- On the old version humans took 10.1 minutes before CAVs; CAVs reached 5.6; humans improved to 7.5 once CAVs appeared.
  `CAV_advantage` 1.4–1.7, highest at a 10% CAV share.
- On the replacement humans take 3.99 minutes and the same method gives about 0.99.

The old demand was far from a settled state, so a handful of CAVs leaving the jammed routes gained a lot.
Why it was replaced is not stated in the commit. Sixty-three stored results still come from the old version.

## Smaller traps

- `winrate` can be 1.0 while `CAV_advantage` is below 1: it compares CAVs with the whole system before them.
- Baselines (all-or-nothing, greedy, random) exist upstream only for the April setup. Whether a method beats the
  trivial baseline in the current setup is not in the table. In our arena all-or-nothing is 2.7% slower than
  tabular IQL (four seeds, range 1.3–4.3%).
- Many rows are one seed. Seed-to-seed spread of `t_CAV` for one method is about ±2%, larger than most
  differences between methods.
- Reward variants `selfish`, `collaborative`, `competitive`, `social` give the same result to three decimals in
  stored runs; `altruistic`, `cooperative`, `militant` fail. *Inferred* reason: a group mean barely depends on one
  CAV's own choice, so it shifts all its route values equally; with no own-time term there is no signal left.
- Route sets differ by seed when routes are generated on the fly, so "seed" also means "different routes".
