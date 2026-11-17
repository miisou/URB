"""Do routes that differ from the shortest one exist in the road graph, and does the generator offer them?"""
import ast, itertools, sys
import numpy as np, pandas as pd, networkx as nx
import types
sys.modules.setdefault("prettytable", types.SimpleNamespace(PrettyTable=object))   # only used for printing
sys.path.insert(0, sys.argv[1])                       # path to the JanuX checkout
import janux as jx

net, routes_csv, trips = sys.argv[2], sys.argv[3], sys.argv[4]
name = net.rstrip("/").split("/")[-1]
G = jx.build_digraph(f"{net}/{name}.con.xml", f"{net}/{name}.edg.xml", f"{net}/{name}.rou.xml")
attrs = next(iter(G.edges(data=True)))[2]
W = "time" if "time" in attrs else list(attrs)[0]
print("graph:", G.number_of_nodes(), "nodes,", G.number_of_edges(), "links; weight attribute:", W, attrs)

def cost(path, H=G):
    return sum(H[a][b][W] for a, b in zip(path, path[1:]))

def shared(p, q):                                     # share of the shorter route's time spent on common segments
    common = set(p) & set(q)
    tp = sum(G[a][b][W] for a, b in zip(p, p[1:]) if a in common and b in common)
    return tp / max(min(cost(p), cost(q)), 1e-9)

r = pd.read_csv(routes_csv)
d = pd.read_csv(trips); cav = d[(d.kind == "AV") & (d.day == d.day.max())]
size = cav.groupby(["origin", "destination"]).id.nunique()
rows = []
for (o, de), g in r.groupby(["origins", "destinations"]):
    paths = [p.split() for p in g.path]
    if any(n not in G for p in paths for n in p):
        continue
    sp = nx.shortest_path(G, paths[0][0], paths[0][-1], weight=W); c0 = cost(sp)
    gen = sorted(paths, key=cost)
    gen_over = np.median([shared(a, b) for a, b in itertools.combinations(gen, 2)])
    # alternative found by making the shortest route's links three times as slow
    H = G.copy()
    for a, b in zip(sp, sp[1:]):
        H[a][b][W] *= 3
    alt = nx.shortest_path(H, sp[0], sp[-1], weight=W)
    rows.append(dict(o=o, d=de, n_cav=size.get((o, de), 0), t0=c0, gen_best=cost(gen[0]) / c0, gen_worst=cost(gen[-1]) / c0,
                     gen_overlap=gen_over, alt_time=cost(alt) / c0, alt_overlap=shared(sp, alt),
                     min_gen_overlap_with_sp=min(shared(sp, p) for p in gen)))
R = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print("pairs analysed:", len(R), "of", r.groupby(["origins", "destinations"]).ngroups)
q = lambda s: "median %.2f (quartiles %.2f-%.2f)" % (s.median(), s.quantile(.25), s.quantile(.75))
print("shortest route in graph, min:", q(R.t0))
print("generator: best of its 4 relative to the true shortest:", q(R.gen_best))
print("generator: time-weighted overlap between two of its routes:", q(R.gen_overlap))
print("generator: its most different route still shares with the shortest:", q(R.min_gen_overlap_with_sp))
print("alternative that avoids the shortest route: time relative to shortest:", q(R.alt_time))
print("alternative: overlap with the shortest:", q(R.alt_overlap))
ok = (R.alt_overlap < 0.5) & (R.alt_time < 1.25)
print("pairs with an alternative under 50%% overlap and under +25%% time: %.0f%%; weighted by CAVs: %.0f%%" % (100 * ok.mean(), 100 * (ok * R.n_cav).sum() / R.n_cav.sum()))
has = (R.min_gen_overlap_with_sp < 0.5)
print("pairs where the generator already offers a route under 50%% overlap with the shortest: %.0f%%; weighted by CAVs: %.0f%%" % (100 * has.mean(), 100 * (has * R.n_cav).sum() / R.n_cav.sum()))
