"""[One line: what this candidate does.] See card.md."""

import numpy as np

from lab.fleet import IndependentFleet, split_obs, valid_actions


class Agent:
    def __init__(self, info, rng, cfg):
        self.n_actions = info["n_actions"]
        self.rng = rng

    def act(self, observation):
        vector, mask = split_obs(observation)
        allowed = valid_actions(self.n_actions, mask)
        self.last_action = int(self.rng.choice(allowed))
        return self.last_action

    def learn(self, reward):
        pass

    def start_test(self):
        pass


def build(ctx):
    cfg, seed = ctx["cfg"], ctx["seed"]
    return IndependentFleet(ctx, lambda info: Agent(info, np.random.default_rng(seed + info["idx"]), cfg))
