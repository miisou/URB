"""Proportional feedback controller of route shares for each OD group. See card.md."""

import numpy as np

from lab.fleet import Fleet, allowed_routes, free_flow_of, od_groups, split_by_shares


class Group:
    def __init__(self, members, free_flow, cfg):
        self.members = members
        self.cfg = cfg
        first = members[0]
        self.allowed = allowed_routes(first, free_flow)
        self.estimate = free_flow_of(first, free_flow)[self.allowed].copy()   # minutes, per allowed route
        self.shares = np.zeros(self.allowed.size)
        self.shares[int(np.argmin(self.estimate))] = 1.0                      # start: all-or-nothing
        self.shares = 0.9 * self.shares + 0.1 / self.allowed.size
        self.position = {}                                                    # agent id -> index into allowed
        self.last_shift = 0.0

    def start_day(self):
        counts = split_by_shares(self.shares, len(self.members))
        remaining = counts.copy()
        assignment, unplaced = {}, []
        for m in self.members:                       # keep yesterday's route where the split allows
            previous = self.position.get(m["id"])
            if previous is not None and remaining[previous] > 0:
                assignment[m["id"]] = previous
                remaining[previous] -= 1
            else:
                unplaced.append(m["id"])
        free = [position for position, count in enumerate(remaining) for _ in range(count)]
        for agent_id, position in zip(unplaced, free):
            assignment[agent_id] = position
        self.position = assignment

    def route(self, agent_id):
        return int(self.allowed[self.position[agent_id]])

    def end_day(self, times):
        sums = np.zeros(self.allowed.size)
        counts = np.zeros(self.allowed.size)
        for m in self.members:
            if m["id"] in times:
                sums[self.position[m["id"]]] += times[m["id"]]
                counts[self.position[m["id"]]] += 1
        used = counts > 0
        alpha = self.cfg["estimate_ema"]
        self.estimate[used] += alpha * (sums[used] / counts[used] - self.estimate[used])
        mean = float(np.dot(self.shares, self.estimate))
        updated = self.shares * np.exp(-self.cfg["gain"] * (self.estimate - mean) / mean)
        updated /= updated.sum()
        self.last_shift = float(np.abs(updated - self.shares).sum())
        self.shares = updated


class ShareControllerFleet(Fleet):
    def __init__(self, ctx):
        self.groups = [Group(members, ctx["free_flow"], ctx["cfg"]) for members in od_groups(ctx).values()]
        self.group_of = {m["id"]: group for group in self.groups for m in group.members}
        self.testing = False
        self.day_started = False
        self.times = {}

    def act(self, agent_id, observation):
        if not self.day_started:
            if not self.testing:
                for group in self.groups:
                    group.start_day()
            self.day_started = True
        return self.group_of[agent_id].route(agent_id)

    def feedback(self, agent_id, reward):
        self.times[agent_id] = -reward

    def end_day(self, day, phase):
        if phase == "train":
            for group in self.groups:
                group.end_day(self.times)
        self.times = {}
        self.day_started = False

    def start_test(self):
        for group in self.groups:        # the split of the last training day is kept for testing
            if not group.position:
                group.start_day()
        self.testing = True
        shifts = [group.last_shift for group in self.groups if len(group.members) >= 5]
        if shifts:
            print(f"share_controller: mean share shift on the last training day, groups of 5+: {np.mean(shifts):.4f}")


def build(ctx):
    return ShareControllerFleet(ctx)
