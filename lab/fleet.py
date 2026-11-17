"""
Interface between the lab runner (scripts/lab_runner.py) and a candidate method.

A candidate lives in lab/candidates/<name>/policy.py and defines

    def build(ctx) -> Fleet

`ctx` is a dict:
    cfg        : the candidate's config.json (a dict)
    seed       : algorithm seed (int)
    agents     : list of dicts, one per CAV, in the order of env.machine_agents:
                 {"id": str, "idx": int, "origin": ..., "destination": ..., "start_time": ..., "n_actions": int}
    free_flow  : {(origin, destination): [free-flow travel time of each route]}

Every day each CAV makes one decision. The runner calls, in this order:
    fleet.act(agent_id, observation)  -> route index      (once per CAV)
    fleet.feedback(agent_id, reward)                      (once per CAV, training days only)
    fleet.end_day(day, phase)                             (phase is "train" or "test")
and `fleet.start_test()` once, before the first test day. Test days must not learn or explore.

The reward is the one RouteRL computes for the task's CAV behaviour; for selfish CAVs it is minus the
agent's own travel time.
"""

import numpy as np


def split_obs(observation):
    """Return (vector, mask). `mask` is a boolean array of allowed routes or None."""
    mask = None
    if isinstance(observation, dict):
        mask = observation.get("action_mask")
        observation = observation["observation"]
    vector = np.asarray(observation, dtype=np.float64).reshape(-1)
    if mask is not None:
        mask = np.asarray(mask, dtype=bool).reshape(-1)
    return vector, mask


def valid_actions(n_actions, mask):
    if mask is None:
        return np.arange(n_actions)
    allowed = np.flatnonzero(mask)
    if allowed.size == 0:
        raise ValueError("Action mask must allow at least one action")
    return allowed


INVALID_TIME = 1e8   # free-flow entries at or above this mark a route that does not exist for the pair


def free_flow_of(info, free_flow):
    """Free-flow travel times of the agent's routes, in the unit RouteRL reports (minutes)."""
    return np.asarray(free_flow[(info["origin"], info["destination"])], dtype=np.float64)[: info["n_actions"]]


def allowed_routes(info, free_flow):
    times = free_flow_of(info, free_flow)
    allowed = np.flatnonzero(times < INVALID_TIME)
    return allowed if allowed.size else np.arange(info["n_actions"])


def shortest_route(info, free_flow):
    """The all-or-nothing choice: the route with the shortest free-flow time."""
    return int(np.argmin(free_flow_of(info, free_flow)))


def od_groups(ctx):
    """{(origin, destination): [agent infos sorted by start time]} for the CAVs of the fleet."""
    groups = {}
    for info in ctx["agents"]:
        groups.setdefault((info["origin"], info["destination"]), []).append(info)
    for members in groups.values():
        members.sort(key=lambda item: (item["start_time"], item["idx"]))
    return groups


def split_by_shares(shares, count):
    """Split `count` agents over routes in proportion to `shares` (largest remainder)."""
    shares = np.asarray(shares, dtype=np.float64)
    shares = shares / shares.sum()
    exact = shares * count
    counts = np.floor(exact).astype(int)
    for route in np.argsort(-(exact - counts))[: count - counts.sum()]:
        counts[route] += 1
    return counts


class Fleet:
    """Base class. A fleet-level method (one controller for all CAVs) overrides these directly."""

    def act(self, agent_id, observation):
        raise NotImplementedError

    def feedback(self, agent_id, reward):
        pass

    def end_day(self, day, phase):
        pass

    def start_test(self):
        pass


class IndependentFleet(Fleet):
    """
    One independent learner per CAV. `make_agent(agent_info)` returns an object with
        act(observation) -> int, learn(reward), start_test()
    """

    def __init__(self, ctx, make_agent):
        self.agents = {info["id"]: make_agent(info) for info in ctx["agents"]}

    def act(self, agent_id, observation):
        return self.agents[agent_id].act(observation)

    def feedback(self, agent_id, reward):
        self.agents[agent_id].learn(reward)

    def start_test(self):
        for agent in self.agents.values():
            agent.start_test()


class RouteEstimates:
    """
    Travel-time estimates per CAV and route, in minutes. For a route the CAV has driven it is a running
    mean of its own times; otherwise the running mean of its OD pair's times on that route; otherwise the
    free-flow time. Free-flow times are optimistic, so untried routes look attractive until tried.
    Routes that do not exist are +inf.
    """

    def __init__(self, ctx, own_ema=0.2, pair_ema=0.2):
        self.own_ema, self.pair_ema = own_ema, pair_ema
        self.free, self.own, self.pair_of, self.allowed = {}, {}, {}, {}
        self.shared = {}
        for info in ctx["agents"]:
            key = (info["origin"], info["destination"])
            times = free_flow_of(info, ctx["free_flow"])
            self.free[info["id"]] = np.where(times < INVALID_TIME, times, np.inf)
            self.own[info["id"]] = np.full(info["n_actions"], np.nan)
            self.pair_of[info["id"]] = key
            self.allowed[info["id"]] = allowed_routes(info, ctx["free_flow"])
            self.shared.setdefault(key, np.full(info["n_actions"], np.nan))

    def update(self, choices, times):
        sums, counts = {}, {}
        for agent_id, time in times.items():
            route = choices[agent_id]
            own = self.own[agent_id]
            own[route] = time if np.isnan(own[route]) else own[route] + self.own_ema * (time - own[route])
            cell = (self.pair_of[agent_id], route)
            sums[cell] = sums.get(cell, 0.0) + time
            counts[cell] = counts.get(cell, 0) + 1
        self.today = {cell: sums[cell] / counts[cell] for cell in sums}      # pair-route means of the day
        for (key, route), value in self.today.items():
            shared = self.shared[key]
            shared[route] = value if np.isnan(shared[route]) else shared[route] + self.pair_ema * (value - shared[route])

    def of(self, agent_id):
        estimate = self.own[agent_id].copy()
        missing = np.isnan(estimate)
        estimate[missing] = self.shared[self.pair_of[agent_id]][missing]
        missing = np.isnan(estimate)
        estimate[missing] = self.free[agent_id][missing]
        estimate[np.isinf(self.free[agent_id])] = np.inf
        return estimate
