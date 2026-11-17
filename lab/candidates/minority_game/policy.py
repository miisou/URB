"""Minority game: each CAV holds a few fixed strategies and plays the one that would have done best. See card.md."""

from collections import Counter, deque

import numpy as np

from lab.fleet import Fleet, RouteEstimates, od_groups, shortest_route


class MinorityFleet(Fleet):
    def __init__(self, ctx):
        cfg = ctx["cfg"]
        self.cfg = cfg
        self.estimates = RouteEstimates(ctx, cfg["own_ema"], cfg["pair_ema"])
        self.memory = int(cfg["memory"])
        self.history = {key: (0,) * self.memory for key in od_groups(ctx)}     # recent fastest routes of the pair
        self.strategies, self.scores, self.allowed, self.rng = {}, {}, {}, {}
        self.recent = {}
        for info in ctx["agents"]:
            agent_id = info["id"]
            rng = np.random.default_rng(ctx["seed"] + info["idx"])
            allowed = self.estimates.allowed[agent_id]
            states = info["n_actions"] ** self.memory
            tables = [rng.choice(allowed, size=states) for _ in range(int(cfg["strategies"]))]
            tables.append(np.full(states, shortest_route(info, ctx["free_flow"])))   # one strategy: always shortest
            self.strategies[agent_id] = np.array(tables)
            self.scores[agent_id] = np.zeros(len(tables))
            self.scores[agent_id][-1] = 1e-6                                      # start on the shortest route
            self.allowed[agent_id], self.rng[agent_id] = allowed, rng
            self.recent[agent_id] = deque(maxlen=int(cfg["freeze_window"]))
        self.n_actions = {info["id"]: info["n_actions"] for info in ctx["agents"]}
        self.fixed = None
        self.choice, self.times = {}, {}

    def _state(self, agent_id):
        state = 0
        for route in self.history[self.estimates.pair_of[agent_id]]:
            state = state * self.n_actions[agent_id] + int(route)
        return state

    def act(self, agent_id, observation):
        if self.fixed is not None:
            return self.fixed[agent_id]
        scores = self.scores[agent_id]
        best = np.flatnonzero(scores == scores.max())
        strategy = int(self.rng[agent_id].choice(best))
        self.choice[agent_id] = int(self.strategies[agent_id][strategy, self._state(agent_id)])
        return self.choice[agent_id]

    def feedback(self, agent_id, reward):
        self.times[agent_id] = -reward

    def end_day(self, day, phase):
        if phase == "train":
            self.estimates.update(self.choice, self.times)
            fastest = {}
            for agent_id in self.times:
                estimate = self.estimates.of(agent_id)
                state = self._state(agent_id)
                self.scores[agent_id] -= estimate[self.strategies[agent_id][:, state]]   # virtual scores
                self.recent[agent_id].append(self.choice[agent_id])
                fastest.setdefault(self.estimates.pair_of[agent_id], int(np.argmin(estimate)))
            for key, route in fastest.items():
                self.history[key] = self.history[key][1:] + (route,)
        self.choice, self.times = {}, {}

    def start_test(self):
        self.fixed = {}
        for agent_id, recent in self.recent.items():     # the route played most often lately
            self.fixed[agent_id] = Counter(recent).most_common(1)[0][0] if recent else int(self.allowed[agent_id][0])


def build(ctx):
    return MinorityFleet(ctx)
