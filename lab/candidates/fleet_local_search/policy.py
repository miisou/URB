"""Local search over the fleet's joint route assignment, one move per OD group. See card.md."""

import numpy as np

from lab.fleet import Fleet, allowed_routes, od_groups, shortest_route


class Group:
    def __init__(self, members, free_flow, rng, cfg):
        self.members = members
        self.rng = rng
        self.cfg = cfg
        self.allowed = {m["id"]: allowed_routes(m, free_flow) for m in members}
        self.assignment = {m["id"]: shortest_route(m, free_flow) for m in members}
        self.movable = [m["id"] for m in members if self.allowed[m["id"]].size > 1]
        self.mean = None            # running mean of the group's cost under the current assignment
        self.var = 0.0
        self.baseline_days = 0
        self.proposal = None        # (agent id, route)
        self.wins = 0
        self.accepted = 0

    def start_day(self, proposal_day):
        self.today = dict(self.assignment)
        self.is_proposal = False
        ready = self.baseline_days >= self.cfg["min_baseline_days"]
        if proposal_day and ready and self.movable:
            if self.proposal is None:
                agent_id = self.movable[int(self.rng.integers(len(self.movable)))]
                options = [r for r in self.allowed[agent_id] if r != self.assignment[agent_id]]
                self.proposal = (agent_id, int(options[int(self.rng.integers(len(options)))]))
                self.wins = 0
            agent_id, route = self.proposal
            self.today[agent_id] = route
            self.is_proposal = True

    def end_day(self, times):
        cost = float(np.mean([times[m["id"]] for m in self.members if m["id"] in times]))
        if not self.is_proposal:
            if self.mean is None:
                self.mean = cost
            else:
                alpha = self.cfg["cost_ema"]
                deviation = cost - self.mean
                self.mean += alpha * deviation
                self.var = (1 - alpha) * (self.var + alpha * deviation * deviation)
            self.baseline_days += 1
            return
        if cost < self.mean - self.cfg["z"] * np.sqrt(self.var):
            self.wins += 1
            if self.wins >= self.cfg["confirmations"]:
                agent_id, route = self.proposal
                self.assignment[agent_id] = route
                self.accepted += 1
                self.proposal = None
                self.mean, self.var, self.baseline_days = cost, 0.0, 0   # re-estimate the new assignment
        else:
            self.proposal = None


class LocalSearchFleet(Fleet):
    def __init__(self, ctx):
        cfg = ctx["cfg"]
        rng = np.random.default_rng(ctx["seed"])
        self.groups = [Group(members, ctx["free_flow"], rng, cfg) for members in od_groups(ctx).values()]
        self.group_of = {m["id"]: group for group in self.groups for m in group.members}
        self.testing = False
        self.day_started = False
        self.day_index = 0
        self.times = {}

    def _start_day(self):
        proposal_day = (not self.testing) and self.day_index % 2 == 1
        for group in self.groups:
            group.start_day(proposal_day)
        self.times = {}
        self.day_started = True

    def act(self, agent_id, observation):
        if not self.day_started:
            self._start_day()
        return self.group_of[agent_id].today[agent_id]

    def feedback(self, agent_id, reward):
        self.times[agent_id] = -reward

    def end_day(self, day, phase):
        if phase == "train":
            for group in self.groups:
                group.end_day(self.times)
        self.day_index += 1
        self.day_started = False

    def start_test(self):
        self.testing = True


def build(ctx):
    return LocalSearchFleet(ctx)
