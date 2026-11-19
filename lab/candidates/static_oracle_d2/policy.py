"""Diagnostic: every CAV drives a fixed route read from config.json, with no learning. See card.md."""

from lab.fleet import Fleet, shortest_route


class FixedFleet(Fleet):
    def __init__(self, ctx):
        table = ctx["cfg"]["assignment"]
        self.route = {}
        missing = 0
        for info in ctx["agents"]:
            key = str(info["id"])
            if key in table:
                self.route[info["id"]] = int(table[key])
            else:
                missing += 1
                self.route[info["id"]] = shortest_route(info, ctx["free_flow"])
        print(f"static_oracle: {len(self.route) - missing} CAVs from the table, {missing} on the shortest route")

    def act(self, agent_id, observation):
        return self.route[agent_id]


def build(ctx):
    return FixedFleet(ctx)
