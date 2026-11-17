"""Port of scripts/iql_tabular.py::TabularQ to the lab interface. See card.md."""

import numpy as np

from lab.fleet import IndependentFleet, split_obs, valid_actions


class TabularQAgent:
    def __init__(self, n_actions, rng, cfg):
        self.n_actions = n_actions
        self.rng = rng
        self.bin_width = float(cfg["bin_width"])
        self.epsilon = float(cfg["eps_init"])
        self.eps_decay = float(cfg["eps_decay"])
        self.eps_min = float(cfg["eps_min"])
        self.lr = float(cfg["lr"])
        self.q_table = {}

    def act(self, observation):
        vector, mask = split_obs(observation)
        allowed = valid_actions(self.n_actions, mask)
        key = tuple(np.floor(vector / self.bin_width).astype(np.int64))
        q_values = self.q_table.setdefault(key, np.zeros(self.n_actions, dtype=np.float64))
        if self.rng.random() < self.epsilon:
            action = int(self.rng.choice(allowed))
        else:
            best = np.max(q_values[allowed])
            action = int(self.rng.choice(allowed[q_values[allowed] == best]))
        self.last = (key, action)
        return action

    def learn(self, reward):
        key, action = self.last
        q_values = self.q_table[key]
        q_values[action] += self.lr * (reward - q_values[action])
        self.epsilon = max(self.eps_min, self.epsilon * self.eps_decay)

    def start_test(self):
        self.epsilon = 0.0


def build(ctx):
    cfg, seed = ctx["cfg"], ctx["seed"]
    return IndependentFleet(
        ctx,
        lambda info: TabularQAgent(info["n_actions"], np.random.default_rng(seed + info["idx"]), cfg),
    )
