#!/usr/bin/env python3
"""
K-plan version of your pipeline.

What this DOES:
- Replaces generate_plan() with generate_k_plans() that runs Fast Downward K times
  using randomized greedy search (different seeds) to get K candidate plans.
- Stores each plan into unique files (sas_plan_k_1, sas_plan_k_2, ...)
- Converts each sas plan to txt and parses actions using your existing helpers.

What this DOES NOT guarantee:
- True “top-k” (k cheapest distinct plans). Fast Downward doesn’t enumerate k-best plans
  out-of-the-box via aliases. This gives you K diverse candidate plans.

If you want true k-best-by-cost, you need iterative “plan banning” (replanning with constraints),
which requires extra compilation/constraints. If you want that, tell me and I’ll give that version.
"""

from read_plan import read_sas_plan, store_sas_plan_as_txt
from pddl_parser import PDDL_Parser
from subprocess import Popen, PIPE
from datetime import datetime
import subprocess
import os
import shutil
import hashlib


# -----------------------------
# Your existing helpers
# -----------------------------
def remove_effect_from_action(parsed_actions, action, effect):
    flag = 0
    for act in parsed_actions:
        if act.name == action:
            for x in act.add_effects:
                if x[0] == effect:
                    remove_tuple = x
                    flag = 1
                if flag == 1:
                    act.add_effects.discard(remove_tuple)
                    break
    return parsed_actions


def current_state_sim(parser, action, sim_state):
    postCond_act = find_postCond(parser, action)
    print("--PostCond of SIM Action--")
    print(postCond_act)
    current_state = sim_state | postCond_act
    return current_state


def find_postCond(parser, action_name):
    postCond = set()
    for act in parser.actions:
        if act.name == action_name:
            postCond = act.add_effects | act.del_effects
            break
    return postCond


def find_preCond(parser, action_name):
    preCond = set()
    for act in parser.actions:
        if act.name == action_name:
            preCond = act.positive_preconditions | act.negative_preconditions
            break
    return preCond


