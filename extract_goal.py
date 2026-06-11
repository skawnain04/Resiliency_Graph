import re
# from read_plan import read_sas_plan_flag, store_sas_plan, update_fault_goal, extract_node_and_fault_numbers
# from pddl_parser import PDDL_Parser
from subprocess import Popen, PIPE
# import os
# import sys
# from datetime import datetime
# import subprocess

def generate_plan():
    # Set the paths to the FastDownward executable and the PDDL files
    fastdownward_path = "/s/chopin/l/grad/shadaab/Downloads/downward/fast-downward.py"

    #domain and problem file for test
    domain_file = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/RG_ext/org_grounded_domain-flare.pddl"
    problem_file = "temp_problem.pddl"
    # Set the output file path
    output_file = "faults-extract.txt"

    #PLAN
    # Define the search configuration
    search_config = "lama-first"

    # Construct the FastDownward command
    command = [
        fastdownward_path,
        "--alias", 
        search_config,
        domain_file,
        problem_file,
    ]

    print(command)
    # Run the planner
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    # Decode the output
    output = stdout.decode("utf-8")

    # Write the output to a file
    with open(output_file, "w") as file:
        file.write(output)

    print(f"Plan stored in {output_file}")

    # ✅ Detect plan existence
    if "Solution found." in output or "Plan found" in output:
        return True
    else:
        return False

def extract_goal_predicates(problem_pddl_path):
    """
    Extract all goal predicates inside (:goal (and ...)) from a PDDL problem file.
    Robust: uses parenthesis counting instead of regex guessing block end.
    """
    with open(problem_pddl_path, "r", encoding="utf-8") as f:
        text = f.read()

    start = text.find("(:goal")
    if start == -1:
        return []

    # Find the end of the (:goal ...) block using parenthesis matching
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
        return []

    goal_block = text[start:end]  # full "(:goal ...)" section

    # Now extract content inside (and ...)
    and_start = goal_block.find("(and")
    if and_start == -1:
        # could be a single predicate goal like (:goal (p ...))
        # extract the first balanced (...) after (:goal
        inner = goal_block[len("(:goal"):].strip()
        return _extract_top_level_paren_expressions(inner)

    # Find the balanced "(and ...)" expression
    and_expr = goal_block[and_start:]
    and_expr = _extract_first_balanced_expr(and_expr)

    # Strip "(and" and extract predicates inside it
    inside = and_expr[len("(and"):].strip()
    return _extract_top_level_paren_expressions(inside)


def _extract_first_balanced_expr(s):
    """Return the first balanced parenthesized expression from s."""
    depth = 0
    start = None
    for i, ch in enumerate(s):
        if ch == "(":
            if depth == 0:
                start = i
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and start is not None:
                return s[start:i+1]
    return ""


def _extract_top_level_paren_expressions(s):
    """Extract top-level ( ... ) expressions from a string."""
    exprs = []
    depth = 0
    start = None
    for i, ch in enumerate(s):
        if ch == "(":
            if depth == 0:
                start = i
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and start is not None:
                exprs.append(s[start:i+1].strip())
                start = None
    return [e for e in exprs if e]

def replace_problem_goal(problem_in_path, new_goals, problem_out_path):
    """
    Replace the (:goal ...) section of a PDDL problem file and write a new problem file.

    Args:
        problem_in_path (str): input problem.pddl path
        new_goals (str | list[str]): either:
            - a single goal predicate string: "(p ...)"
            - a list of goal predicate strings: ["(p1 ...)", "(p2 ...)", ...]
            - OR a full goal body string like "(and ...)" or "(p ...)"
        problem_out_path (str): output problem.pddl path
    """
    with open(problem_in_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Build goal text
    if isinstance(new_goals, list):
        goal_body = "(and\n" + "\n".join(f"    {g.strip()}" for g in new_goals) + "\n)"
    else:
        s = str(new_goals).strip()
        # If user passed "(and ...)" or "(p ...)" use as-is; otherwise wrap
        goal_body = s if s.startswith("(") else f"({s})"
        if not goal_body.startswith("(and") and "\n" in goal_body:
            # if multi-line but not explicitly (and ...), keep as-is
            pass

    new_goal_block = f"(:goal {goal_body})"

    # Find existing (:goal ...) block by parenthesis matching
    start = text.find("(:goal")
    if start == -1:
        raise ValueError("No (:goal ...) block found in the input problem file.")

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
        raise ValueError("Could not parse the (:goal ...) block (unbalanced parentheses).")

    # Replace and write out
    updated = text[:start] + new_goal_block + text[end:]

    with open(problem_out_path, "w", encoding="utf-8") as f:
        f.write(updated)



if __name__ == '__main__':
    # Example:
    goals = extract_goal_predicates("flare-problem_all_faults.pddl")
    # print(len(goal_list))
    # x = goal_list[:1]
    # print(x[0])

    # replace_problem_goal(
    # "flare-problem_all_faults.pddl",
    # x[0],
    # "problem_single_goal.pddl"
    # )

    x = []
    for goal in goals:
        print(goal)
        replace_problem_goal("/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/problem_single_goal.pddl", goal, "temp_problem.pddl")
        
        if generate_plan():
            print(goal)
            x.append(goal)
            print("Plan found, stopping.")


    for i in x:
        print(i)
    # generate_plan()



