#!/usr/bin/env python3
"""
Control script of the lab: from a candidate card to a row in lab/LEADERBOARD.md.

    python lab/labctl.py new <name>                       scaffold lab/candidates/<name>/
    python lab/labctl.py submit <name> --stage smoke|screen|confirm [--seeds 43 44]
    python lab/labctl.py status                           refresh job states in lab/ledger.csv
    python lab/labctl.py collect                          fetch finished runs, then rebuild the table
    python lab/labctl.py table                            rebuild lab/LEADERBOARD.md from lab/runs/
    python lab/labctl.py adopt <dir> <name> --stage S --seed N [--note TEXT]
                                                          register a run made outside the lab

Only the Python standard library is used. Cluster commands go through `ssh`; the VPN must be on.
See lab/README.md for the rules of the loop.
"""

import argparse
import csv
import datetime
import json
import math
import os
import shutil
import subprocess
import sys

LAB = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(LAB)
ARENA = json.load(open(os.path.join(LAB, "arena.json"), encoding="utf-8"))
CL = ARENA["cluster"]
# The login is kept out of the repository: lab/cluster.local.json {"host": "user@gateway"} or URB_LAB_HOST.
_local = os.path.join(LAB, "cluster.local.json")
CL["host"] = os.environ.get("URB_LAB_HOST") or (
    json.load(open(_local, encoding="utf-8"))["host"] if os.path.exists(_local) else None)
LEDGER = os.path.join(LAB, "ledger.csv")
FIELDS = ["run_id", "candidate", "stage", "seed", "job_id", "submitted", "status", "note"]
STAGES = ["smoke", "screen", "confirm"]


# ---------------------------------------------------------------- ledger and files

