# Lab memory

What has been learned while running experiments on URB, kept so that the next idea starts from it.
Read this folder before designing a new method; update it when a run changes what is known.

| File | Holds |
| --- | --- |
| [system.md](system.md) | How the environment actually works, checked in the code: decisions, observation, reward, humans, routes, metrics |
| [benchmark_pitfalls.md](benchmark_pitfalls.md) | Where the leaderboard number does not mean what it seems to mean |
| [findings.md](findings.md) | Measured results, each with its number, its evidence, and how far it can be trusted |
| [idea_map.md](idea_map.md) | Every method idea: tried or not, outcome, and why; plus the design lessons drawn from them |
| [open_questions.md](open_questions.md) | Where improvement is still possible and what would test it |
| [ops.md](ops.md) | Running things on the cluster: timings, failures met, how they were fixed |
| [literature.md](literature.md) | Published work on URB and neighbouring benchmarks: what is compared, measured, and counted as new |

## Rules for entries

- **Say how it is known.** Each claim is one of: *read in code*, *measured* (with the run or script), *inferred*.
  Inferences are labelled as such and say what would confirm them.
- **Give the scope.** Network, CAV share, number of routes, seeds. Most results here are one seed on one network.
- **Date every finding.** Upstream changes; a finding ties to the revision it was made on (currently `5457dcf`).
- **Correct, do not append.** When a later run overturns an entry, rewrite the entry and note what changed.
- **Keep failed ideas.** A dropped idea with its reason is worth more than a blank.
- **No personal identifiers.** No logins, hosts, or names of people outside what the upstream repository already shows.
