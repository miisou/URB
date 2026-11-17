"""Log-linear learning with a cooling temperature (simulated annealing over route choices). See card.md."""

import numpy as np

from lab.fleet import Fleet, RouteEstimates, shortest_route


class AnnealedFleet(Fleet):
    def __init__(self, ctx):
        cfg = ctx["cfg"]
        self.cfg = cfg
        self.rng = np.random.default_rng(ctx["seed"])
        self.estimates = RouteEstimates(ctx, cfg["own_ema"], cfg["pair_ema"])
        self.route = {info["id"]: shortest_route(info, ctx["free_flow"]) for info in ctx["agents"]}
        self.ids = [info["id"] for info in ctx["agents"]]
        self.total_days = int(cfg["training_eps"])
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
            progress = min(1.0, self.day / max(1, self.total_days - 1))
            temperature = self.cfg["temp_start"] * (self.cfg["temp_end"] / self.cfg["temp_start"]) ** progress
            for agent_id in self.ids:
                if self.rng.random() < self.cfg["revision_rate"]:
                    estimate = self.estimates.of(agent_id)
                    scores = -(estimate - estimate.min()) / temperature
                    weights = np.exp(scores)
                    self.route[agent_id] = int(self.rng.choice(weights.size, p=weights / weights.sum()))
        self.times = {}

    def start_test(self):
        for agent_id in self.ids:                     # end cold: every CAV settles on its best estimate
            self.route[agent_id] = int(np.argmin(self.estimates.of(agent_id)))


def build(ctx):
    return AnnealedFleet(ctx)
