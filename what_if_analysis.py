from read_plan import read_sas_plan, store_sas_plan
from pddl_parser_updated import PDDL_Parser
from subprocess import Popen, PIPE
import os
import sys
from datetime import datetime
import subprocess
import domain_problem_update
import re
import itertools
import json

# def get_total_costs_for_action_sets(domain_file, list_of_action_sets):
#     """
#     Computes the total cost for each set of action names from a PDDL domain file.

#     Args:
#         domain_file (str): Path to the domain.pddl file.
#         list_of_action_sets (list of sets): Each set contains action names.

#     Returns:
#         list of floats: Total cost for each action set.
#     """
#     with open(domain_file, 'r') as f:
#         lines = f.readlines()

#     action_costs = {}
#     inside_action = False
#     current_action = None
#     paren_balance = 0
#     buffer = []

#     for line in lines:
#         stripped = line.strip()

#         # Start of action
#         if not inside_action and stripped.startswith("(:action"):
#             parts = stripped.split()
#             if len(parts) >= 2:
#                 current_action = parts[1]
#                 inside_action = True
#                 paren_balance = line.count('(') - line.count(')')
#                 buffer = [line]
#             continue

#         elif inside_action:
#             buffer.append(line)
#             paren_balance += line.count('(') - line.count(')')
#             if paren_balance == 0:
#                 # End of action block
#                 action_block = "\n".join(buffer)
#                 cost_match = re.search(r"\(increase\s+\(total-cost\)\s+([0-9.]+)\)", action_block)
#                 if cost_match:
#                     action_costs[current_action] = float(cost_match.group(1))
#                 else:
#                     action_costs[current_action] = 0.0
#                     print(f"⚠️ No cost found in action '{current_action}', defaulting to 0.")
#                 inside_action = False
#                 current_action = None
#                 buffer = []
#             continue

#     print(f"✅ Parsed {len(action_costs)} actions with costs.\n")

#     # Compute cost for each action set
#     costs_per_set = []

#     for i, action_set in enumerate(list_of_action_sets):
#         print(f"📦 Processing set {i + 1}: {action_set}")
#         total = 0.0
#         for action in action_set:
#             if action in action_costs:
#                 cost = action_costs[action]
#                 total += cost
#                 print(f"  - {action}: {cost}")
#             else:
#                 print(f"  ❌ Action '{action}' not found in domain.")
#         print(f"  ➕ Total cost for set {i + 1}: {total}\n")
#         costs_per_set.append(total)

#     return costs_per_set

def get_total_costs_for_action_sets(domain_file, list_of_action_sets):
    """
    Computes the total cost for each set of action names from a PDDL domain file
    and returns the list of costs and the set with the least cost.

    Args:
        domain_file (str): Path to the domain.pddl file.
        list_of_action_sets (list of sets): Each set contains action names.

    Returns:
        tuple: (list of costs, set with least cost, its cost)
    """
    with open(domain_file, 'r') as f:
        lines = f.readlines()

    action_costs = {}
    inside_action = False
    current_action = None
    paren_balance = 0
    buffer = []

    # Parse the domain to extract each action and its cost
    for line in lines:
        stripped = line.strip()

        if not inside_action and stripped.startswith("(:action"):
            parts = stripped.split()
            if len(parts) >= 2:
                current_action = parts[1]
                inside_action = True
                paren_balance = line.count('(') - line.count(')')
                buffer = [line]
            continue

        elif inside_action:
            buffer.append(line)
            paren_balance += line.count('(') - line.count(')')
            if paren_balance == 0:
                action_block = "\n".join(buffer)
                cost_match = re.search(r"\(increase\s+\(total-cost\)\s+([0-9.]+)\)", action_block)
                if cost_match:
                    action_costs[current_action] = float(cost_match.group(1))
                else:
                    action_costs[current_action] = 0.0
                    print(f"⚠️ No cost found in action '{current_action}', defaulting to 0.")
                inside_action = False
                current_action = None
                buffer = []
            continue

    print(f"✅ Parsed {len(action_costs)} actions with costs.\n")

    # Compute cost for each action set and track the minimum
    costs_per_set = []
    min_cost = float('inf')
    min_cost_set = None

    for i, action_set in enumerate(list_of_action_sets):
        print(f"📦 Processing set {i + 1}: {action_set}")
        total = 0.0
        for action in action_set:
            if action in action_costs:
                cost = action_costs[action]
                total += cost
                print(f"  - {action}: {cost}")
            else:
                print(f"  ❌ Action '{action}' not found in domain.")
        print(f"  ➕ Total cost for set {i + 1}: {total}\n")
        costs_per_set.append(total)

        if total < min_cost:
            min_cost = total
            min_cost_set = action_set

    return costs_per_set, min_cost_set, min_cost


