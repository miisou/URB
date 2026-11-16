"""
Generic runner for lab candidates (see lab/README.md).

It follows scripts/iql_tabular.py step by step (human learning, mutation, CAV learning, testing,
metrics) and delegates every CAV decision to the fleet object built by
lab/candidates/<candidate>/policy.py. Hyperparameters come from lab/candidates/<candidate>/config.json,
which must contain "training_eps".

Example:
python3 lab_runner.py --id demo --candidate tabular_q_port --env-conf config_ing_short \
    --task-conf selfish_40 --net ingolstadt_custom2 --env-seed 40 --torch-seed 40
"""

import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import argparse
import ast
import importlib.util
import json
import logging
import random

import numpy as np
import pandas as pd

from routerl import TrafficEnvironment
from tqdm import tqdm

from utils import clear_SUMO_files
from utils import print_agent_counts
from utils import run_metrics_analysis
from utils import script_path_for_config


def load_candidate(name):
    folder = os.path.join(repo_root, "lab", "candidates", name)
    with open(os.path.join(folder, "config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    spec = importlib.util.spec_from_file_location(f"lab_candidate_{name}", os.path.join(folder, "policy.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return cfg, module


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=str, required=True)
    parser.add_argument('--candidate', type=str, required=True)
    parser.add_argument('--env-conf', type=str, default="config1")
    parser.add_argument('--task-conf', type=str, required=True)
    parser.add_argument('--net', type=str, required=True)
    parser.add_argument('--env-seed', type=int, default=42)
    parser.add_argument('--torch-seed', type=int, default=42)
    parser.add_argument('--smoke', action='store_true', default=False,
                        help="10 human days, 10 CAV-learning days, 5 test days: checks that the code runs")
    parser.add_argument('--skip-metrics', action='store_true', default=False)
    args = parser.parse_args()

    candidate = args.candidate
    ALGORITHM = f"lab_{candidate}"
    exp_id = args.id
    env_config = args.env_conf
    task_config = args.task_conf
    network = args.net
    env_seed = args.env_seed
    torch_seed = args.torch_seed

    print("### STARTING EXPERIMENT ###")
    print(f"Algorithm: {ALGORITHM}")
    print(f"Experiment ID: {exp_id}")
    print(f"Network: {network}")
    print(f"Environment seed: {env_seed}")
    print(f"Algorithm seed: {torch_seed}")
    print(f"Environment config: {env_config}")
    print(f"Task config: {task_config}")
    print(f"Smoke run: {args.smoke}\n")

    logging.getLogger("matplotlib").setLevel(logging.ERROR)
    random.seed(env_seed)
    np.random.seed(env_seed)

    cand_cfg, cand_module = load_candidate(candidate)
    env_params = json.load(open(f"../config/env_config/{env_config}.json"))
    task_params = json.load(open(f"../config/task_config/{task_config}.json"))
    params = dict()
    params.update(cand_cfg)
    params.update(env_params)
    params.update(task_params)
    params.pop("desc", None)

    training_eps = int(params["training_eps"])
    human_learning_episodes = int(params["human_learning_episodes"])
    test_eps = int(params["test_eps"])
    plot_every = int(params.get("plot_every", 50))
    if args.smoke:
        human_learning_episodes, training_eps, test_eps = 10, 10, 5
        params.update(human_learning_episodes=10, training_eps=10, test_eps=5, smoke=True)

    custom_network_folder = f"../networks/{network}"
    phases = [1, human_learning_episodes, training_eps + human_learning_episodes]
    phase_names = ["Human stabilization", "Mutation and AV learning", "Testing phase"]
    base_results_dir = os.environ.get("RESULTS_BASE_DIR", "../results")
    records_folder = os.path.join(base_results_dir, exp_id)
    plots_folder = os.path.join(records_folder, "plots")

    with open(os.path.join(custom_network_folder, f"od_{network}.txt"), 'r', encoding='utf-8') as f:
        od_data = ast.literal_eval(f.read())
    origins = od_data['origins']
    destinations = od_data['destinations']

    agents_csv_path = os.path.join(custom_network_folder, "agents.csv")
    if not os.path.exists(agents_csv_path):
        raise FileNotFoundError(f"Agents file not found: {agents_csv_path}")
    os.makedirs(records_folder, exist_ok=True)
    new_agents_csv_path = os.path.join(records_folder, "agents.csv")
    with open(agents_csv_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(new_agents_csv_path, 'w', encoding='utf-8') as f:
        f.write(content)
    agents_df = pd.read_csv(new_agents_csv_path)
    num_agents = len(agents_df)
    max_start_time = agents_df['start_time'].max()

    num_machines = int(num_agents * params["ratio_machines"])
    total_episodes = human_learning_episodes + training_eps + test_eps

    dump_config = params.copy()
    dump_config["network"] = network
    dump_config["env_seed"] = env_seed
    dump_config["torch_seed"] = torch_seed
    dump_config["env_config"] = env_config
    dump_config["task_config"] = task_config
    dump_config["alg_config"] = f"lab/candidates/{candidate}/config.json"
    dump_config["candidate"] = candidate
    dump_config["script"] = script_path_for_config(__file__)
    dump_config["algorithm"] = ALGORITHM
    dump_config["num_agents"] = num_agents
    dump_config["num_machines"] = num_machines
    with open(os.path.join(records_folder, "exp_config.json"), 'w', encoding='utf-8') as f:
        json.dump(dump_config, f, indent=4)

    env = TrafficEnvironment(
        seed = env_seed,
        create_agents = False,
        create_paths = True,
        save_detectors_info = False,
        agent_parameters = {
            "new_machines_after_mutation": num_machines,
            "human_parameters": {
                "model": params["human_model"],
                "alpha": params["human_alpha"],
                "beta": params["human_beta"],
                "beta_randomness": params["human_beta_randomness"],
                "deterministic": params["human_deterministic"],
            },
            "machine_parameters": {
                "behavior": params["av_behavior"],
                "observation_type": params["observations"]
            }
        },
        environment_parameters = {
            "save_every": params["save_every"],
        },
        simulator_parameters = {
            "network_name": network,
            "custom_network_folder": custom_network_folder,
            "sumo_type": "sumo",
            "simulation_timesteps": max_start_time
        },
        plotter_parameters = {
            "phases": phases,
            "phase_names": phase_names,
            "smooth_by": params["smooth_by"],
            "plot_choices": params["plot_choices"],
            "records_folder": records_folder,
            "plots_folder": plots_folder
        },
        path_generation_parameters = {
            "origins": origins,
            "destinations": destinations,
            "number_of_paths": params["number_of_paths"],
            "beta": params["path_gen_beta"],
            "num_samples": params["num_samples"],
            "path_gen_workers": params.get("path_gen_workers", 1),
            "visualize_paths": False
        }
    )

    env.start()
    env.reset()
    print_agent_counts(env)

    ### Human learning phase ###
    pbar = tqdm(total=total_episodes, desc="Human learning")
    for episode in range(human_learning_episodes):
        env.step()
        pbar.update()

    # Mutation
    env.mutation(disable_human_learning = not params["should_humans_adapt"], mutation_start_percentile = -1)
    print_agent_counts(env)

    # Build the candidate's fleet
    ctx = {
        "cfg": cand_cfg,
        "seed": torch_seed,
        "agents": [
            {
                "id": str(agent.id),
                "idx": idx,
                "origin": agent.origin,
                "destination": agent.destination,
                "start_time": agent.start_time,
                "n_actions": agent.action_space_size,
            }
            for idx, agent in enumerate(env.machine_agents)
        ],
        "free_flow": env.get_free_flow_times(),
    }
    fleet = cand_module.build(ctx)

    def run_day(day, phase):
        env.reset()
        for agent_id in env.agent_iter():
            observation, reward, termination, truncation, info = env.last()
            if termination or truncation:
                if phase == "train":
                    fleet.feedback(agent_id, float(reward))
                action = None
            else:
                action = int(fleet.act(agent_id, observation))
            env.step(action)
        fleet.end_day(day, phase)

    ### Learning phase ###
    pbar.set_description("AV learning")
    os.makedirs(plots_folder, exist_ok=True)
    for episode in range(training_eps):
        run_day(episode, "train")
        if episode % plot_every == 0:
            env.plot_results()
        pbar.update()

    ### Testing phase ###
    fleet.start_test()
    pbar.set_description("Testing")
    for episode in range(test_eps):
        run_day(episode, "test")
        pbar.update()

    pbar.close()
    env.plot_results()
    env.stop_simulation()
    clear_SUMO_files(os.path.join(records_folder, "SUMO_output"), os.path.join(records_folder, "episodes"), remove_additional_files=True)
    if not args.skip_metrics:
        run_metrics_analysis(exp_id, results_folder=base_results_dir)
