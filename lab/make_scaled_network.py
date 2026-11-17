"""
Make a demand-scaled copy of a network folder.

    python lab/make_scaled_network.py ingolstadt_custom2 2 ingolstadt_custom2_d2
    python lab/make_scaled_network.py ingolstadt_custom2 3 ingolstadt_custom2_d3

Every vehicle of agents.csv is kept and gets (factor - 1) copies with the same origin and destination and a
departure time jittered by a uniform integer in [-jitter, +jitter] seconds (default 60), clipped to the
original departure window, so the simulated period does not grow. Rows are sorted by departure time and get
new ids 0..N-1. Every other file is copied unchanged; files whose names carry the network name are renamed,
because RouteRL and scripts/lab_runner.py look for <net>.net.xml, <net>.rou.xml, <net>.con.xml,
<net>.edg.xml, <net>.nod.xml and od_<net>.txt inside networks/<net>/. clustered_routes/ is not copied (the
lab arenas do not use it). The random seed is fixed (default 2026).
"""

import argparse
import os
import shutil

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("factor", type=int)
parser.add_argument("target")
parser.add_argument("--jitter", type=int, default=60)
parser.add_argument("--seed", type=int, default=2026)
args = parser.parse_args()

src = os.path.join(ROOT, "networks", args.source)
dst = os.path.join(ROOT, "networks", args.target)
if os.path.exists(dst):
    raise SystemExit(f"{dst} exists; remove it first")
os.makedirs(dst)
for name in sorted(os.listdir(src)):
    path = os.path.join(src, name)
    if os.path.isdir(path) or name == "agents.csv":
        continue
    shutil.copy(path, os.path.join(dst, name.replace(args.source, args.target)))

agents = pd.read_csv(os.path.join(src, "agents.csv"))
rng = np.random.default_rng(args.seed)
lo, hi = int(agents.start_time.min()), int(agents.start_time.max())
copies = [agents.assign(copy=0)]
for k in range(1, args.factor):
    extra = agents.copy()
    extra["start_time"] = np.clip(extra.start_time + rng.integers(-args.jitter, args.jitter + 1, len(extra)), lo, hi)
    copies.append(extra.assign(copy=k))
out = pd.concat(copies, ignore_index=True)
out = out.sort_values(["start_time", "copy", "id"], kind="stable").reset_index(drop=True)
out["id"] = np.arange(len(out))
out["kind"] = "Human"
out[list(agents.columns)].to_csv(os.path.join(dst, "agents.csv"), index=False)
pairs_src = agents.groupby(["origin", "destination"]).size()
pairs_dst = out.groupby(["origin", "destination"]).size()
assert (pairs_dst == pairs_src * args.factor).all()
print(f"{args.target}: {len(out)} vehicles ({len(agents)} x {args.factor}), {len(pairs_dst)} pairs, "
      f"departures {out.start_time.min()}..{out.start_time.max()} s; files: {sorted(os.listdir(dst))}")
