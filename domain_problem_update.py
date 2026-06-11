import re
import os

def transform_cause_fault_actions(input_file: str, output_file: str) -> None:
    """
    Reads a PDDL domain file, transforms all `cause_fault_*` action effect predicates
    into conditional effects, and writes the result to a new file.
    """
    def transform_predicate(predicate: str) -> str:
        stripped = predicate.strip()
        return f"(when (not {stripped}) (and {stripped} (exe-{stripped[1:-1]})))"

    def process_pddl_text_strict(content: str) -> str:
        pattern = r"\(:action\s+(cause_fault_[^\s]+)(.*?):effect\s*\(and(.*?)\)\s*\)\s*\)"

        def transform_action(match):
            name = match.group(1)
            body = match.group(2)
            effects = match.group(3)

            # Extract predicates from the effect block
            predicates = re.findall(r"\([^\(\)]+\)", effects)

            transformed = []
            increase = []
            for pred in predicates:
                if "increase" in pred:
                    increase.append(pred)
                else:
                    transformed.append(transform_predicate(pred))

            all_effects = transformed + increase
            effect_block = "(and\n" + "\n".join(f"\t\t\t{e}" for e in all_effects) + "\n\t\t)"
            return f"(:action {name}{body}:effect {effect_block})"

        return re.sub(pattern, transform_action, content, flags=re.DOTALL)

    # Read and process file
    with open(input_file, "r") as f:
        content = f.read()

    modified_content = process_pddl_text_strict(content)

    with open(output_file, "w") as f:
        f.write(modified_content)

    print(f"Transformed PDDL written to: {output_file}")


def add_cost_to_actions(domain_file, output_file=None):
    """
    Reads a PDDL domain file and adds the predicate (increase (total-cost) 1)
    at the end of every action's effect section (inside the (and ... ) block),
    except for actions whose name starts with "exe-to-checked".

    Assumes that each action is formatted like:

    (:action action_name
         :parameters (…)
         :precondition (and …)
         :effect 
    (and
         (predicate1)
         (predicate2)
         … 
    )
    )

    Args:
        domain_file (str): Path to the input domain.pddl file.
        output_file (str, optional): If provided, writes the updated content here.

    Returns:
        str: The updated domain file content.
    """
    with open(domain_file, 'r') as f:
        domain_content = f.read()

    # This regex matches an entire action definition,
    # capturing in:
    #   group(1): the entire action definition
    #   group(2): the action name
    #   group(3): the content inside the effect block (i.e. between “(and” and the newline+closing “)”).
    action_pattern = re.compile(
        r'(\(:action\s+([^\s:]+)\s*'
        r':parameters\s*\([^)]*\)\s*'
        r':precondition\s*\(.*?\)\s*'
        r':effect\s*\(and(.*?)\n\s*\)\s*\))',
        re.DOTALL
    )

    def add_cost_if_needed(match):
        full_action = match.group(1)
        action_name = match.group(2)
        effect_body = match.group(3).strip()
        
        # Do not change actions starting with "exe-to-checked"
        if action_name.startswith("exe-to-checked"):
            return full_action
        
        # Ensure the cost predicate is added at the last position before the closing paren.
        updated_effect = effect_body.rstrip() + "\n    (increase (total-cost) 1)"
        
        # Replace only the effect block, ensuring proper formatting.
        new_action = full_action.replace(effect_body, updated_effect, 1)
        return new_action

    updated_content = action_pattern.sub(add_cost_if_needed, domain_content)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(updated_content)

    return updated_content



