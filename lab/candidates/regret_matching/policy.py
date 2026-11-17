"""Regret matching: each CAV plays routes in proportion to its positive cumulative regret. See card.md."""

import numpy as np

from lab.fleet import Fleet, RouteEstimates, shortest_route


class RegretFleet(Fleet):
    def __init__(self, ctx):
        cfg = ctx["cfg"]
        self.cfg = cfg
        self.estimates = RouteEstimates(ctx, cfg["own_ema"], cfg["pair_ema"])
        self.rng = {info["id"]: np.random.default_rng(ctx["seed"] + info["idx"]) for info in ctx["agents"]}
        self.regret = {info["id"]: np.zeros(info["n_actions"]) for info in ctx["agents"]}
        self.route = {info["id"]: shortest_route(info, ctx["free_flow"]) for info in ctx["agents"]}
        self.testing = False
        self.times = {}

    def act(self, agent_id, observation):
        if not self.testing:
            positive = np.maximum(self.regret[agent_id], 0.0)
            total = positive.sum()
            if total > 0:
                self.route[agent_id] = int(self.rng[agent_id].choice(positive.size, p=positive / total))
        return self.route[agent_id]

    def feedback(self, agent_id, reward):
        self.times[agent_id] = -reward

    def end_day(self, day, phase):
        if phase == "train":
            self.estimates.update(self.route, self.times)
            decay = self.cfg["regret_decay"]
            for agent_id, time in self.times.items():
                estimate = self.estimates.of(agent_id)
                gain = time - estimate                      # minutes saved had the CAV taken each other route
                gain[~np.isfinite(gain)] = -np.inf
                gain[self.route[agent_id]] = 0.0
                self.regret[agent_id] = decay * self.regret[agent_id] + gain
        self.times = {}

    def start_test(self):
        for agent_id, regret in self.regret.items():    # settle on the route with the largest regret, if any
            if np.max(regret) > 0:
                self.route[agent_id] = int(np.argmax(regret))
        self.testing = True


def build(ctx):
    return RegretFleet(ctx)
