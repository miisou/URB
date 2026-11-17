"""Pack the per-day trip logs of finished runs into one compact table per run (run on the cluster node).

    python extract_trips.py <results dir> <output dir> [substring ...]

Runs whose name contains any of the substrings (default: "screen_s40") are packed; a run already packed is
skipped. Also copies each run's routes.csv (route index = order within the pair, free-flow time in minutes)
and exp_config.json next to the table, for the congestion analysis.
"""
import glob, os, re, shutil, sys
import pandas as pd

src, dst = sys.argv[1], sys.argv[2]
wanted = sys.argv[3:] or ["screen_s40"]
os.makedirs(dst, exist_ok=True)
for run in sorted(os.listdir(src)):
    files = glob.glob(f"{src}/{run}/episodes/ep*.csv")
    if not any(w in run for w in wanted) or not files:
        continue
    if not os.path.exists(f"{src}/{run}/metrics/BenchmarkMetrics.csv"):
        print(run, "not finished, skipped", flush=True)
        continue
    for extra, suffix in (("routes.csv", ".routes.csv"), ("exp_config.json", ".exp_config.json")):
        if os.path.exists(f"{src}/{run}/{extra}"):
            shutil.copy(f"{src}/{run}/{extra}", f"{dst}/{run}{suffix}")
    if os.path.exists(f"{dst}/{run}.csv.gz"):
        continue
    frames = []
    for f in files:
        x = pd.read_csv(f, usecols=["travel_time", "id", "kind", "action", "origin", "destination", "start_time"])
        x["day"] = int(re.findall(r"ep(\d+)", os.path.basename(f))[0])
        frames.append(x)
    out = pd.concat(frames, ignore_index=True)
    out.to_csv(f"{dst}/{run}.csv.gz", index=False)
    print(run, len(files), "days", len(out), "rows", flush=True)
