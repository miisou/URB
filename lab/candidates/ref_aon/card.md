# ref_aon

- **Idea:** all-or-nothing: every CAV always takes the route with the shortest free-flow time (`scripts/baselines.py --model aon`).
- **Role:** secondary reference. A candidate that does not beat it has learned nothing about congestion.
- **Origin of seeds 40–42:** runs `humdet_aon_sto_s40..42` of the study `stochastic-humans-explain-tabular-iql-advantage`.
