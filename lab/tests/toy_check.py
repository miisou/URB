"""
Local check of lab candidates on a toy congestion model. No SUMO needed.

    python lab/tests/toy_check.py [candidate ...]

It drives each candidate through the same calls as scripts/lab_runner.py (act, feedback, end_day,
start_test) on a made-up model: origin-destination groups with the sizes of the arena's demand file,
four routes each, and a travel time that grows with the number of vehicles on the route.

This checks that the code runs, does not learn or change during testing, and behaves sensibly. The toy
has no shared links between groups and invented parameters, so its numbers say nothing about SUMO.
"""

import csv
import importlib.util
import json
import os
import sys

import numpy as np

LAB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(LAB)
sys.path.insert(0, ROOT)
ARENA = json.load(open(os.path.join(LAB, "arena.json"), encoding="utf-8"))


def make_world(seed, ratio_machines=0.4):
    rng = np.random.default_rng(seed)
    with open(os.path.join(ROOT, "networks", ARENA["network"], "agents.csv"), newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    machine_rows = [rows[i] for i in sorted(rng.choice(len(rows), int(len(rows) * ratio_machines), replace=False))]
    humans = {}
    for row in rows:
        key = (int(row["origin"]), int(row["destination"]))
        humans[key] = humans.get(key, 0) + 1
    for row in machine_rows:
        humans[(int(row["origin"]), int(row["destination"]))] -= 1
    free_flow, capacity, human_split = {}, {}, {}
    for key in humans:
        times = np.sort(rng.uniform(3.0, 6.0, size=4))
        if rng.random() < 0.2:
            times[3] = 1e9                              # some pairs have only three routes
        free_flow[key] = list(times)
        capacity[key] = rng.uniform(4.0, 30.0, size=4)
        weights = np.exp(-1.5 * (times - times.min()))  # frozen humans prefer the short routes
        human_split[key] = weights / weights.sum()
    agents = [{"id": row["id"], "idx": idx, "origin": int(row["origin"]), "destination": int(row["destination"]),
               "start_time": float(row["start_time"]), "n_actions": 4} for idx, row in enumerate(machine_rows)]
    return dict(agents=agents, free_flow=free_flow, capacity=capacity, humans=humans, human_split=human_split)


def simulate_day(world, choices, rng):
    load = {}
    for agent in world["agents"]:
        cell = (agent["origin"], agent["destination"], choices[agent["id"]])
        load[cell] = load.get(cell, 0) + 1
    times = {}
    human_load = {key: rng.multinomial(count, world["human_split"][key]) for key, count in world["humans"].items()}
    for agent in world["agents"]:
        key = (agent["origin"], agent["destination"])
        route = choices[agent["id"]]
        total = load[(key[0], key[1], route)] + human_load[key][route]
        base = world["free_flow"][key][route]
        if base >= 1e8:
            raise RuntimeError(f"agent {agent['id']} chose a route that does not exist")
        times[agent["id"]] = base * (1.0 + 0.6 * (total / world["capacity"][key][route]) ** 2) + rng.normal(0, 0.05)
    return times


def run(name, seed=40, train_days=600, test_days=100):
    folder = os.path.join(LAB, "candidates", name)
    cfg = json.load(open(os.path.join(folder, "config.json"), encoding="utf-8"))
    spec = importlib.util.spec_from_file_location(f"cand_{name}", os.path.join(folder, "policy.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    world = make_world(seed)
    rng = np.random.default_rng(seed + 1000)
    observations = {}
    for agent in world["agents"]:       # as in RouteRL: a vector plus a mask of the routes that exist
        times = np.asarray(world["free_flow"][(agent["origin"], agent["destination"])])
        observations[agent["id"]] = {"observation": np.zeros(7, dtype=np.float32), "action_mask": times < 1e8}
    fleet = module.build({"cfg": cfg, "seed": seed, "agents": world["agents"], "free_flow": world["free_flow"]})
    means, test_choices = {"train": [], "test": []}, []
    for phase, days in (("train", train_days), ("test", test_days)):
        if phase == "test":
            fleet.start_test()
        for day in range(days):
            choices = {agent["id"]: int(fleet.act(agent["id"], observations[agent["id"]])) for agent in world["agents"]}
            times = simulate_day(world, choices, rng)
            if phase == "train":
                for agent_id, time in times.items():
                    fleet.feedback(agent_id, -time)
            else:
                test_choices.append(tuple(choices[agent["id"]] for agent in world["agents"]))
            fleet.end_day(day, phase)
            means[phase].append(float(np.mean(list(times.values()))))
    return dict(train=float(np.mean(means["train"])), first50=float(np.mean(means["train"][:50])),
                test=float(np.mean(means["test"])), fixed_at_test=len(set(test_choices)) == 1)


def aon_reference(seed=40, days=100):
    world = make_world(seed)
    rng = np.random.default_rng(seed + 1000)
    choices = {a["id"]: int(np.argmin(world["free_flow"][(a["origin"], a["destination"])])) for a in world["agents"]}
    return float(np.mean([np.mean(list(simulate_day(world, choices, rng).values())) for _ in range(days)]))


if __name__ == "__main__":
    names = sys.argv[1:] or sorted(
        name for name in os.listdir(os.path.join(LAB, "candidates"))
        if os.path.exists(os.path.join(LAB, "candidates", name, "policy.py")))
    print(f"{'candidate':22} {'test':>7} {'train':>7} {'first 50 days':>14}  same routes on every test day")
    print(f"{'(all-or-nothing)':22} {aon_reference():7.3f}")
    for name in names:
        result = run(name)
        print(f"{name:22} {result['test']:7.3f} {result['train']:7.3f} {result['first50']:14.3f}  {result['fixed_at_test']}")
