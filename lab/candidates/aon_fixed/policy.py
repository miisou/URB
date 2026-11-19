"""All-or-nothing on the lab runner: every CAV on its shortest free-flow route every day. See card.md."""

from lab.fleet import Fleet, shortest_route


class ShortestFleet(Fleet):
    def __init__(self, ctx):
        self.route = {info["id"]: shortest_route(info, ctx["free_flow"]) for info in ctx["agents"]}

    def act(self, agent_id, observation):
        return self.route[agent_id]


def build(ctx):
    return ShortestFleet(ctx)