def copy_actions(source_file, target_file, action_names):
    """
    Copies specified actions from source_file and inserts them inside the domain scope
    of the target_file (before the final closing parenthesis).

    Args:
        source_file (str): Path to the original domain.pddl file.
        target_file (str): Path to the target domain.pddl file to insert actions into.
        action_names (list or set): Action names to extract and insert.
    """
    with open(source_file, 'r') as f:
        source_lines = f.readlines()

    # Step 1: Extract matching action blocks from source
    inside_action = False
    paren_balance = 0
    buffer = []
    current_action_name = None
    matched_actions = []

    for line in source_lines:
        stripped = line.strip()

        if not inside_action and stripped.startswith("(:action"):
            parts = stripped.split()
            if len(parts) >= 2:
                current_action_name = parts[1]
                if current_action_name in action_names:
                    inside_action = True
                    paren_balance = line.count("(") - line.count(")")
                    buffer = [line]
                    continue

        elif inside_action:
            buffer.append(line)
            paren_balance += line.count("(") - line.count(")")
            if paren_balance == 0:
                inside_action = False
                matched_actions.append("".join(buffer))
                buffer = []
                current_action_name = None
            continue

    if not matched_actions:
        print("⚠️ No matching actions found.")
        return

    # Step 2: Insert matched actions before final closing ')'
    with open(target_file, 'r') as f:
        target_lines = f.readlines()

    # Find the index of the last closing parenthesis (assumed to close the domain)
    for i in range(len(target_lines) - 1, -1, -1):
        if target_lines[i].strip() == ")":
            insertion_index = i
            break
    else:
        print("Could not find domain closing ')' in target file.")
        return

    # Insert actions before the final ')'
    new_content = (
        target_lines[:insertion_index] +
        ["\n"] +
        [action + "\n" for action in matched_actions] +
        [target_lines[insertion_index]]
    )

    with open(target_file, 'w') as f:
        f.writelines(new_content)

    print(f"Inserted {len(matched_actions)} action(s) into '{target_file}' inside the domain scope.")



def remove_pddl_actions(file_path, action_names):
    """
    Removes all specified actions from a domain.pddl file using balanced parentheses.

    Args:
        file_path (str): Path to the domain.pddl file.
        action_names (set or list): Action names to remove.

    Returns:
        int: Number of actions removed.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    inside_action = False
    paren_balance = 0
    buffer = []
    total_removed = 0
    current_action_name = None

    for line in lines:
        stripped = line.strip()

        if not inside_action and stripped.startswith("(:action"):
            # Parse action name
            parts = stripped.split()
            if len(parts) >= 2:
                current_action_name = parts[1]
                if current_action_name in action_names:
                    inside_action = True
                    paren_balance = line.count("(") - line.count(")")
                    buffer = [line]
                    continue  # Don't add this line to new_lines
                else:
                    # Not a target action
                    new_lines.append(line)
            else:
                # malformed action line, just keep it
                new_lines.append(line)

        elif inside_action:
            buffer.append(line)
            paren_balance += line.count("(") - line.count(")")
            if paren_balance == 0:
                # Finished skipping one full action
                inside_action = False
                total_removed += 1
                buffer = []
                current_action_name = None
            continue  # Skip adding this line

        else:
            new_lines.append(line)

    # Write back the cleaned content
    with open(file_path, 'w') as f:
        f.writelines(new_lines)

    if total_removed == 0:
        print("⚠️ No matching actions found.")
    else:
        print(f"✅ Removed {total_removed} action(s) and updated '{file_path}'.")

    return total_removed

def generate_non_empty_subsets(input_list):
    """
    Generate all non-empty subsets of a list (converted to a set).

    Args:
        input_list (list): The original list of elements.

    Returns:
        list of sets: All non-empty subsets of the input as a set.
    """
    input_set = set(input_list)
    subset_list = []
    for r in range(1, len(input_set) + 1):
        for combo in itertools.combinations(input_set, r):
            subset_list.append(set(combo))
    return subset_list

# def generate_limited_subsets(input_list, max_size=3):
#     input_set = set(input_list)
#     for r in range(1, min(max_size + 1, len(input_set) + 1)):
#         for combo in itertools.combinations(input_set, r):
#             yield set(combo)

# def list_exploit_actions(domain_file_path):
#     """
#     Reads a PDDL domain file and lists all action names that start with 'exploits-vulnerability-'.

#     Args:
#         domain_file_path (str): Path to the domain.pddl file.

