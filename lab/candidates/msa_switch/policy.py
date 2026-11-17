"""Method of successive averages: a shrinking share of CAVs moves to its currently best route. See card.md."""

import numpy as np

from lab.fleet import Fleet, RouteEstimates, shortest_route


class MsaFleet(Fleet):
    def __init__(self, ctx):
        cfg = ctx["cfg"]
        self.cfg = cfg
        self.rng = np.random.default_rng(ctx["seed"])
        self.estimates = RouteEstimates(ctx, cfg["own_ema"], cfg["pair_ema"])
        self.route = {info["id"]: shortest_route(info, ctx["free_flow"]) for info in ctx["agents"]}
        self.ids = [info["id"] for info in ctx["agents"]]
        self.day = 0
        self.times = {}

    def act(self, agent_id, observation):
        return self.route[agent_id]

    def feedback(self, agent_id, reward):
        self.times[agent_id] = -reward

    def end_day(self, day, phase):
        if phase == "train":
            self.estimates.update(self.route, self.times)
            self.day += 1
            step = 1.0 / (1.0 + self.day / self.cfg["step_scale"])
            for agent_id in self.ids:
                if self.rng.random() < step:
                    self.route[agent_id] = int(np.argmin(self.estimates.of(agent_id)))
        self.times = {}


def build(ctx):
    return MsaFleet(ctx)