# -----------------------------
# Grounding
# -----------------------------
def ground_domain_problem(domain, problem, typ):
    command = [
        "python3",
        "grounder/grounder_interface.py",
        domain,
        problem,
        f"k_plan/{typ}_grounded_{domain}",
        f"k_plan/{typ}_grounded_{problem}",
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    print("Grounder Output:")
    print(result.stdout)
    print("Grounder Errors:")
    print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError("Grounding failed; see errors above.")


# -----------------------------
# Fast Downward: K plan generation
# -----------------------------
def _hash_plan_actions(actions):
    """Stable hash for a plan (to filter duplicates)."""
    s = "\n".join(actions).encode("utf-8")
    return hashlib.sha256(s).hexdigest()


def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def run_fast_downward_once(domain_file, problem_file, fd_path, plan_file, seed=0, time_limit_sec=30):
    """
    Run FD once and write plan to plan_file via --plan-file.
    Uses randomized greedy search to produce different plans across seeds.
    """
    # A decent randomized greedy configuration:
    # - uses FF heuristic, randomizes successor order, and uses a random seed
    # - good for quickly getting alternative solutions
    search = (
        f"lazy_greedy([ff()], preferred=[ff()], "
        f"randomize_successors=true, random_seed={seed})"
    )

    cmd = [
        fd_path,
        "--plan-file", plan_file,
        "--overall-time-limit", str(time_limit_sec),
        domain_file,
        problem_file,
        "--search", search,
    ]

    print("\n[FD CMD]")
    print(" ".join(cmd))

    proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()

    out = stdout.decode("utf-8", errors="ignore")
    err = stderr.decode("utf-8", errors="ignore")

    return proc.returncode, out, err


def generate_k_plans(domain, problem, output_dir, k=3, base_seed=100, time_limit_sec=30):
    """
    Generates up to K (diverse) plans by running FD K times with different seeds.

    Returns:
      plan_txt_paths: list of paths to plan text files (actions in your format)
      plan_actions_list: list[list[str]] each is list of actions
    """
    fd_path = "/s/chopin/l/grad/shadaab/Downloads/downward/fast-downward.py"

    domain_file = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/" + domain
    problem_file = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/" + problem

    _ensure_dir(output_dir)

    plan_txt_paths = []
    plan_actions_list = []
    seen = set()

    for i in range(1, k + 1):
        seed = base_seed + i

        # FD output files
        plan_file = os.path.join(output_dir, f"sas_plan_k_{i}")
        output_log = os.path.join(output_dir, f"fd_out_{i}.txt")

        # Run FD
        rc, out, err = run_fast_downward_once(
            domain_file=domain_file,
            problem_file=problem_file,
            fd_path=fd_path,
            plan_file=plan_file,
            seed=seed,
            time_limit_sec=time_limit_sec,
        )

        # store console output for debugging
        with open(output_log, "w") as f:
            f.write(out)
            f.write("\n\n[STDERR]\n")
            f.write(err)

        # If no plan file produced, skip
        if not os.path.exists(plan_file) or os.path.getsize(plan_file) == 0:
            print(f"[WARN] No plan produced for seed={seed}. See {output_log}")
            continue

        # Convert sas plan -> txt (your helper copies lines)
        plan_txt = os.path.join(output_dir, f"plan_k_{i}.txt")
        store_sas_plan_as_txt(plan_file, plan_txt)

        # Read actions
        actions = read_sas_plan(plan_txt)

        # Filter duplicates
        h = _hash_plan_actions(actions)
        if h in seen:
            print(f"[INFO] Duplicate plan (seed={seed}); skipping.")
            continue
        seen.add(h)

        plan_txt_paths.append(plan_txt)
        plan_actions_list.append(actions)

        print(f"[OK] Plan {len(plan_actions_list)} stored: {plan_txt}")

    return plan_txt_paths, plan_actions_list


# -----------------------------
# Optional: pick the “best” plan for your RPLA loop
# -----------------------------
def plan_executable_prefix_length(parser_est, sim_state, actions):
    """
    Measures how many initial actions are executable in the simulator state (by precondition check).
    """
    prefix = 0
    for a in actions:
        pre = find_preCond(parser_est, a)
        if set(pre).issubset(set(sim_state)):
            prefix += 1
        else:
            break
    return prefix


def choose_best_plan(parser_est, sim_state, plans_actions_list):
    """
    Chooses plan that maximizes executable prefix length (ties: shorter plan).
    """
    if not plans_actions_list:
        return []

    scored = []
    for acts in plans_actions_list:
        pref = plan_executable_prefix_length(parser_est, sim_state, acts)
        scored.append((pref, -len(acts), acts))

    scored.sort(reverse=True)
    best = scored[0][2]
    print(f"[SELECT] Best plan: executable_prefix={scored[0][0]} length={len(best)}")
    return list(best)


# -----------------------------
# Main (your pipeline)
# -----------------------------
def main():
    start = datetime.now()

    network = "flare"

    # Files
    domain_estimator = f"domain_all_faults-{network}.pddl"
    problem_estimator = f"problem-{network}.pddl"

    domain_sim = f"domain-{network}.pddl"
    problem_sim = f"problem-{network}.pddl"

    # Ground
    t_ground = datetime.now()
    ground_domain_problem(domain_estimator, problem_estimator, "est")
    ground_domain_problem(domain_sim, problem_sim, "org")
    print(f"[TIME] Grounding took {(datetime.now() - t_ground).total_seconds():.2f}s")

    grounded_domain_estimator = "k_plan/" + "est_grounded_" + domain_estimator
    grounded_problem_estimator = "k_plan/" + "est_grounded_" + problem_estimator

    grounded_domain_sim = "k_plan/" + "org_grounded_" + domain_sim
    grounded_problem_sim = "k_plan/" + "org_grounded_" + problem_sim

    # Parse simulator and estimator
    parser_sim = PDDL_Parser()
    parser_sim.parse_domain(grounded_domain_sim)
    parser_sim.parse_problem(grounded_problem_sim)

    parser_est = PDDL_Parser()
    parser_est.parse_domain(grounded_domain_estimator)
    parser_est.parse_problem(grounded_problem_estimator)

    # Initial states
    sim_state = parser_sim.state
    est_state = parser_est.state

    print("\nInitial State of Simulator:")
    for item in sim_state:
        print(item)
    print("---------------------------")

    print("\nInitial State of Estimator:")
    for item in est_state:
        print(item)
    print("---------------------------")

    # Goal state of estimator
    est_goal_state = parser_est.positive_goals | parser_est.negative_goals

    # K planning settings
    K = 3
    FD_TIME_LIMIT = 30  # seconds per candidate plan
    OUTPUT_DIR = "k_plan/k_candidates"

    a = 0
    flag = 0
    while True:
        print(f"\n========== OUTER ITERATION {a} ==========")

        # Reload estimator parser each outer iteration (since you update the domain)
        parser_est = PDDL_Parser()
        parser_est.parse_domain(grounded_domain_estimator)
        parser_est.parse_problem(grounded_problem_estimator)

        # Generate K candidate plans for estimator
        _, plans_actions_list = generate_k_plans(
            domain=grounded_domain_estimator,
            problem=grounded_problem_estimator,
            output_dir=OUTPUT_DIR,
            k=K,
            base_seed=1000 + 17 * a,
            time_limit_sec=FD_TIME_LIMIT,
        )

        if not plans_actions_list:
            raise RuntimeError("No plans found by FD (K candidates all failed).")

        # Choose “best” plan for your refinement loop
        estimator_actions = choose_best_plan(parser_est, sim_state, plans_actions_list)

        print("***Chosen Estimated Plan***")
        print(estimator_actions)

        # Refresh goal state (in case it changed)
        est_goal_state = parser_est.positive_goals | parser_est.negative_goals

        i = 0
        while len(estimator_actions) > 0:
            print(f"\n---- INNER ITERATION {i} ----")

            action = estimator_actions.pop(0)
            print("--POP Action from Estimated plan--")
            print(action)

            preCond_act_est = find_preCond(parser_est, action)
            print("--PreCond of EST Action--")
            print(preCond_act_est)

            is_subset_of_sim = set(preCond_act_est).issubset(set(sim_state))

            if is_subset_of_sim:
                print("It is a Subset of SIM")

                # Simulator update
                sim_state = current_state_sim(parser_sim, action, sim_state)
                print("Current State of Simulator:")
                for item in sim_state:
                    print(item)
                print("---------------------------")

                # Estimator update
                postCond_act_est = find_postCond(parser_est, action)
                print("--PostCond of EST Action--")
                print(postCond_act_est)

                est_state = est_state | postCond_act_est
                print("Current State of Estimator:")
                for item in est_state:
                    print(item)
                print("---------------------------")

                # If mismatch: refine estimator by removing extra predicates from that action
                if sim_state != est_state:
                    predicates_remove_from_est = est_state - sim_state
                    print("Remove Predicates:")
                    print(f"{predicates_remove_from_est} from Action:{action}")

                    for j in predicates_remove_from_est:
                        parser_est.actions = remove_effect_from_action(parser_est.actions, action, j[0])

                    for kpred in predicates_remove_from_est:
                        if kpred in est_state:
                            est_state.remove(kpred)

                # Goal check
                is_subset_of_goal = set(est_goal_state).issubset(set(est_state))
                if is_subset_of_goal:
                    print("GOAL REACHED!")
                    flag = 1
                    break
                else:
                    print("NO GOAL REACHED!")

            else:
                print("Action not executable in simulator state; skipping (will replan next outer iter).")
                # Break inner loop and trigger replanning after domain update
                break

            i += 1

        print("\n***Domain Updated***")
        parser_est.generate_pddl_file(grounded_domain_estimator)

        if flag == 1:
            break

        a += 1

    end = datetime.now()
    td = (end - start).total_seconds() * 10**3
    print(f"\nThe TOTAL time of execution of above program is : {td:.03f}ms")
    print(f"Iteration {a+1}")


if __name__ == "__main__":
    main()