#     Returns:
#         List[str]: A list of matching action names.
#     """
#     with open(domain_file_path, 'r') as file:
#         content = file.read()

#     # Match PDDL :action blocks and extract their names
#     action_pattern = re.compile(r'\(:action\s+([^\s\)]+)', re.IGNORECASE)
#     action_names = action_pattern.findall(content)

#     # Filter actions that start with 'exploits-vulnerability-'
#     exploit_actions = [name for name in action_names if name.startswith('exploits-vulnerability-')]

#     return exploit_actions

def list_matching_actions(domain_file_path, prefixes):
    """
    Reads a PDDL domain file and lists all action names that start with any of the given prefixes.

    Args:
        domain_file_path (str): Path to the domain.pddl file.
        prefixes (List[str]): List of string prefixes to match.

    Returns:
        List[str]: A list of matching action names.
    """
    with open(domain_file_path, 'r') as file:
        content = file.read()

    # Match PDDL :action blocks and extract their names
    action_pattern = re.compile(r'\(:action\s+([^\s\)]+)', re.IGNORECASE)
    action_names = action_pattern.findall(content)

    # Filter actions that start with any of the given prefixes
    matching_actions = [
        name for name in action_names
        if any(name.startswith(prefix) for prefix in prefixes)
    ]

    return matching_actions



def generate_plan(domain, problem, output):
    # Set the paths to the FastDownward executable and the PDDL files
    fastdownward_path = "/s/chopin/l/grad/shadaab/Downloads/downward/fast-downward.py"

    #domain and problem file for test
    domain_file = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/"+domain
    problem_file = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/"+problem
    # Set the output file path
    output_file = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/"+output

    #PLAN
    # Define the search configuration
    # search_config = "astar(cegar(subtasks=[goals()], max_states=1000000))"
    search_config = "astar(ff())"

    # Construct the FastDownward command
    command = [
        fastdownward_path,
        domain_file,
        problem_file,
        "--search",
        search_config
    ]

    # print(f"Plan generation command:{command}")
    # Run the planner
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    # Decode the output
    output = stdout.decode("utf-8")

    # Write the output to a file
    with open(output_file, "w") as file:
        file.write(output)

    # print(f"Plan stored in {output_file}")


def ground_domain_problem(domain, problem):
    command = [
    "python3",
    "grounder/grounder_interface.py",
    domain,
    problem,
    "what_if_analysis/grounded_"+domain,
    "what_if_analysis/grounded_"+problem
    ]

    # print(f"Command: {command}")
    # Execute the command
    result = subprocess.run(command, capture_output=True, text=True)
    # print(result)



domain = "domain-flare_what_if.pddl"
problem = "problem-flare_what_if.pddl"

sas_plan_path = "sas_plan"

start = datetime.now()

ground_domain_problem(domain, problem)

domain_estimator = "what_if_analysis/grounded_domain-flare_what_if.pddl"
problem_estimator = "what_if_analysis/grounded_problem-flare_what_if.pddl"
org_domain = "what_if_analysis/grounded-flare-domain-original.pddl"
output_est_plan_path = "what_if_analysis/plan.txt"
plan_path = "what_if_analysis/only_plan.txt"

#Add cost=1 to every action
start_time = datetime.now()
domain_problem_update.add_cost_to_actions(domain_estimator, domain_estimator)
end_time = datetime.now()
time_taken = end_time - start_time
print(f"Time Taken for actions to convert add cost=1:{time_taken}")

#Add cost function
start_time = datetime.now()
domain_problem_update.add_total_cost_function(domain_estimator)
end_time = datetime.now()
time_taken = end_time - start_time
print(f"Time Taken for actions to add cost function:{time_taken}")

#Problem file update with (:metric minimize (total-cost)) and (= (total-cost) 0)
start_time = datetime.now()
domain_problem_update.modify_problem_file_for_whatIf(problem_estimator, problem_estimator)
end_time = datetime.now()
time_taken = end_time - start_time
print(f"Time Taken to modify problem file:{time_taken}")


# print("Generating Plan")
# start_time = datetime.now()
# generate_plan(domain_estimator, problem_estimator, output_est_plan_path)
# end_time = datetime.now()
# time_taken = end_time - start_time
# print(f"Time Taken to generate plan:{time_taken}")

# store_sas_plan_as_txt("sas_plan", plan_path)

