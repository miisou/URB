"""Shared multiplicative-weights distribution over routes for each OD group. See card.md."""

import numpy as np

from lab.fleet import Fleet, allowed_routes, free_flow_of, od_groups, split_by_shares


class Group:
    def __init__(self, members, free_flow, rng, cfg):
        self.members = members
        self.rng = rng
        self.cfg = cfg
        first = members[0]
        self.allowed = allowed_routes(first, free_flow)
        self.estimate = free_flow_of(first, free_flow)[self.allowed].copy()   # minutes, per allowed route
        self.cumulative = np.zeros(self.allowed.size)
        self.days = 0
        self.fixed = None

    def probabilities(self):
        eta = self.cfg["eta0"] / np.sqrt(self.days + 1.0)
        scores = -eta * (self.cumulative - self.cumulative.min())
        weights = np.exp(scores - scores.max())
        return weights / weights.sum()

    def choose(self, agent_id):
        if self.fixed is not None:
            return self.fixed[agent_id]
        return int(self.allowed[self.rng.choice(self.allowed.size, p=self.probabilities())])

    def end_day(self, choice, times):
        sums = np.zeros(self.allowed.size)
        counts = np.zeros(self.allowed.size)
        for m in self.members:
            if m["id"] in times:
                position = int(np.flatnonzero(self.allowed == choice[m["id"]])[0])
                sums[position] += times[m["id"]]
                counts[position] += 1
        used = counts > 0
        alpha = self.cfg["estimate_ema"]
        self.estimate[used] += alpha * (sums[used] / counts[used] - self.estimate[used])
        self.cumulative += self.estimate
        self.days += 1

    def freeze(self):
        counts = split_by_shares(self.probabilities(), len(self.members))
        routes = [self.allowed[position] for position, count in enumerate(counts) for _ in range(count)]
        self.fixed = {m["id"]: int(route) for m, route in zip(self.members, routes)}


class HedgeFleet(Fleet):
    def __init__(self, ctx):
        rng = np.random.default_rng(ctx["seed"])
        self.groups = [Group(members, ctx["free_flow"], rng, ctx["cfg"]) for members in od_groups(ctx).values()]
        self.group_of = {m["id"]: group for group in self.groups for m in group.members}
        self.choice = {}
        self.times = {}

    def act(self, agent_id, observation):
        self.choice[agent_id] = self.group_of[agent_id].choose(agent_id)
        return self.choice[agent_id]

    def feedback(self, agent_id, reward):
        self.times[agent_id] = -reward

    def end_day(self, day, phase):
        if phase == "train":
            for group in self.groups:
                group.end_day(self.choice, self.times)
        self.choice, self.times = {}, {}

    def start_test(self):
        for group in self.groups:
            group.freeze()


def build(ctx):
    return HedgeFleet(ctx)
