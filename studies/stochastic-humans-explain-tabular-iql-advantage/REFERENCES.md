# References

List only sources that affect the hypothesis, implementation, or interpretation. Prefer stable links instead of copied PDFs.

| Source | Relevant point | Use in this study |
| --- | --- | --- |
| RouteRL `routerl/human_learning/learning_model.py`, class `Gawron` (v2.0.0 and `routerl-nightly`) | With `deterministic=false` the route is sampled with probability proportional to `exp(beta × cost)`; with `true` the highest-utility route is always taken | implementation |
| URB commit `3483d2b` ("new configs", 2026-06-02) | Introduced `human_deterministic: false`, 300 human-learning days, and `trip_info_eta` in the task and environment configurations | implementation |
| [`studies/independent-tabular-iql-cannot-beat-humans-provins`](../independent-tabular-iql-cannot-beat-humans-provins/FINAL_REPORT.md) | Tabular IQL beats sampling humans in Provins; source of the 1.02 threshold; names "frozen humans" among untested explanations | supports the threshold; challenges a general reading of this hypothesis |
| [`studies/tripinfoeta-improves-independent-iql`](../tripinfoeta-improves-independent-iql/FINAL_REPORT.md) | In `ingolstadt_custom2`, dynamic ETA gives no benefit over fixed route values, so learned policies are close to fixed-route choices | supports the reason |
| `results/iql_ing_*`, `results/ing_aon`, `results/ing_rnd` (April 2026) | Deterministic humans at about 4.20 min on `ingolstadt_custom`; no learner clearly faster; the only baseline runs in the repository | supports the reason |
| `results/tbq_ing2_*`, `results/tbrf_ing2_*` | Sampling humans at about 4.47 min on `ingolstadt_custom2`; tabular learners at about 4.32 min | supports the reason |
| Gawron (1998), *Simulation-based traffic assignment*, https://kups.ub.uni-koeln.de/9257/ | The human learning model | implementation |