def add_total_cost_function(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    new_lines = []
    predicates_block = False
    function_added = False

    for i, line in enumerate(lines):
        new_lines.append(line)

        # Detect the start of predicates block
        if '(:predicates' in line:
            predicates_block = True

        # Detect the end of predicates block and insert functions after the entire block
        if predicates_block and line.strip() == ')':
            predicates_block = False
            if not function_added:
                new_lines.append('(:functions  \n    (total-cost)\n  )\n')
                function_added = True

    # Write the updated lines back to the file
    with open(file_path, 'w') as file:
        file.writelines(new_lines)

#V2

def split_top_level_sexpressions(s):
    """
    Splits a string containing S-expressions into a list of top-level expressions.
    For example, given a string "(p) (q (r))", returns ["(p)", "(q (r))"].
    """
    exprs = []
    current = []
    level = 0
    in_expr = False
    i = 0
    while i < len(s):
        char = s[i]
        if char == '(':
            if level == 0:
                # start of a new top-level expression
                current = []
            level += 1
            current.append(char)
        elif char == ')':
            current.append(char)
            level -= 1
            if level == 0:
                exprs.append(''.join(current).strip())
        else:
            if level > 0:
                current.append(char)
        i += 1
    return exprs

def convert_pddl_action(action_str):
    """
    Convert a PDDL action to add conditional effects for all predicates containing "fault".
    
    The function expects an action in the form:
    
    (:action ACTION_NAME
      :parameters (...)
      :precondition (...)
      :effect
       (and
         EFFECT1
         EFFECT2
         ...))
    
    For every top-level effect item that contains "fault", it is replaced with a conditional effect:
      (when (not EFFECT) (and EFFECT (exe-<inner-of-EFFECT>)))
    
    Args:
        action_str (str): The original PDDL action string
    
    Returns:
        str: Converted PDDL action string with conditional effects.
    """
    # Parse the main components of the action.
    action_pattern = re.compile(
        r'\(:action\s+([^\s:]+)'               # Action name
        r'\s*:parameters\s*\(([^)]*)\)'        # Parameters
        r'\s*:precondition\s*(\(.*?\))'        # Precondition
        r'\s*:effect\s*(\(.*\))',              # Effect (the entire effect block)
        re.DOTALL
    )
    match = action_pattern.search(action_str)
    if not match:
        return action_str  # Return unchanged if the pattern does not match.
    
    action_name = match.group(1).strip()
    parameters = match.group(2).strip()
    precondition = match.group(3).strip()
    original_effect = match.group(4).strip()
    
    # Expecting original_effect in the form: (and ... )
    inner = original_effect.strip()
    if inner.startswith('(') and inner.endswith(')'):
        inner = inner[1:-1].strip()  # remove outer parentheses
    if inner.startswith('and'):
        inner = inner[3:].strip()    # remove the "and" keyword
    
    # Split the remaining content into top-level S-expressions.
    effect_items = split_top_level_sexpressions(inner)
    
    new_effect_list = []
    for effect in effect_items:
        # For every predicate that includes "fault", build a conditional effect.
        if "has-fault-" in effect:
            # Remove the outer parentheses for constructing the exe- version.
            inner_effect = effect.strip()
            if inner_effect.startswith('(') and inner_effect.endswith(')'):
                inner_effect = inner_effect[1:-1].strip()
            condition_effect = (
                f"(when (not {effect})\n"
                f"      (and {effect}\n"
                f"           (exe-{inner_effect})))"
            )
            new_effect_list.append(condition_effect)
        else:
            new_effect_list.append(effect)
    
    # Rebuild the effect block.
    new_effect_block = "(and\n" + "\n".join("    " + e for e in new_effect_list) + "\n)"
    
    # Construct the new action string.
    new_action_str = (
        f"(:action {action_name}\n"
        f" :parameters ({parameters})\n"
        f" :precondition {precondition}\n"
        f" :effect\n"
        f"  {new_effect_block}\n)"
    )
    return new_action_str

def add_conditional_effect_to_domain(input_file, output_file=None):
    """
    Convert a complete PDDL domain file by transforming actions.
    
    For each action, if its effect block contains any predicate with the substring "fault",
    the predicate is wrapped with a conditional effect.
    
    Args:
        input_file (str): Path to the input domain.pddl file.
        output_file (str, optional): Path to save the converted domain file.
    
    Returns:
        str: Converted domain file content.
    """
    with open(input_file, 'r') as f:
        domain_content = f.read()
    
    # Find all action blocks.
    action_pattern = re.compile(
        r'\(:action\s+[^\s:]+\s*:parameters\s*\([^)]*\)\s*:precondition\s*\(.*?\)\s*:effect\s*\(.*?\)\s*\)',
        re.DOTALL
    )
    actions = action_pattern.findall(domain_content)
    
    converted_actions = {}
    for action in actions:
        converted_action = convert_pddl_action(action)
        converted_actions[action] = converted_action
    
    # Replace the original actions with the converted actions.
    for original, converted in converted_actions.items():
        domain_content = domain_content.replace(original, converted)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(domain_content)
    
    return domain_content

# V1
# def convert_pddl_action(action_str):
#     """
#     Convert PDDL action to add conditional effects for faults in the action name.
    
#     Args:
#         action_str (str): The original PDDL action string
    
#     Returns:
#         str: Converted PDDL action string with conditional effects
#     """
#     # Regular expression to parse PDDL action structure
#     action_pattern = re.compile(
#         r'\(:action\s+([^\s:]+)'               # Action name
#         r'\s*:parameters\s*\(([^)]*)\)'        # Parameters
#         r'\s*:precondition\s*(\(.*?\))'        # Precondition
#         r'\s*:effect\s*(\(.*?\)\s*\))',        # Effect (captures everything inside the effect block)
#         re.DOTALL                         # Allows matching across multiple lines
#     )
    
#     # Match the action string
#     match = action_pattern.search(action_str)
#     if not match:
#         return action_str  # Return unchanged if no match is found
    
#     # Extract components
#     action_name = match.group(1).strip()
#     # print(f"action_name:",action_name)
#     parameters = match.group(2).strip()
#     # print(f"parameters:",parameters)
#     precondition = match.group(3).strip()
#     # print(f"precondition:",precondition)
#     original_effect = match.group(4).strip()
#     # print(f"original_effect:",original_effect)
#     # print("===============")
#     # Parse original effects
#     # Parse original effects
#     effect_items = re.findall(r'\(([^()]+)\)', original_effect)
    
#     # Construct new conditional effects
#     new_effects = []
#     for effect in effect_items:
#         if "fault" in effect:  # Only convert effects containing "fault"
#             condition_effect = (
#                 f"  (when (not ({effect}))\n"
#                 f"          (and ({effect})\n"
#                 f"              (exe-{effect})))"
#             )
#             new_effects.append(condition_effect)
#         else:
#             # Keep the original effect unchanged
#             new_effects.append(f"({effect})")
    
#     # Construct the new action string in a PDDL-like format
#     new_action_str = (
#         f"(:action {action_name}\n"
#         f" :parameters ({parameters})\n"
#         f" :precondition {precondition}\n"
#         f" :effect\n"
#         f"  (and\n"
#         + "\n".join(f"    {effect}" for effect in new_effects) +
#         f"\n  )"
#     )
#     # print(f"new_action_str:",new_action_str)
#     return new_action_str

#V1
# def add_conditional_effect_to_domain(input_file, output_file=None):
#     """
#     Convert a complete PDDL domain file by transforming actions.
    
#     Args:
#         input_file (str): Path to the input domain.pddl file
#         output_file (str, optional): Path to save the converted domain file
    
#     Returns:
#         str: Converted domain file content
#     """
#     # Read the input file
#     with open(input_file, 'r') as f:
#         domain_content = f.read()
    
#     # Find all action blocks
#     action_pattern = re.compile(
#     r'\(:action\s+[^\s:]+\s*:parameters\s*\([^)]*\)\s*:precondition\s*\(.*?\)\s*:effect\s*\(.*?\)\s*\)', 
#     re.DOTALL
#     )
#     actions = action_pattern.findall(domain_content)
#     # print(len(actions))
    
#     # Convert each action
#     converted_actions = {}
#     for action in actions:
#         converted_action = convert_pddl_action(action)
#         f"(:converted_action {converted_action}"
#         converted_actions[action] = converted_action
    
#     # Replace original actions with converted actions
#     for original, converted in converted_actions.items():
#         domain_content = domain_content.replace(original, converted)
    
#     # If output file is specified, write the converted content
#     if output_file:
#         with open(output_file, 'w') as f:
#             f.write(domain_content)
    
#     return domain_content


def modify_problem_file(problem_file, output_file=None):
    """
    Reads a PDDL problem file, removes existing goal predicates, and adds:
      - (:goal) as an empty goal clause
      - (:metric minimize (total-cost)) after the goal
      - (= (total-cost) 0) at the end of the :init section after all predicates

    Args:
        problem_file (str): Path to the input problem.pddl file.
        output_file (str, optional): Path to write the updated problem file.

    Returns:
        str: The updated problem file content.
    """
    # Step 1: Read the problem file content
    with open(problem_file, 'r') as f:
        problem_content = f.read()

    # Step 2: Remove existing goal predicates and replace with empty (:goal)
    goal_pattern = re.compile(r'\(:goal\s*\(.*?\)\s*\)', re.DOTALL)
    updated_content = goal_pattern.sub('(:goal )', problem_content)

    # Step 3: Add (:metric minimize (total-cost)) after the empty goal
    metric_pattern = re.compile(r'\(:goal \)')
    updated_content = metric_pattern.sub('(:goal )\n(:metric minimize (total-cost))', updated_content)

    # Step 4: Add (= (total-cost) 0) at the end of the :init section after all predicates
    def add_total_cost_to_init(match):
        init_block = match.group(1).strip()
        if '(= (total-cost) 0)' not in init_block:
            # Append (= (total-cost) 0) at the very end of the :init section
            updated_init = init_block + '\n(= (total-cost) 0)'
            return f'(:init \n{updated_init}\n)'
        return match.group(0)  # If already present, return unchanged

    # Update :init section by adding total-cost at the end
    updated_content = re.sub(r'\(:init\s*(.*?)\n\)', add_total_cost_to_init, updated_content, flags=re.DOTALL)

    # Step 5: Ensure there are no extra closing parentheses at the end
    updated_content = re.sub(r'\)\s*\)\s*$', ')', updated_content.strip())

    # Step 6: Write to output file if specified
    if output_file:
        with open(output_file, 'w') as f:
            f.write(updated_content)

    return updated_content

import re

def modify_problem_file_for_whatIf(problem_file, output_file=None):
    """
    Safely modifies a PDDL problem file to:
    - Add (= (total-cost) 0) in :init section if not present
    - Add (:metric minimize (total-cost)) after the :goal section if not present
    """
    with open(problem_file, 'r') as f:
        lines = f.readlines()

    output_lines = []
    in_init = False
    in_goal = False
    paren_count = 0
    goal_inserted = False
    metric_added = False
    init_modified = False

    for line in lines:
        stripped = line.strip()

        # Track when we're inside the :init block
        if stripped.startswith("(:init"):
            in_init = True
            paren_count = stripped.count('(') - stripped.count(')')
        elif in_init:
            paren_count += stripped.count('(') - stripped.count(')')
            if not init_modified and paren_count == 0:
                if '(= (total-cost) 0)' not in ''.join(lines):
                    output_lines.append("  (= (total-cost) 0)\n")
                in_init = False
                init_modified = True

        # Track when we're inside the :goal block
        if stripped.startswith("(:goal"):
            in_goal = True
            paren_count = stripped.count('(') - stripped.count(')')
        elif in_goal:
            paren_count += stripped.count('(') - stripped.count(')')
            if paren_count == 0 and not goal_inserted:
                in_goal = False
                goal_inserted = True
                output_lines.append(line)
                if not any(":metric minimize (total-cost)" in l for l in lines):
                    output_lines.append("(:metric minimize (total-cost))\n")
                continue

        output_lines.append(line)

    # Save to file if needed
    if output_file:
        with open(output_file, 'w') as f:
            f.writelines(output_lines)

    return ''.join(output_lines)


def add_exe_check_predicates_to_domain(domain_file, output_file=None):
    """
    Reads a PDDL domain file and, in the :predicates section, adds new predicates
    for each predicate whose name starts with "fault". For each such predicate, two
    new predicates are added: one with the name "exe-" + original and another with 
    "check-" + original.
    
    Args:
        domain_file (str): Path to the input domain file.
        output_file (str, optional): If provided, writes the updated domain content to this file.
    
    Returns:
        str: The updated domain file content.
    """
    with open(domain_file, 'r') as f:
        content = f.read()

    # Find the predicates section.
    # This regex captures three groups:
    #   1. The opening of the predicates section, including "(:predicates" and the newline.
    #   2. Everything in between (the inner content listing the predicates).
    #   3. The closing parenthesis (on its own line or with whitespace).
    predicates_section_pattern = re.compile(r'(\(:predicates\s*\n)(.*?)(\n\s*\))', re.DOTALL)
    m = predicates_section_pattern.search(content)
    if not m:
        # No predicates section found; return content unchanged.
        return content

    prefix = m.group(1)
    inner = m.group(2)
    suffix = m.group(3)

    # Find all predicate names in the inner section.
    # Assumes predicates are written as: (predicate_name [optional arguments...])
    predicate_pattern = re.compile(r'\(\s*([^\s()]+)')
    existing_predicates = set(predicate_pattern.findall(inner))

    # Prepare new predicates for every predicate starting with "fault"
    new_predicates = []
    for pred in existing_predicates:
        if pred.startswith("fault_"):
            # print("Yes")
            new_exe = "exe-" + pred
            new_check = "check-" + pred
            if new_exe not in existing_predicates:
                new_predicates.append(f"    ({new_exe})")
            if new_check not in existing_predicates:
                new_predicates.append(f"    ({new_check})")

    if new_predicates:
        # Append the new predicates at the end of the inner section.
        new_inner = inner.rstrip() + "\n" + "\n".join(new_predicates) + "\n"
        new_predicates_section = prefix + new_inner + suffix
        # Replace the old predicates section with the new one in the file content.
        new_content = content[:m.start()] + new_predicates_section + content[m.end():]
    else:
        new_content = content

    # Write to output_file if provided.
    if output_file:
        with open(output_file, 'w') as f:
            f.write(new_content)
    return new_content

def add_conversion_actions_to_domain(domain_file, output_file=None):
    """
    Reads a PDDL domain file, finds all predicates whose names start with "fault-",
    and creates new conversion actions. For each such predicate, an action is added:
      - Name: conv-to-checked-<fault predicate>
      - Precondition: (and
                         (exe-<fault predicate>)
                       )
      - Effect: (and
                  (check-<fault predicate>)
                  (<fault predicate>)
                )
    
    The new actions are inserted into the domain file just before the final closing parenthesis.
    All existing actions and domain content remain intact.
    
    Args:
        domain_file (str): Path to the input domain file.
        output_file (str, optional): If provided, writes the updated domain content to this file.
    
    Returns:
        str: The updated domain file content.
    """
    # Read the domain file content.
    with open(domain_file, 'r') as f:
        content = f.read()
        # print(content)
    
    # Find the predicates section.
    # This regex captures:
    #  1. The opening part: "(:predicates" and newline.
    #  2. The inner content listing the predicates.
    #  3. The closing parenthesis of the predicates section.
    predicates_section_pattern = re.compile(r'(\(:predicates\s*\n)(.*?)(\n\s*\))', re.DOTALL)
    m = predicates_section_pattern.search(content)
    if not m:
        print("No predicates section found!")
        return content

    inner = m.group(2)
    # Extract predicate names from the predicates section.
    # This assumes predicates are defined like: (predicate_name ... )
    predicate_pattern = re.compile(r'\(\s*([^\s()]+)')
    existing_predicates = set(predicate_pattern.findall(inner))
    
    # Create conversion actions for each predicate whose name starts with "fault-"
    new_actions = []
    for pred in existing_predicates:
        if pred.startswith("fault_"):
            # print("Yes")
            new_action = (
                f"    (:action conv-to-checked-{pred}\n"
                f"         :parameters ()\n"
                f"         :precondition (and\n"
                f"                   (exe-{pred})\n"
                f"                 )\n"
                f"         :effect (and\n"
                f"                   (check-{pred})\n"
                # f"                   ({pred})\n"  
                f"                 )\n"
                f"    )\n"
            )
            new_actions.append(new_action)
    
    if new_actions:
        # Insert the new actions before the final closing parenthesis.
        content = content.rstrip()
        if content.endswith(")"):
            content = content[:-1]  # Remove the final ')'
        content += "\n" + "".join(new_actions) + ")\n"  # Append new actions and re-add final ')'
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(content)
    
    return content

def add_exe_to_checked_actions_with_cost(domain_file, output_file=None):
    """
    Reads a PDDL domain file and for every predicate that starts with "fault_",
    creates a new action with:
      - Name: exe-to-checked-<fault predicate>
      - Precondition: (and
                        (not (exe-<fault predicate>))
                      )
      - Effect: (and
                    (check-<fault predicate>)
                    (<fault predicate>)
                    (increase (total-cost) 1000)
                  )
    
    The new actions are appended to the domain file content (keeping the rest of the domain intact)
    just before the final closing parenthesis.
    
    Args:
        domain_file (str): Path to the input domain file.
        output_file (str, optional): Path to the output domain file.
    
    Returns:
        str: The updated domain file content.
    """
    # Read the domain file content.
    with open(domain_file, 'r') as f:
        content = f.read()

    # Locate the predicates section.
    # This regex captures three groups:
    #  1. The start of the predicates section (including "(:predicates" and following newline)
    #  2. The inner content listing the predicates.
    #  3. The closing parenthesis (with any leading whitespace).
    predicates_section_pattern = re.compile(r'(\(:predicates\s*\n)(.*?)(\n\s*\))', re.DOTALL)
    m = predicates_section_pattern.search(content)
    if not m:
        print("No predicates section found!")
        return content

    inner = m.group(2)
    # Extract predicate names from the predicates section.
    # Assumes predicates are defined like: (predicate_name ... )
    predicate_pattern = re.compile(r'\(\s*([^\s()]+)')
    existing_predicates = set(predicate_pattern.findall(inner))
    
    # Filter for fault predicates (those starting with "fault-")
    fault_predicates = [pred for pred in existing_predicates if pred.startswith("fault_")]

    # Create new actions for each fault predicate.
    new_actions = []
    for fault in fault_predicates:
        new_action = (
            f"    (:action exe-to-checked-{fault}\n"
            f"         :parameters ()\n"
            f"         :precondition (and\n"
            f"                   (not (exe-{fault}))\n"
            f"                 )\n"
            f"         :effect (and\n"
            f"                   (check-{fault})\n"
            # f"                   ({fault})\n"
            f"                   (increase (total-cost) 1000)\n"
            f"                 )\n"
            f"    )\n"
        )
        new_actions.append(new_action)

    if new_actions:
        # Insert the new actions before the final closing parenthesis.
        content = content.rstrip()
        if content.endswith(")"):
            content = content[:-1]  # Remove the final ')'
        content += "\n" + "".join(new_actions) + ")\n"  # Append new actions and re-add final ')'
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(content)
    
    return content

def replace_goal_with_only_check_predicates(domain_file, problem_file, output_file=None):
    """
    Reads a PDDL domain file and a PDDL problem file. It extracts all predicate names from the 
    domain's predicates section that start with "check-" and replaces the entire goal clause 
    in the problem file with ONLY these predicates using an AND conjunction.

    Args:
        domain_file (str): Path to the domain.pddl file.
        problem_file (str): Path to the problem.pddl file.
        output_file (str, optional): If provided, writes the updated problem content to this file.

    Returns:
        str: The updated problem file content.
    """
    # ----- Step 1: Extract check predicates from the domain file -----
    with open(domain_file, 'r') as f:
        domain_content = f.read()
    
    # Locate the predicates section (spanning multiple lines).
    predicates_section_pattern = re.compile(r'\(:predicates\s*(.*?)\n\)', re.DOTALL)
    m = predicates_section_pattern.search(domain_content)
    if not m:
        print("No predicates section found in the domain file!")
        return None
    
    predicates_inner = m.group(1)
    
    # Extract predicate names (assumes predicates are defined like: (predicate_name ...))
    predicate_pattern = re.compile(r'\(\s*([^\s()]+)')
    all_predicates = set(predicate_pattern.findall(predicates_inner))
    
    # Filter for those starting with "check-"
    # check_predicates = [pred for pred in all_predicates if pred.startswith("fault_") or pred.startswith("fault-") or pred.startswith("fault")]
    check_predicates = [pred for pred in all_predicates if pred.startswith("check-")]


    
    if not check_predicates:
        print("No check predicates found in the domain file.")
        with open(problem_file, 'r') as f:
            return f.read()
    
    # Prepare new goal conjuncts (one per line with proper indentation)
    new_goal_conjuncts = "\n".join("    (" + pred + ")" for pred in sorted(check_predicates))
    
    # ----- Step 2: Locate and replace the goal clause in the problem file -----
    with open(problem_file, 'r') as f:
        problem_content = f.read()
    
    # Adjusted regex to handle empty goal clauses as well.
    goal_pattern = re.compile(r'\(:goal\s*(\(.*?\)|)\)', re.DOTALL)
    goal_match = goal_pattern.search(problem_content)
    
    if not goal_match:
        print("No goal clause found in the problem file!")
        return problem_content

    # Construct the new goal clause containing only the check predicates.
    new_goal_expr = f"(:goal (and\n{new_goal_conjuncts}\n))"
    
    # Replace the entire goal clause with the new one.
    updated_problem_content = goal_pattern.sub(new_goal_expr, problem_content, count=1)
    
    # Write the updated problem file if an output file is provided.
    if output_file:
        with open(output_file, 'w') as f:
            f.write(updated_problem_content)
    
    return updated_problem_content



def main():

    #Domain file update for extended RG with cond-eff
    # domain_file = 'RG_ext/est_grounded_domain_all_faults-flare.pddl' #input file
    updated_domain = 'RG_ext/est_grounded_domain_all_faults-n3_v5_f5.pddl' #updated domain file
    # add_total_cost_function(domain_file)


    #Add Conditional-Effect to grounded_domain file
    # add_conditional_effect_to_domain(domain_file, updated_domain)

    # #Add "exe" and "check" predicates for faults
    # add_exe_check_predicates_to_domain(domain_file, updated_domain)

    # #Add actions to convert from "exe" to "check" variables
    # add_conversion_actions_to_domain(updated_domain, updated_domain)

    # # #Add actions to convert from not "exe" to "check" with cost variables
    # add_exe_to_checked_actions_with_cost(updated_domain, updated_domain)

    # Add cost=1 to actions
    # add_cost_to_actions(updated_domain, updated_domain)

    # #Problem file update for extended RG with cond-eff
    # problem_file = 'RG_ext/est_grounded_problem-flare.pddl' #input file
    updated_problem = 'RG_ext/est_grounded_problem-n3_v5_f5.pddl' #updated domain file

    # #Remove make the goal empty in the problem file
    # modify_problem_file(problem_file, updated_problem)

    # #Add all faults to the problem file
    replace_goal_with_only_check_predicates(updated_domain, updated_problem, updated_problem)

if __name__ == "__main__":
    main()