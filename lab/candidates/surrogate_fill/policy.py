"""Fitted load model per OD pair and route, solved by filling routes in departure order. See card.md."""

import numpy as np

from lab.fleet import Fleet, allowed_routes, free_flow_of, od_groups


class Group:
    def __init__(self, members, free_flow, rng, cfg):
        self.members, self.rng, self.cfg = members, rng, cfg
        self.allowed = allowed_routes(members[0], free_flow)
        self.free = free_flow_of(members[0], free_flow)
        n = members[0]["n_actions"]
        self.stats = np.zeros((n, 5))                      # per route: days, sum load, sum time, sum load^2, sum load*time
        self.offset = {m["id"]: np.zeros(n) for m in members}   # personal deviation from the pair's model
        self.assignment = {m["id"]: int(np.argmin(self.free)) for m in members}

    def model(self):
        base = self.free.copy()
        slope = np.zeros_like(base)
        for route in self.allowed:
            days, sx, sy, sxx, sxy = self.stats[route]
            if days >= 1:
                base[route] = sy / days
            spread = days * sxx - sx * sx
            if days >= self.cfg["min_fit_days"] and spread > 1e-9:
                slope[route] = max(0.0, (days * sxy - sx * sy) / spread)
                base[route] = (sy - slope[route] * sx) / days
        return base, slope

    def plan(self, explore):
        if explore:
            for m in self.members:
                self.assignment[m["id"]] = int(self.rng.choice(self.allowed))
            return
        base, slope = self.model()
        load = np.zeros_like(base)
        for m in self.members:                              # departure order; each CAV is charged its own time
            cost = np.full(base.size, np.inf)               # plus the delay it adds to those already placed
            for route in self.allowed:
                cost[route] = base[route] + slope[route] * (2 * load[route] + 1) + self.offset[m["id"]][route]
            route = int(np.argmin(cost))
            self.assignment[m["id"]] = route
            load[route] += 1

    def learn(self, times):
        base, slope = self.model()
        load, sums = np.zeros(base.size), np.zeros(base.size)
        for m in self.members:
            if m["id"] in times:
                load[self.assignment[m["id"]]] += 1
                sums[self.assignment[m["id"]]] += times[m["id"]]
        for route in np.flatnonzero(load > 0):
            mean = sums[route] / load[route]
            self.stats[route] += (1, load[route], mean, load[route] ** 2, load[route] * mean)
        alpha = self.cfg["offset_ema"]
        for m in self.members:
            if m["id"] in times:
                route = self.assignment[m["id"]]
                predicted = base[route] + slope[route] * load[route]
                offset = self.offset[m["id"]]
                offset[route] += alpha * (times[m["id"]] - predicted - offset[route])


class SurrogateFleet(Fleet):
    def __init__(self, ctx):
        cfg = ctx["cfg"]
        self.cfg = cfg
        self.rng = np.random.default_rng(ctx["seed"])
        self.groups = [Group(members, ctx["free_flow"], self.rng, cfg) for members in od_groups(ctx).values()]
        self.group_of = {m["id"]: group for group in self.groups for m in group.members}
        self.testing, self.day_started, self.day = False, False, 0
        self.times = {}

    def act(self, agent_id, observation):
        if not self.day_started:
            if not self.testing:
                for group in self.groups:
                    explore = self.day < self.cfg["explore_days"] or self.rng.random() < self.cfg["refresh_explore"]
                    group.plan(explore)
            self.day_started = True
        return self.group_of[agent_id].assignment[agent_id]

    def feedback(self, agent_id, reward):
        self.times[agent_id] = -reward

    def end_day(self, day, phase):
        if phase == "train":
            for group in self.groups:
                group.learn(self.times)
            self.day += 1
        self.times = {}
        self.day_started = False

    def start_test(self):
        for group in self.groups:
            group.plan(False)
        self.testing = True


def build(ctx):
    return SurrogateFleet(ctx)
