"""Minority game, version 2: strategies are scored by whether they picked a less crowded route. See card.md."""

from collections import Counter, deque

import numpy as np

from lab.fleet import Fleet, RouteEstimates, free_flow_of, od_groups, shortest_route


class MinorityFleet(Fleet):
    def __init__(self, ctx):
        cfg = ctx["cfg"]
        self.cfg = cfg
        self.estimates = RouteEstimates(ctx, cfg["own_ema"], cfg["pair_ema"])
        self.memory = int(cfg["memory"])
        groups = od_groups(ctx)
        self.pair_size = {key: len(members) for key, members in groups.items()}
        self.history = {key: (0,) * self.memory for key in groups}       # recent least-used routes of the pair
        self.eligible = {}                                                  # routes within max_detour of the shortest
        for key, members in groups.items():
            times = free_flow_of(members[0], ctx["free_flow"])
            allowed = self.estimates.allowed[members[0]["id"]]
            self.eligible[key] = allowed[times[allowed] <= cfg["max_detour"] * times[allowed].min()]
        self.strategies, self.scores, self.rng, self.recent = {}, {}, {}, {}
        for info in ctx["agents"]:
            agent_id = info["id"]
            key = (info["origin"], info["destination"])
            rng = np.random.default_rng(ctx["seed"] + info["idx"])
            states = info["n_actions"] ** self.memory
            tables = [rng.choice(self.eligible[key], size=states) for _ in range(int(cfg["strategies"]))]
            tables.append(np.full(states, shortest_route(info, ctx["free_flow"])))   # one strategy: always shortest
            self.strategies[agent_id] = np.array(tables)
            self.scores[agent_id] = np.zeros(len(tables))
            self.scores[agent_id][-1] = 1e-6                                      # start on the shortest route
            self.rng[agent_id] = rng
            self.recent[agent_id] = deque(maxlen=int(cfg["freeze_window"]))
        self.n_actions = {info["id"]: info["n_actions"] for info in ctx["agents"]}
        self.fixed = None
        self.choice, self.times, self.state_at_choice = {}, {}, {}

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
        state = self._state(agent_id)
        self.state_at_choice[agent_id] = state          # strategies are scored on the state they acted in
        self.choice[agent_id] = int(self.strategies[agent_id][strategy, state])
        return self.choice[agent_id]

    def feedback(self, agent_id, reward):
        self.times[agent_id] = -reward

    def end_day(self, day, phase):
        if phase == "train":
            self.estimates.update(self.choice, self.times)
            counts = {}
            for agent_id, route in self.choice.items():
                key = self.estimates.pair_of[agent_id]
                counts.setdefault(key, np.zeros(self.n_actions[agent_id]))[route] += 1
            minority = {}
            for key, count in counts.items():
                eligible = self.eligible[key]
                # a route is on the minority side if it carried fewer of the pair's CAVs than the average
                # eligible route today; the pair's history records the least-used eligible route
                minority[key] = np.where(count < count[eligible].mean(), 1.0, -1.0)
                self.history[key] = self.history[key][1:] + (int(eligible[np.argmin(count[eligible])]),)
            for agent_id in self.times:
                key = self.estimates.pair_of[agent_id]
                picks = self.strategies[agent_id][:, self.state_at_choice[agent_id]]
                if self.pair_size[key] >= self.cfg["min_pair"]:
                    self.scores[agent_id] += minority[key][picks]                # minority payoff
                else:                                                            # too few CAVs: no crowd to avoid
                    self.scores[agent_id] -= self.estimates.of(agent_id)[picks]
                self.recent[agent_id].append(self.choice[agent_id])
        self.choice, self.times = {}, {}

    def start_test(self):
        self.fixed = {}
        for agent_id, recent in self.recent.items():     # the route played most often lately
            self.fixed[agent_id] = Counter(recent).most_common(1)[0][0] if recent else int(
                self.strategies[agent_id][-1, 0])


def build(ctx):
    return MinorityFleet(ctx)
