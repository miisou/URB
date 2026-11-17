"""Ant-colony routing, version 2: as `pheromone`, but test days are greedy on the final weights. See card.md."""

import numpy as np

from lab.fleet import Fleet, RouteEstimates, od_groups


class PheromoneFleet(Fleet):
    def __init__(self, ctx):
        cfg = ctx["cfg"]
        self.cfg = cfg
        self.estimates = RouteEstimates(ctx, cfg["own_ema"], cfg["pair_ema"])
        self.rng = {info["id"]: np.random.default_rng(ctx["seed"] + info["idx"]) for info in ctx["agents"]}
        self.trail = {}
        for key, members in od_groups(ctx).items():
            free = self.estimates.free[members[0]["id"]]
            self.trail[key] = np.where(np.isfinite(free), 1.0, 0.0)
        self.fixed = None
        self.choice, self.times = {}, {}

    def _weights(self, agent_id):
        estimate = self.estimates.of(agent_id)
        attraction = np.where(np.isfinite(estimate), (estimate.min() / estimate) ** self.cfg["beta"], 0.0)
        return self.trail[self.estimates.pair_of[agent_id]] ** self.cfg["alpha"] * attraction

    def act(self, agent_id, observation):
        if self.fixed is not None:
            return self.fixed[agent_id]
        weights = self._weights(agent_id)
        self.choice[agent_id] = int(self.rng[agent_id].choice(weights.size, p=weights / weights.sum()))
        return self.choice[agent_id]

    def feedback(self, agent_id, reward):
        self.times[agent_id] = -reward

    def end_day(self, day, phase):
        if phase == "train":
            self.estimates.update(self.choice, self.times)
            deposits, members = {}, {}
            for agent_id, time in self.times.items():
                key = self.estimates.pair_of[agent_id]
                best = np.min(self.estimates.of(agent_id))
                deposits.setdefault(key, np.zeros_like(self.trail[key]))[self.choice[agent_id]] += best / time
                members[key] = members.get(key, 0) + 1
            for key, deposit in deposits.items():
                rho = self.cfg["evaporation"]
                self.trail[key] = (1 - rho) * self.trail[key] + rho * deposit / members[key] * deposit.size
                alive = self.trail[key] > 0
                self.trail[key][alive] = np.maximum(self.trail[key][alive], 1e-3)   # never forget a route entirely
        self.choice, self.times = {}, {}

    def start_test(self):
        # v1 drew one route per CAV at random from its weights and kept it. Here each CAV takes the route
        # with the highest weight (trail of its pair times its own attraction); ties go to the faster estimate.
        self.fixed = {}
        for agent_id in self.rng:
            weights = self._weights(agent_id)
            top = np.flatnonzero(weights >= weights.max() * (1 - 1e-12))
            estimate = self.estimates.of(agent_id)
            self.fixed[agent_id] = int(top[np.argmin(estimate[top])])


def build(ctx):
    return PheromoneFleet(ctx)
