# static_oracle_600

- **Idea:** a diagnostic, not a method. `static_oracle` again, with exactly the same assignment (every CAV on its table-best route from eleven 4-route runs on seed 40), but with 600 nominal training days, so the test days are 901–1000 like every learning run.
- **Why:** the critic's third review found that `static_oracle` tested on days 311–410 and the reference on 901–1000. With humans drawing identical choices on identical day numbers, an unchanged policy moves by 0.42% between those windows (`ref_aon` 4.3458 on 501–600 against `aon_fixed` 4.3643 on 901–1000). The earlier "0.42% better than the reference" is the same size as a window effect and is not established.
- **Changes relative to `static_oracle`:** only `training_eps` 10 → 600. No learning, no exploration, the same routes on every day.
- **Prediction (written before the run):** `t_CAV` **4.197** on seed 40 (table value in-sample 4.1957; split-half 4.1967, critic's review 1), tolerance ±0.4% (the window effect measured at ×1), i.e. 4.180–4.214. The reference is 4.2114 on the same days. Inside the band and below 4.2114: the oracle's room above the reference survives on the same window. Above 4.2114: the earlier +0.42% was a window effect.
- **Drop if:** not applicable as a method.
