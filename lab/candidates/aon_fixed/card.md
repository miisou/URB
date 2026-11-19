# aon_fixed

- **Idea:** all-or-nothing through the lab runner: every CAV drives the route with the shortest free-flow time on every day, with 600 nominal training days, so its test days are days 901–1000 like every learning candidate.
- **Changes relative to `ref_aon`:** same choice rule, but `ref_aon` (`scripts/baselines.py --model aon`) trains for 200 days and tests on days 501–600. Humans draw identical choices on identical day numbers across runs of a seed, so only a run that tests on the same day numbers is a paired comparison. `ref_aon` is kept as it is.
- **Why:** paired all-or-nothing baseline on the default arena and on the congested arenas `d2` and `d3`.
- **Prediction:** `t_CAV` within 0.3% of `ref_aon` on the default arena (only the human draws differ); on `d2`/`d3` no prediction.
- **Drop if:** not a method; a check. If it differs from `ref_aon` by more than 1% on the default arena, day numbers matter more than assumed.
