"""Congestion summary of packed runs (lab/diag/extract_trips.py output).

    python lab/diag/congestion.py <trips dir> <run> [<run> ...]

Per run: phases from the run's exp_config.json (pre = human days, train = CAV learning days, test = rest).
- mean travel time of future CAVs and remaining humans before CAVs, of CAVs during training (from the trip
  logs, every logged day), and of CAVs and humans at test;
- removed trips: RouteRL takes a vehicle that stood still for `stuck_time` (600 s) out of the simulation and
  books it at simulation_timesteps / 60 min (simulation_timesteps = last departure, so about 29.97 min);
  counted as trips within 0.02 min of that value, per phase and in total;
- realised / free-flow time of the chosen route (routes.csv), median and mean;
- load effect: extra minutes per additional vehicle of the same pair on the same route on the same day,
  CAV trips of the CAV phase, with (CAV, route) and day fixed effects (two-way demeaning). Reported for the
  count of fleet CAVs and for the count of all vehicles of the pair on that route.
- removal events (logged days with at least one removal) per day, and the minutes of each group's mean they
  account for (mean with removed trips minus mean without);
- settling of the humans before CAVs: mean time of everyone in days H-99..H-50 against H-49..H.
"""
import json, os, sys
import numpy as np
import pandas as pd


def twoway_slope(y, x, g1, g2, iters=30):
    y, x = y.astype(float).copy(), x.astype(float).copy()
    for _ in range(iters):
        for g in (g1, g2):
            y -= y.groupby(g).transform("mean")
            x -= x.groupby(g).transform("mean")
    sxx = (x * x).sum()
    if sxx <= 0:
        return np.nan, np.nan
    b = (x * y).sum() / sxx
    resid = y - b * x
    dof = max(len(y) - g1.nunique() - g2.nunique() - 1, 1)
    se = np.sqrt((resid ** 2).sum() / dof / sxx)
    return b, se


def summarise(folder, run):
    d = pd.read_csv(os.path.join(folder, run + ".csv.gz"))
    cfg = json.load(open(os.path.join(folder, run + ".exp_config.json"), encoding="utf-8"))
    H, T = int(cfg["human_learning_episodes"]), int(cfg["training_eps"])
    d["phase"] = np.where(d.day <= H, "pre", np.where(d.day <= H + T, "train", "test"))
    cav_ids = set(d.loc[d.kind == "AV", "id"])
    d["future_cav"] = d.id.isin(cav_ids)
    sim_minutes = d.start_time.max() / 60.0
    d["removed"] = (d.travel_time - sim_minutes).abs() < 0.02
    routes = pd.read_csv(os.path.join(folder, run + ".routes.csv"))
    routes["action"] = routes.groupby(["origins", "destinations"]).cumcount()
    ff = routes.set_index(["origins", "destinations", "action"]).free_flow_time
    d["ff"] = ff.reindex(pd.MultiIndex.from_frame(d[["origin", "destination", "action"]])).values
    d["ratio"] = d.travel_time / d.ff
    out = dict(run=run, vehicles=d.id.nunique(), cavs=len(cav_ids), logged_days=d.day.nunique(),
               sim_min=round(sim_minutes, 2))
    pre, train, test = (d[d.phase == p] for p in ("pre", "train", "test"))
    out["CAV_pre"] = pre[pre.future_cav].travel_time.mean()
    out["HDV_pre"] = pre[~pre.future_cav].travel_time.mean()
    out["CAV_train"] = train[train.kind == "AV"].travel_time.mean()
    out["HDV_train"] = train[train.kind != "AV"].travel_time.mean()
    out["CAV_test"] = test[test.kind == "AV"].travel_time.mean()
    out["HDV_test"] = test[test.kind != "AV"].travel_time.mean()
    for name, part in (("pre", pre), ("train", train), ("test", test)):
        days = part.day.nunique()
        out[f"removed_{name}"] = int(part.removed.sum())
        # an event is a logged day with at least one removal
        out[f"removal_events_per_day_{name}"] = part[part.removed].day.nunique() / days if days else np.nan
        out[f"removed_per_day_{name}"] = part.removed.sum() / days if days else np.nan
    for name, part in (("train", train), ("test", test)):
        for kind, sel in (("CAV", part.kind == "AV"), ("HDV", part.kind != "AV")):
            x = part[sel]
            # minutes of the mean that come from removed trips being booked at ~30 min
            out[f"{kind}_{name}_minutes_from_removed"] = x.travel_time.mean() - x[~x.removed].travel_time.mean()
    a = d[(d.day > H - 100) & (d.day <= H - 50)].travel_time.mean()
    b = d[(d.day > H - 50) & (d.day <= H)].travel_time.mean()
    out["all_pre_days_-100_-51"], out["all_pre_days_-50_0"] = a, b
    out["human_drift_%"] = 100 * (b - a) / a
    out["removed_share_%"] = 100 * d.removed.mean()
    ok = d[~d.removed & d.ff.notna()]
    out["ratio_median"] = ok.ratio.median()
    out["ratio_mean"] = ok.ratio.mean()
    out["ratio_test_median"] = ok[ok.phase == "test"].ratio.median()
    out["CAV_test_without_removed"] = ok[(ok.phase == "test") & (ok.kind == "AV")].travel_time.mean()
    late = d[d.phase != "pre"].copy()
    late["n_all"] = late.groupby(["day", "origin", "destination", "action"]).id.transform("size")
    late["n_cav"] = late.groupby(["day", "origin", "destination", "action"]).future_cav.transform("sum")
    cav = late[(late.kind == "AV") & ~late.removed]
    pair_cavs = cav.groupby(["origin", "destination"]).id.transform("nunique")
    cav = cav[pair_cavs >= 2]
    for col in ("n_cav", "n_all"):
        cell = cav.id.astype(str) + "_" + cav.action.astype(str)
        b, se = twoway_slope(cav.travel_time, cav[col], cell, cav.day)
        out[f"load_{col}"], out[f"load_{col}_se"] = b, se
    return out


if __name__ == "__main__":
    folder, runs = sys.argv[1], sys.argv[2:]
    rows = [summarise(folder, r) for r in runs]
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 50)
    print(pd.DataFrame(rows).set_index("run").T.to_string(float_format=lambda v: f"{v:.4f}"))