#find the exploitable actions
prefix = ["exploits-vulnerability-cve-2019-0575_microsoft-windows-12-server_internal-network",
          "exploits-vulnerability-cve-2017-9312_internal-network_plc-allen-brdley-controllogix",
          "exploits-vulnerability-cve-2017-6032_internal-network_plc-schneider-electric-modicon-m221",
          "exploits-vulnerability-cve-2018-10594_internal-network_plc-yokogawa-stardom",
          "exploits-vulnerability-cve-2017-12741_internal-network_plc-siemens-s7-1200",
          "exploits-vulnerability-cve-2017-9638_internal-network_plc-mitsubishi-melsec-q-series",
          "exploits-vulnerability-cve-2017-12089_internal-network_plc-allen-bradley-micrologix-1100",
          "exploits-vulnerability-cve-2016-8673_internal-network_plc-siemens-s7-300-or-400",
          "exploits-vulnerability-cve-2019-6815_internal-network_plc-schneider-electric-modicon-m580"]

actions = list_matching_actions(domain_estimator, prefix)
# actions = actions[:3]
print(f"Length of Subsets:{len(actions)}")
print(len(actions))
# print(actions)

#generate subset of actions
# actions =["exploits-vulnerability-cve-2017-9638_internal-network_plc-mitsubishi-melsec-q-series"]
subsets = list(generate_non_empty_subsets(actions))
print(f"Length of Subsets:{len(subsets)}")
subsets = sorted(subsets, key=len, reverse=True)
print(len(subsets))
# print(subsets)

# #TEST
# popped_set = {"exploits-vulnerability-cve-2019-0575_microsoft-windows-12-server_internal-network"}
# # print("Popped set:", popped_set)
# remove_pddl_actions(domain_estimator, popped_set)
# print("Action remove!")

# # copy_actions(org_domain, domain_estimator, popped_set)
# # print("Action ADDED!")
# try:
#     print("Generating Plan")
#     start_time = datetime.now()
#     generate_plan(domain_estimator, problem_estimator, output_est_plan_path)
#     # print("Storing Plan")
#     sas_file_existance = store_sas_plan("sas_plan", plan_path)
#     print(sas_file_existance)

#       # or provide full path if needed

#     if os.path.exists(sas_plan_path):
#         print(f"✅ File '{sas_plan_path}' exists.")
#     else:
#         print(f"❌ File '{sas_plan_path}' does NOT exist.")

#     # with open(plan_path, 'r') as plan_file:
#     #         print("Inside Open!")
#     #         plan_content = plan_file.read().strip()
#     #         print("Plan:")
#     #         print(plan_content if plan_content else "⚠️ Plan is empty.")

# except Exception as e:
#     print("❌ Exception occurred while generating or loading the plan:")
#     print(e)

# print("End!")


# # #Algorithm:

changes = []

while subsets:
    popped_set = subsets.pop()
    print("Popped set:", popped_set)
    print("Remaining list length:", len(subsets))
    actions_to_remove = popped_set
    remove_pddl_actions(domain_estimator, actions_to_remove)

    try:
        print("Generating Plan")
        start_time = datetime.now()
        generate_plan(domain_estimator, problem_estimator, output_est_plan_path)
        sas_file_existance = store_sas_plan("sas_plan", plan_path)
        end_time = datetime.now()
        time_taken = end_time - start_time
        print(f"Time Taken to generate plan inside the loop:{time_taken}")

        if os.path.exists(sas_plan_path):
            print(f"File '{sas_plan_path}' exists.")
        else:
            print(f"File '{sas_plan_path}' does NOT exist.")

        # if actions_to_remove == {"exploits-vulnerability-cve-2017-9638_internal-network_plc-mitsubishi-melsec-q-series"}:
        #     break;
        
        # #check if the plan is empty or not
        # with open(plan_path, 'r') as plan_file:
        #     plan_content = plan_file.read().strip()
        #     print("Plan:")
        #     print(plan_content if plan_content else "⚠️ Plan is empty.")

        #add the subset for no plan
        if not sas_file_existance:
            print("Plan is EMPTY.")
            changes.append(popped_set)
        else:
            print("Plan is NOT empty.")
            # changes.append(popped_set)
    
    except Exception as e:
        print("Exception occurred while generating or loading the plan:")
        print(e)
        
        #add the actions back to Domain
    copy_actions(org_domain, domain_estimator, actions_to_remove)


print("Changes!")
# for change in changes:
#     print(change)
print(len(changes))
print(changes)

with open("action_to_change.json", "w") as f:
    json.dump([list(s) for s in changes], f, indent=2)
    print("Save!")

with open("action_to_change.json", "r") as f:
    action_sets = [set(s) for s in json.load(f)]
    print("Loaded!")

print(len(action_sets))

costs, best_set, best_cost = get_total_costs_for_action_sets(org_domain, action_sets)

# print("\n📊 All Costs:", costs)
print("🏆 Best Set for Change:", best_set)
print("💰 Cost:", best_cost)


