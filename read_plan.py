import sys
import os

import re

def extract_node_and_fault_numbers(network_str):
    """
    Extract node and fault numbers from a string like 'n3_v3_f3'.

    Returns:
        tuple: (node_number, fault_number)
    """

    node_match = re.search(r"n(\d+)", network_str)
    fault_match = re.search(r"f(\d+)", network_str)

    if not node_match or not fault_match:
        raise ValueError("Invalid network format. Expected something like 'n3_v3_f3'")

    node_number = int(node_match.group(1))
    fault_number = int(fault_match.group(1))

    return node_number, fault_number

def update_fault_goal(problem_file_path, fault_number, node_number, output_file_path=None):
    """
    Update the fault and node in the (:goal ...) section of a PDDL problem file.

    Parameters:
        problem_file_path (str): Path to input problem.pddl
        fault_number (int or str): Fault number x
        node_number (int or str): Node number y (e.g., 3 -> n3)
        output_file_path (str, optional): If provided, writes output to this file.
                                          Otherwise, overwrites the original file.
    """

    with open(problem_file_path, 'r') as f:
        content = f.read()

    # Construct new goal predicate
    new_goal_predicate = f"(fault_f{fault_number}_occurs_due_to_compromised_node n{node_number})"

    # Regex to match the fault predicate inside (:goal (and ...))
    pattern = re.compile(
        r"\(fault_f\d+_occurs_due_to_compromised_node\s+n\d+\)"
    )

    # Replace old fault predicate with new one
    updated_content = pattern.sub(new_goal_predicate, content, count=1)

    # Write output
    if output_file_path:
        with open(output_file_path, 'w') as f:
            f.write(updated_content)
    else:
        with open(problem_file_path, 'w') as f:
            f.write(updated_content)

def update_problem_goal_given_fault(problem_file_path, new_goals, output_file_path=None):
    """
    Replace the (:goal ...) section of a PDDL problem file with the goal(s) provided.

    Parameters:
        problem_file_path (str): Path to input problem.pddl
        new_goals (str | list[str]):
            - single goal predicate, e.g. "(has-fault-flare-flameout)"
            - OR list of predicates, e.g. ["(p1 ...)", "(p2 ...)"]
        output_file_path (str, optional): If provided, writes to this file;
                                          otherwise overwrites input file.
    """

    with open(problem_file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # ----------------------------
    # Normalize new_goals -> list[str]
    # ----------------------------
    if isinstance(new_goals, str):
        goals_list = [new_goals.strip()]
    elif isinstance(new_goals, list):
        goals_list = [str(g).strip() for g in new_goals]
    else:
        raise TypeError("new_goals must be a string or a list of strings.")

    # Clean each goal and validate basic shape
    cleaned = []
    for g in goals_list:
        g = g.strip()

        # remove accidental quotes
        if (g.startswith('"') and g.endswith('"')) or (g.startswith("'") and g.endswith("'")):
            g = g[1:-1].strip()

        # if user passed without parentheses, wrap it
        if not g.startswith("("):
            g = f"({g})"

        # basic sanity check
        if not g.endswith(")"):
            raise ValueError(f"Goal looks malformed (missing closing ')'): {g}")

        cleaned.append(g)

    # ----------------------------
    # Always build CNF goal: (:goal (and ...))
    # ----------------------------
    goal_body = "(and\n" + "\n".join(f"    {g}" for g in cleaned) + "\n)"
    new_goal_block = f"(:goal {goal_body})"

    # ----------------------------
    # Locate existing (:goal ...) block using parenthesis counting
    # ----------------------------
    start = text.find("(:goal")
    if start == -1:
        raise ValueError("No (:goal ...) block found in problem file.")

    i = start
    depth = 0
    end = None
    while i < len(text):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1

    if end is None:
        raise ValueError("Unbalanced parentheses while parsing (:goal ...) block.")

    # ----------------------------
    # Replace goal and write output
    # ----------------------------
    updated_text = text[:start] + new_goal_block + text[end:]

    out_path = output_file_path or problem_file_path
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(updated_text)


def read_sas_plan(file_path):
    """
    Read a SAS plan file and return a list of actions.

    Args:
        file_path (str): The path to the SAS plan file.

    Returns:
        list: A list of action names.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()

    actions = []
    for line in lines:
        line = line.strip()
        if line.startswith('('):
            action_name = line[1:line.index(' ')]
            actions.append(action_name)

    return actions

def store_sas_plan(file_path, file_dest):
    """
    Copy a SAS plan file to another location as plain text.

    Args:
        file_path (str): The path to the SAS plan file.
        file_dest (str): The path to write the plan text to.

    Returns:
        bool: True if successful, False if the source file does not exist.
    """
    if not os.path.exists(file_path):
        print(f"❌ Source SAS plan file '{file_path}' does not exist.")
        return False

    with open(file_path, 'r') as f:
        lines = f.readlines()

    with open(file_dest, "w") as out_f:
        out_f.writelines(lines)

    print(f"✅ Plan copied to '{file_dest}'.")
    return True

def read_sas_plan_flag(file_path):
    """
    Read a SAS plan file and return a list of actions.
    If no SAS plan exists or no actions are found, return 0.

    Args:
        file_path (str): The path to the SAS plan file.

    Returns:
        list | int: List of action names, or 0 if no plan exists.
    """

    # Case 1: SAS plan file does not exist
    if not os.path.exists(file_path):
        return 0

    with open(file_path, 'r') as f:
        lines = f.readlines()

    actions = []
    for line in lines:
        line = line.strip()
        if line.startswith('(') and ' ' in line:
            action_name = line[1:line.index(' ')]
            actions.append(action_name)

    # Case 2: File exists but no plan/actions found
    if not actions:
        return 0

    return actions

def store_sas_plan_as_txt(file_path, file_dest):
    """
    Read a SAS plan file and return a list of actions.

    Args:
        file_path (str): The path to the SAS plan file.

    Returns:
        list: A list of action names.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()

    #write file
    f = open(file_dest, "w")
    f.writelines(lines)
    f.close()

if __name__ == '__main__':
    # plan_src = sys.argv[1]
    # plan_dest = sys.argv[2]

    #store_sas_plan_as_txt("sas_plan", "copy_plan.txt")
    # 
    network = "n3_v3_f3"

    node, fault = extract_node_and_fault_numbers(network)

    print(node)   # 3
    print(fault)  # 3