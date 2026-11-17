"""Is a CAV's travel time a function of its own route only? Compare final routes and times across methods."""
import glob, os, re, sys
import numpy as np, pandas as pd

prefix = sys.argv[1] if len(sys.argv) > 1 else ""          # "" (4 routes), "p12.", "s60."
here = os.path.dirname(os.path.abspath(__file__))
runs = {}
for f in sorted(glob.glob(f"{here}/trips/*.csv.gz")):
    name = os.path.basename(f)[:-7]
    arena = name.split(".")[0] + "." if "." in name else ""
    if arena != prefix or "ref_aon" in name or re.search(r"_a\d+$", name):   # second algorithm seeds: not a method
        continue
    d = pd.read_csv(f); d = d[d.kind == "AV"]
    runs[name.replace(prefix, "").replace("__screen_s40", "")] = d
names = list(runs)
ref = "tabular_q_port" if "tabular_q_port" in runs else "ref_tabular_iql"
last = max(d.day.max() for d in runs.values()); test_lo = last - 99
print("methods:", names, "| reference:", ref, "| CAVs:", runs[ref].id.nunique(), "| test days from", test_lo)

final, t_test, tables = {}, {}, {}
for n, d in runs.items():
    te = d[d.day >= test_lo]
    final[n] = te.groupby("id").action.agg(lambda s: s.mode()[0])
    t_test[n] = te.groupby("id").travel_time.mean()
    late = d[d.day > 300]                                  # CAV phase: training and test
    tables[n] = late.groupby(["id", "action"]).travel_time.agg(["sum", "size"])
F = pd.DataFrame(final); T = pd.DataFrame(t_test)

def table(exclude=None):
    parts = [t for n, t in tables.items() if n != exclude]
    s = pd.concat(parts).groupby(level=[0, 1]).sum()
    s = s[s["size"] >= 5]
    return (s["sum"] / s["size"]).unstack()

print("\n1. Final route of each CAV, method against method")
print("   all methods on the same route: %.1f%% of CAVs" % (100 * (F.nunique(axis=1) == 1).mean()))
P = table()
best = P.idxmin(axis=1); srt = np.sort(P.values, axis=1); gap = pd.Series(srt[:, 1] - srt[:, 0], index=P.index)
print("   routes with a pooled estimate per CAV:", P.notna().sum(1).value_counts().sort_index().to_dict())
print("   gap best to second-best route, min: median %.2f, quartiles %.2f / %.2f" % (gap.median(), gap.quantile(.25), gap.quantile(.75)))
rows = []
for n in names:
    Pn = table(exclude=n)                                  # times measured under the OTHER methods only
    chosen = pd.Series([Pn.at[i, F.at[i, n]] if F.at[i, n] in Pn.columns else np.nan for i in F.index], index=F.index)
    ok = chosen.notna()
    bn = Pn.min(axis=1)
    rows.append(dict(method=n, t_CAV=T[n].mean(), predicted=chosen[ok].mean(), actual_same_cavs=T[n][ok].mean(),
                     covered=100 * ok.mean(), on_best=100 * (F[n] == best).mean(), same_as_ref=100 * (F[n] == F[ref]).mean(),
                     lost=(chosen - bn)[ok].mean(), oracle=bn.mean()))
R = pd.DataFrame(rows).sort_values("t_CAV")
R["pred_err_%"] = 100 * (R.predicted - R.actual_same_cavs) / R.actual_same_cavs
pd.set_option("display.width", 220)
print("\n2. Per method: time predicted from a table (CAV, route) -> mean time measured in the other methods' runs")
print(R.round(4).to_string(index=False))
c = np.corrcoef(R.predicted, R.actual_same_cavs)[0, 1]
print("   correlation predicted vs actual across methods: %.3f" % c)

print("\n3. Per CAV: where methods disagree with the pooled-best route, how much is at stake")
dis = F.ne(best, axis=0)
for n in R.method:
    m = dis[n]; g = gap[m]
    print("   %-20s off-best CAVs %5.1f%%, of them with gap < 0.1 min: %5.1f%%, median gap %.2f" % (n, 100 * m.mean(), 100 * (g < .1).mean() if len(g) else 0, g.median() if len(g) else 0))

print("\n4. Does a CAV's time on a route depend on which method runs the fleet?")
per = pd.concat({n: (t["sum"] / t["size"])[t["size"] >= 10] for n, t in tables.items()}, axis=1)
per = per[per.notna().sum(1) >= 4]
spread = per.std(axis=1); level = per.mean(axis=1)
print("   (CAV, route) cells measured in 4+ methods: %d; std of the cell mean across methods: median %.3f min = %.1f%% of the time" % (len(per), spread.median(), 100 * (spread / level).median()))
d = runs[ref]; d = d[d.day > 300]
dd = d.groupby(["id", "action"]).travel_time.agg(["std", "size"]); dd = dd[dd["size"] >= 10]
print("   for scale, day-to-day std of one CAV on one route inside one run: median %.3f min" % dd["std"].median())
print("   oracle (every CAV on its pooled-best route): %.4f min; reference %.4f; gap %.2f%%" % (P.min(axis=1).mean(), T[ref].mean(), 100 * (T[ref].mean() - P.min(axis=1).mean()) / T[ref].mean()))
