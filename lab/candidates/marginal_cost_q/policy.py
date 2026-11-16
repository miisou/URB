"""Reference value learner trained on an estimated marginal cost to the fleet. See card.md."""

import numpy as np

from lab.fleet import Fleet, allowed_routes, od_groups


class SlopeFit:
    """Online least squares of a route's mean travel time on the number of fleet CAVs using it."""

    def __init__(self):
        self.n = 0
        self.sx = self.sy = self.sxx = self.sxy = 0.0

    def add(self, load, time):
        self.n += 1
        self.sx += load
        self.sy += time
        self.sxx += load * load
        self.sxy += load * time

    def slope(self, min_days):
        if self.n < min_days:
            return 0.0
        spread = self.n * self.sxx - self.sx * self.sx
        if spread <= 1e-9:
            return 0.0
        return max(0.0, (self.n * self.sxy - self.sx * self.sy) / spread)


class MarginalCostFleet(Fleet):
    def __init__(self, ctx):
        cfg = ctx["cfg"]
        self.cfg = cfg
        self.epsilon = float(cfg["eps_init"])
        self.testing = False
        self.rng = {}
        self.q = {}
        self.allowed = {}
        self.group_key = {}
        for key, members in od_groups(ctx).items():
            for m in members:
                self.rng[m["id"]] = np.random.default_rng(ctx["seed"] + m["idx"])
                self.q[m["id"]] = np.zeros(m["n_actions"], dtype=np.float64)
                self.allowed[m["id"]] = allowed_routes(m, ctx["free_flow"])
                self.group_key[m["id"]] = key
        self.fits = {}
        self.choice = {}
        self.times = {}

    def act(self, agent_id, observation):
        rng, allowed, q = self.rng[agent_id], self.allowed[agent_id], self.q[agent_id]
        if not self.testing and rng.random() < self.epsilon:
            action = int(rng.choice(allowed))
        else:
            best = np.max(q[allowed])
            action = int(rng.choice(allowed[q[allowed] == best]))
        self.choice[agent_id] = action
        return action

    def feedback(self, agent_id, reward):
        self.times[agent_id] = -reward

    def end_day(self, day, phase):
        if phase == "train":
            loads, sums = {}, {}
            for agent_id, time in self.times.items():
                cell = (self.group_key[agent_id], self.choice[agent_id])
                loads[cell] = loads.get(cell, 0) + 1
                sums[cell] = sums.get(cell, 0.0) + time
            for cell, load in loads.items():
                self.fits.setdefault(cell, SlopeFit()).add(load, sums[cell] / load)
            lr = float(self.cfg["lr"])
            for agent_id, time in self.times.items():
                cell = (self.group_key[agent_id], self.choice[agent_id])
                slope = self.fits[cell].slope(self.cfg["min_fit_days"])
                signal = -(time + slope * (loads[cell] - 1))
                q = self.q[agent_id]
                q[self.choice[agent_id]] += lr * (signal - q[self.choice[agent_id]])
            self.epsilon = max(float(self.cfg["eps_min"]), self.epsilon * float(self.cfg["eps_decay"]))
        self.choice, self.times = {}, {}

    def start_test(self):
        self.testing = True


def build(ctx):
    return MarginalCostFleet(ctx)