def read_ledger():
    if not os.path.exists(LEDGER):
        return []
    with open(LEDGER, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_ledger(rows):
    with open(LEDGER, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def candidate_dir(name):
    return os.path.join(LAB, "candidates", name)


def load_candidate(name):
    path = os.path.join(candidate_dir(name), "candidate.json")
    if not os.path.exists(path):
        sys.exit(f"No candidate '{name}' (expected {path})")
    return json.load(open(path, encoding="utf-8"))


def run_id_of(name, stage, seed):
    return f"{name}__{stage}_s{seed}"


def metrics_of(run_id):
    path = os.path.join(LAB, "runs", run_id, "BenchmarkMetrics.csv")
    if not os.path.exists(path):
        return None
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return None
    out = {}
    for key, value in rows[0].items():
        try:
            out[key] = float(value)
        except (TypeError, ValueError):
            out[key] = float("nan")
    return out


# ---------------------------------------------------------------- cluster

def ssh(command, stdin=None, timeout=180):
    if not CL["host"]:
        sys.exit('No cluster login: set URB_LAB_HOST or create lab/cluster.local.json {"host": "user@gateway"}.')
    full = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", CL["host"], command]
    try:
        result = subprocess.run(full, stdin=stdin, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        sys.exit("ssh timed out. Check the VPN and try again; nothing was changed by this step.")
    if result.returncode != 0 and ("resolve" in result.stderr or "timed out" in result.stderr):
        sys.exit("Cluster not reachable: the VPN is off. Reconnect it and repeat the command.")
    return result


def sync():
    """Send the code the runs need. lab/runs/ on the cluster is never overwritten."""
    paths = ["scripts", "config", "analysis", "baseline_models", f"networks/{ARENA['network']}",
             "requirements.txt", "lab/fleet.py", "lab/arena.json", "lab/candidates", "lab/cluster"]
    remote = (f"mkdir -p ~/{CL['remote_dir']} && tar xzf - -C ~/{CL['remote_dir']} && cd ~/{CL['remote_dir']} && "
              "sed -i 's/\\r$//' lab/cluster/*.sh lab/cluster/cmds/*.sh 2>/dev/null; mkdir -p lab/logs lab/runs")
    tar = subprocess.Popen(["tar", "czf", "-"] + paths, cwd=ROOT, stdout=subprocess.PIPE)
    result = ssh(remote, stdin=tar.stdout)
    tar.stdout.close()
    if tar.wait() != 0 or result.returncode != 0:
        sys.exit(f"sync failed: {result.stderr.strip()}")


def build_command(name, cand, stage, seed, run_id):
    values = dict(id=run_id, seed=seed, env_conf=ARENA["env_conf"], task_conf=ARENA["task_conf"],
                  network=ARENA["network"])
    if cand["kind"] == "lab":
        command = ("python -u scripts/lab_runner.py --id {id} --candidate " + name +
                   " --env-conf {env_conf} --task-conf {task_conf} --net {network}"
                   " --env-seed {seed} --torch-seed {seed}").format(**values)
        if stage == "smoke":
            command += " --smoke"
        return command
    if stage == "smoke":
        sys.exit(f"'{name}' runs an existing script; it has no smoke stage.")
    return cand["command"].format(**values)


# ---------------------------------------------------------------- commands

def cmd_new(args):
    target = candidate_dir(args.name)
    if os.path.exists(target):
        sys.exit(f"{target} already exists")
    os.makedirs(target)
    for filename in ("card.md", "policy.py", "config.json", "candidate.json"):
        text = open(os.path.join(LAB, "templates", filename), encoding="utf-8").read()
        with open(os.path.join(target, filename), "w", encoding="utf-8", newline="\n") as f:
            f.write(text.replace("{name}", args.name))
    print(f"Created {target}. Fill in card.md first, then policy.py and config.json.")


def cmd_submit(args):
    cand = load_candidate(args.name)
    card = os.path.join(candidate_dir(args.name), "card.md")
    if "[" in open(card, encoding="utf-8").read().split("\n", 1)[1] and cand.get("role") == "candidate":
        sys.exit(f"{card} still has unfilled [placeholders]. The card comes before the run.")
    seeds = args.seeds or ARENA["seeds"][args.stage]
    ledger = read_ledger()
    active = {row["run_id"] for row in ledger if row["status"] in ("submitted", "running", "done")}
    todo = []
    for seed in seeds:
        run_id = run_id_of(args.name, args.stage, seed)
        if run_id in active:
            print(f"skip {run_id}: already {next(r['status'] for r in ledger if r['run_id'] == run_id)}")
            continue
        todo.append((seed, run_id))
    if not todo:
        return
    queued = ssh("squeue -h -u $USER -n urb-lab | wc -l").stdout.strip()
    if queued.isdigit() and int(queued) + len(todo) > CL["max_parallel"]:
        sys.exit(f"{queued} lab jobs are already queued; {len(todo)} more would exceed max_parallel="
                 f"{CL['max_parallel']}.")
    os.makedirs(os.path.join(LAB, "cluster", "cmds"), exist_ok=True)
    for seed, run_id in todo:
        with open(os.path.join(LAB, "cluster", "cmds", run_id + ".sh"), "w", encoding="utf-8", newline="\n") as f:
            f.write(build_command(args.name, cand, args.stage, seed, run_id) + "\n")
    sync()
    for seed, run_id in todo:
        sbatch = (f"cd ~/{CL['remote_dir']} && sbatch --parsable -p {CL['partition']} --qos={CL['qos']} "
                  f"--cpus-per-task={CL['cpus']} --mem={CL['mem']} --time={CL['time'][args.stage]} "
                  f"--output=lab/logs/slurm-%j.out lab/cluster/run_one.sh {run_id}")
        result = ssh(sbatch)
        job_id = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
        if result.returncode != 0 or not job_id.isdigit():
            sys.exit(f"sbatch failed for {run_id}: {result.stderr.strip() or result.stdout.strip()}")
        ledger = [row for row in ledger if row["run_id"] != run_id]
        ledger.append(dict(run_id=run_id, candidate=args.name, stage=args.stage, seed=seed, job_id=job_id,
                           submitted=datetime.datetime.now().isoformat(timespec="minutes"),
                           status="submitted", note=""))
        write_ledger(ledger)
        print(f"submitted {run_id} as job {job_id}")


def refresh_states(ledger):
    open_rows = [row for row in ledger if row["status"] in ("submitted", "running") and row["job_id"].isdigit()]
    if not open_rows:
        return
    jobs = ",".join(row["job_id"] for row in open_rows)
    result = ssh(f"sacct -n -X -P -j {jobs} -o JobID,State")
    states = dict(line.split("|")[:2] for line in result.stdout.splitlines() if "|" in line)
    for row in open_rows:
        state = states.get(row["job_id"], "").split()[0] if states.get(row["job_id"]) else ""
        if state in ("PENDING",):
            row["status"] = "submitted"
        elif state in ("RUNNING", "COMPLETING"):
            row["status"] = "running"
        elif state == "COMPLETED":
            row["status"] = "finished"      # becomes "done" once its metrics are collected
        elif state:
            row["status"] = "failed"
            row["note"] = (row["note"] + " " + state).strip()


def cmd_status(args):
    ledger = read_ledger()
    refresh_states(ledger)
    write_ledger(ledger)
    for row in ledger:
        if row["status"] != "done":
            print(f"{row['run_id']:44} job {row['job_id']:>8}  {row['status']}  {row['note']}")
    print(f"{sum(row['status'] == 'done' for row in ledger)} runs done, {len(ledger)} in the ledger")


def cmd_collect(args):
    ledger = read_ledger()
    refresh_states(ledger)
    remote = f"cd ~/{CL['remote_dir']}/lab && tar czf - runs 2>/dev/null"
    fetch = subprocess.Popen(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", CL["host"], remote],
                             stdout=subprocess.PIPE)
    unpack = subprocess.run(["tar", "xzf", "-"], cwd=LAB, stdin=fetch.stdout)
    fetch.stdout.close()
    if fetch.wait() != 0 or unpack.returncode != 0:
        print("warning: could not fetch lab/runs from the cluster (VPN off, or nothing there yet)")
    for row in ledger:
        if row["status"] in ("finished", "running", "submitted", "failed") and metrics_of(row["run_id"]):
            row["status"] = "done"
        elif row["status"] == "finished":
            row["status"] = "failed"
            row["note"] = (row["note"] + " no metrics file").strip()
    write_ledger(ledger)
    cmd_table(args)


def cmd_adopt(args):
    run_id = run_id_of(args.name, args.stage, args.seed)
    load_candidate(args.name)
    target = os.path.join(LAB, "runs", run_id)
    os.makedirs(target, exist_ok=True)
    shutil.copy(os.path.join(args.dir, "exp_config.json"), target)
    shutil.copy(os.path.join(args.dir, "metrics", "BenchmarkMetrics.csv"), target)
    ledger = [row for row in read_ledger() if row["run_id"] != run_id]
    ledger.append(dict(run_id=run_id, candidate=args.name, stage=args.stage, seed=args.seed, job_id="",
                       submitted="", status="done", note=args.note or f"adopted from {os.path.basename(args.dir)}"))
    write_ledger(ledger)
    print(f"adopted {args.dir} as {run_id}")


# ---------------------------------------------------------------- table

def improvement_pct(candidate_value, reference_value):
    """Positive = the candidate is better on the primary metric."""
    if ARENA["primary_direction"] == "lower":
        return 100.0 * (reference_value - candidate_value) / reference_value
    return 100.0 * (candidate_value - reference_value) / reference_value


def fmt(value, digits=3):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "n/a"
    return f"{value:.{digits}f}"


def mean(values):
    values = [v for v in values if v is not None and not math.isnan(v)]
    return sum(values) / len(values) if values else None


def cmd_table(args):
    ledger = read_ledger()
    primary = ARENA["primary_metric"]
    threshold = ARENA["min_improvement_pct"]
    done = [dict(row, metrics=metrics_of(row["run_id"])) for row in ledger]
    done = [row for row in done if row["metrics"]]

    def reference_value(ref_name, seed):
        for row in done:
            if row["candidate"] == ref_name and row["seed"] == str(seed) and row["stage"] != "smoke":
                return row["metrics"].get(primary)
        return None

    names = sorted({row["candidate"] for row in ledger})
    summary, rows_out = [], []
    for name in names:
        cand = load_candidate(name)
        role = cand.get("role", "candidate")
        mine = [row for row in done if row["candidate"] == name]
        reached = next((stage for stage in reversed(STAGES) if any(r["stage"] == stage for r in mine)), None)
        top = [row for row in mine if row["stage"] == reached]
        if role == "reference":     # a reference is summarised over every seed it has
            top = [row for row in mine if row["stage"] != "smoke"]
            reached = "all" if top else reached
        deltas, deltas2 = [], []
        for row in top:
            ref = reference_value(ARENA["reference"], row["seed"])
            ref2 = reference_value(ARENA["secondary_reference"], row["seed"])
            row["delta"] = improvement_pct(row["metrics"][primary], ref) if ref else None
            row["delta2"] = improvement_pct(row["metrics"][primary], ref2) if ref2 else None
            deltas.append(row["delta"])
            deltas2.append(row["delta2"])
        if reached == "smoke":      # a smoke run is too short for its numbers to mean anything
            deltas, deltas2 = [], []
            for row in top:
                row["metrics"] = {}
        known = [d for d in deltas if d is not None]
        failed = [row for row in ledger if row["candidate"] == name and row["status"] == "failed"]
        if role == "reference":
            verdict = "reference"
        elif reached is None:
            verdict = "failed" if failed else "no finished run"
        elif reached == "smoke":
            verdict = "smoke ok"
        elif not known:
            verdict = "no reference on these seeds"
        elif role == "check":
            verdict = f"check: differs by {abs(mean(known)):.2f}%"
        elif reached == "screen":
            verdict = "promote to confirm" if mean(known) >= threshold else "dropped at screen"
        else:
            wanted = len(ARENA["seeds"]["confirm"])
            if len(known) < wanted:
                verdict = f"confirming ({len(known)}/{wanted} seeds)"
            elif mean(known) >= threshold and sum(d > 0 for d in known) >= math.ceil(2 * wanted / 3):
                verdict = "CONFIRMED"
            else:
                verdict = "not confirmed"
        cells = [name, role, reached or "-", ", ".join(sorted(row["seed"] for row in top)) or "-",
                 fmt(mean([row["metrics"].get(primary) for row in top])),
                 fmt(mean(known), 2) if known else "n/a",
                 fmt(mean([d for d in deltas2 if d is not None]), 2)]
        cells += [fmt(mean([row["metrics"].get(m) for row in top])) for m in ARENA["report_metrics"] if m != primary]
        summary.append((role != "reference", -(mean(known) or -1e9), cells + [verdict]))
        for row in sorted(mine, key=lambda r: (STAGES.index(r["stage"]), r["seed"])):
            if row["stage"] == "smoke":
                rows_out.append([row["run_id"], row["job_id"] or "-", "ran", "-", "-", "smoke: numbers not comparable"])
                continue
            ref = reference_value(ARENA["reference"], row["seed"])
            rows_out.append([row["run_id"], row["job_id"] or "-", fmt(row["metrics"].get(primary), 4), fmt(ref, 4),
                             fmt(improvement_pct(row["metrics"][primary], ref), 2) if ref else "n/a", row["note"]])

    tried = [n for n in names if load_candidate(n).get("role", "candidate") == "candidate"]
    lines = [
        "# Lab leaderboard",
        "",
        f"Generated {datetime.datetime.now().isoformat(timespec='minutes')} by `lab/labctl.py table`. Do not edit by hand.",
        "",
        f"- **Arena:** `{ARENA['name']}`: network `{ARENA['network']}`, task `{ARENA['task_conf']}`, "
        f"environment `{ARENA['env_conf']}`",
        f"- **Primary metric:** `{primary}` ({ARENA['primary_direction']} is better). "
        f"Δ columns are the improvement in percent over the reference on the same seed; positive is better.",
        f"- **Rule:** screen on seed(s) {ARENA['seeds']['screen']}; promote at Δ ≥ {threshold}%; "
        f"confirm on seeds {ARENA['seeds']['confirm']}, which no candidate was screened on.",
        f"- **Candidates tried so far:** {len(tried)} (every one is listed, including dropped ones).",
        "",
        "| Candidate | Role | Stage | Seeds | " + primary + " | Δ vs `" + ARENA["reference"] + "` % | Δ vs `"
        + ARENA["secondary_reference"] + "` % | "
        + " | ".join(m for m in ARENA["report_metrics"] if m != primary) + " | Verdict |",
        "|" + " --- |" * (8 + len([m for m in ARENA["report_metrics"] if m != primary])),
    ]
    for _, _, cells in sorted(summary, key=lambda item: (item[0], item[1])):
        lines.append("| " + " | ".join(cells) + " |")
    lines += ["", "## Runs", "",
              "| Run | Job | " + primary + " | Reference, same seed | Δ % | Note |", "| --- | --- | --- | --- | --- | --- |"]
    lines += ["| " + " | ".join(cells) + " |" for cells in rows_out]
    unfinished = [row for row in ledger if row["status"] != "done"]
    if unfinished:
        lines += ["", "## Not finished", "", "| Run | Job | Status | Note |", "| --- | --- | --- | --- |"]
        lines += [f"| {row['run_id']} | {row['job_id'] or '-'} | {row['status']} | {row['note']} |" for row in unfinished]
    with open(os.path.join(LAB, "LEADERBOARD.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {os.path.join(LAB, 'LEADERBOARD.md')}: {len(summary)} candidates, {len(rows_out)} finished runs")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("new"); p.add_argument("name"); p.set_defaults(func=cmd_new)
    p = sub.add_parser("submit"); p.add_argument("name"); p.add_argument("--stage", choices=STAGES, required=True)
    p.add_argument("--seeds", type=int, nargs="*"); p.set_defaults(func=cmd_submit)
    p = sub.add_parser("status"); p.set_defaults(func=cmd_status)
    p = sub.add_parser("collect"); p.set_defaults(func=cmd_collect)
    p = sub.add_parser("table"); p.set_defaults(func=cmd_table)
    p = sub.add_parser("adopt"); p.add_argument("dir"); p.add_argument("name")
    p.add_argument("--stage", choices=STAGES, required=True); p.add_argument("--seed", type=int, required=True)
    p.add_argument("--note"); p.set_defaults(func=cmd_adopt)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
