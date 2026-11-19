"""Write a fixed assignment from a pooled (CAV, route) table of seed-40 trip logs (lab/diag/trips/).

    python lab/diag/make_oracle.py                         -> static_oracle: every CAV on its table-best route
    python lab/diag/make_oracle.py --rank 2 --out static_distant
                                                           -> every CAV on its table-second-best route
                                                              (CAVs with one measured route keep it)
    python lab/diag/make_oracle.py --arena d2 --max-day 900 --training-eps 600 --out static_oracle_d2
                                                           -> arena d2, training days only (301-900), split-half check

Default (no --arena): the 4-route arena, every non-AON run, all days after 300 (test days included), as used for
static_oracle and static_distant. With --max-day the table uses only days 301..max-day, and runs whose own test days
fall inside that range (ref_aon: 200 training days) are left out. A split-half prediction is always printed: routes
chosen on odd logged days, valued on even logged days; it is the honest prediction (no selection on the same noise).
"""
import argparse, glob, json, os, re
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--rank", type=int, default=1)
parser.add_argument("--out", default="static_oracle")
parser.add_argument("--arena", default="")
parser.add_argument("--max-day", type=int, default=None)
parser.add_argument("--training-eps", type=int, default=10)
args = parser.parse_args()

here = os.path.dirname(os.path.abspath(__file__))
prefix = args.arena + "." if args.arena else ""
frames, used = [], []
for f in sorted(glob.glob(f"{here}/trips/*.csv.gz")):
    name = os.path.basename(f)[:-7]
    arena = name.split(".")[0] + "." if "." in name else ""
    if arena != prefix or "ref_aon" in name or "static_" in name or re.search(r"_a\d+$", name) or "screen" not in name:
        continue
    d = pd.read_csv(f, usecols=["id", "kind", "action", "travel_time", "day"])
    d = d[(d.kind == "AV") & (d.day > 300)]
    if args.max_day:
        d = d[d.day <= args.max_day]
    frames.append(d)
    used.append(name)
d = pd.concat(frames, ignore_index=True)


def table_of(x):
    s = x.groupby(["id", "action"]).travel_time.agg(["sum", "size"])
    s = s[s["size"] >= 5]
    return (s["sum"] / s["size"]).unstack()


def pick(table, rank):
    order = np.argsort(table.fillna(np.inf).values, axis=1)
    n_measured = table.notna().sum(axis=1).values
    k = np.minimum(rank, n_measured) - 1                      # fall back to the last measured route
    col = order[np.arange(len(table)), k]
    return pd.Series(table.columns.values[col], index=table.index), table.values[np.arange(len(table)), col]


table = table_of(d)
routes, values = pick(table, args.rank)
odd, even = table_of(d[(d.day // 5) % 2 == 1]), table_of(d[(d.day // 5) % 2 == 0])
r_odd, _ = pick(odd, args.rank)
common = r_odd.index.intersection(even.index)
honest = np.array([even.at[i, r_odd[i]] if r_odd[i] in even.columns else np.nan for i in common])
cfg = {"training_eps": args.training_eps, "rank": args.rank, "arena": args.arena or "default",
       "table_days": f"301-{args.max_day or 'end'}", "table_runs": used,
       "predicted_t_CAV": round(float(np.mean(values)), 4),
       "predicted_t_CAV_split_half": round(float(np.nanmean(honest)), 4),
       "assignment": {str(int(i)): int(r) for i, r in routes.items()}}
json.dump(cfg, open(f"{here}/../candidates/{args.out}/config.json", "w"), indent=1)
best = table.idxmin(axis=1)
print("runs:", used)
print(len(routes), "CAVs, in-sample", cfg["predicted_t_CAV"], "| split-half", cfg["predicted_t_CAV_split_half"],
      f"({np.isnan(honest).sum()} of {len(honest)} CAVs without an even-day cell)",
      "| on table-best:", int((routes == best).sum()), "| routes", routes.value_counts().sort_index().to_dict())
