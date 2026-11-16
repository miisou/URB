# tabular_q_port

- **Idea:** the reference tabular Q-learner rewritten against the lab interface (`lab/fleet.py`), with the same hyperparameters and the same use of random numbers.
- **Changes relative to the reference:** none intended. It runs through `scripts/lab_runner.py` instead of `scripts/iql_tabular.py`.
- **Why:** it checks the runner. It also measures how much two runs with the same seeds differ, which is the noise floor for every later comparison.
- **Prediction:** `t_CAV` within 0.2% of `ref_tabular_iql` on seed 40 (identical if SUMO is deterministic for a fixed seed).
- **Drop if:** it differs by more than 1%. Then the runner does not reproduce the reference and must be fixed before any candidate is trusted.
