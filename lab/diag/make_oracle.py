"""Write a fixed assignment from the pooled (CAV, route) table of the 4-route arena on seed 40.

    python lab/diag/make_oracle.py                         -> static_oracle: every CAV on its table-best route
    python lab/diag/make_oracle.py --rank 2 --out static_distant
                                                           -> every CAV on its table-second-best route
                                                              (CAVs with one measured route keep it)
"""
import argparse, glob, json, os, re
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--rank", type=int, default=1)
parser.add_argument("--out", default="static_oracle")
args = parser.parse_args()

here = os.path.dirname(os.path.abspath(__file__))
parts = []
for f in sorted(glob.glob(f"{here}/trips/*.csv.gz")):
    name = os.path.basename(f)
    if "." in name[:-7] or "ref_aon" in name or "static_" in name or re.search(r"_a\d+$", name[:-7]):
        continue
    d = pd.read_csv(f); d = d[(d.kind == "AV") & (d.day > 300)]
    parts.append(d.groupby(["id", "action"]).travel_time.agg(["sum", "size"]))
s = pd.concat(parts).groupby(level=[0, 1]).sum(); s = s[s["size"] >= 5]
table = (s["sum"] / s["size"]).unstack()
order = np.argsort(table.fillna(np.inf).values, axis=1)
n_measured = table.notna().sum(axis=1).values
k = np.minimum(args.rank, n_measured) - 1                      # fall back to the last measured route
pick = order[np.arange(len(table)), k]
routes = pd.Series(table.columns.values[pick], index=table.index)
values = table.values[np.arange(len(table)), pick]
cfg = {"training_eps": 10, "rank": args.rank, "predicted_t_CAV": round(float(np.mean(values)), 4),
       "assignment": {str(int(i)): int(r) for i, r in routes.items()}}
json.dump(cfg, open(f"{here}/../candidates/{args.out}/config.json", "w"), indent=1)
best = table.idxmin(axis=1)
print(len(routes), "CAVs, predicted", cfg["predicted_t_CAV"], "| table-best mean", round(float(table.min(axis=1).mean()), 4),
      "| on table-best:", int((routes == best).sum()), "| with one measured route:", int((n_measured < args.rank).sum()),
      "| routes", routes.value_counts().sort_index().to_dict())
