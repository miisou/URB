# tabular_q_decay

- **Idea:** the reference tabular Q-learner (`tabular_q_port`, same code) with an exploration schedule that actually ends: epsilon goes from 0.5 to 0.05 by training day 450 and stays at 0.05 (`eps_decay` = 0.1^(1/450) = 0.994896, applied once per day).
- **Changes relative to the reference:** only `eps_decay` (0.999628 in `config_ing_short`, which takes epsilon from 0.5 to 0.40 over 600 days). Upstream config and `ref_tabular_iql` are untouched.
- **Why:** an independent review found the reference still explores on 37% of late training days. "Nothing beats the reference" was measured against a learner whose schedule was made for a ten times longer run. This candidate is the properly decaying reference.
- **Prediction:** test `t_CAV` within ±0.3% of `ref_tabular_iql` on seed 40 (default arena) and on `p12` (test days are greedy in both, and F2 puts the reference near its own optimum); slightly better rather than worse because the Q-values of the final routes are less polluted by exploration days. Mean CAV time over training days 301–900 clearly lower than the reference's 4.500 (4 routes) and 4.689 (12 routes), close to the 4.22–4.25 of the pair-level methods.
- **Drop if:** not a method candidate but a corrected reference. If it beats `ref_tabular_iql` by more than 0.3% at test, the standings in F8 must be re-read against it.
