from read_plan import read_sas_plan_flag, store_sas_plan, update_fault_goal, extract_node_and_fault_numbers, update_problem_goal_given_fault
from pddl_parser import PDDL_Parser
from subprocess import Popen, PIPE
import os
import sys
from datetime import datetime
import subprocess

def remove_effect_from_action(parsed_actions, action, effect):
    flag=0
    for act in parsed_actions:
        # print('----------Action Name------------------')
        # print(act.name)
        if act.name == action:
            # print("I am inside pickup")
            for x in act.add_effects:
                # print(x)
                # print(x[0])
                if x[0] == effect:
                    remove_tuple=x
                    flag=1
                if flag==1:
                    act.add_effects.discard(remove_tuple)
                    # print("Removed tuple")
                    # print(act.add_effects)
                    break
                # print("loop x")
    
    return parsed_actions

def current_state_sim(parser, action, sim_state):
    postCond_act = find_postCond(parser, action)
    print("--PostCond of SIM Action--")
    print(postCond_act)
    current_state = sim_state | postCond_act
    # print("Current State of Simulator:")
    # print(current_state)

    return current_state

def find_postCond(parser, action_name):
    for act in parser.actions:
        if act.name==action_name:
            postCond = act.add_effects | act.del_effects
    
    return postCond

def find_preCond(parser, action_name):
    for act in parser.actions:
        if act.name==action_name:
            preCond = act.positive_preconditions | act.negative_preconditions
    
    return preCond

def generate_plan(domain, problem, output):
    # Set the paths to the FastDownward executable and the PDDL files
    fastdownward_path = "/s/chopin/l/grad/shadaab/Downloads/downward/fast-downward.py"

    #domain and problem file for test
    domain_file = domain
    problem_file = problem
    # Set the output file path
    output_file = output

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
        return 1
    else:
        return 0


def ground_domain_problem(domain, problem, type):
    
    command = [
    "python3",
    "grounder/grounder_interface.py",
    domain,
    problem,
    "iterative_goal/"+type+"_grounded_"+domain,
    "iterative_goal/"+type+"_grounded_"+problem
    ]

    # Execute the command
    result = subprocess.run(command, capture_output=True, text=True)

    # Print the output and errors (if any)
    # print("Output:")
    # print(result.stdout)

    print("Errors:")
    print(result.stderr)

# def ground_domain(domain, type):
    
#     command = [
#     "python3",
#     "grounder/grounder_interface.py",
#     domain,
#     "iterative_goal/"+type+"_grounded_"+domain,
#     # "iterative_goal/"+type+"_grounded_"+problem
#     ]

#     # Execute the command
#     result = subprocess.run(command, capture_output=True, text=True)

#     # Print the output and errors (if any)
#     # print("Output:")
#     # print(result.stdout)

#     print("Errors:")
#     print(result.stderr)


count_iter = 0

network = "flare"

# org_faults = [
#     "(has-fault-condensate-presence-in-fg-due-to-compromised_plc-mitsubishi-melsec-q-series)",
#     "(has-fault-defect-on-ignition-system-due-to-compromised_plc-siemens-s7-1200)",
#     "(has-fault-defect-on-ignition-system-due-to-compromised_plc-siemens-s7-300-or-400)",
#     "(has-fault-failure-on-ignition-system-due-to-compromised_plc-siemens-s7-1200)",
#     "(has-fault-failure-on-ignition-system-due-to-compromised_plc-siemens-s7-300-or-400)",
#     "(has-fault-fg-interrupted-at-source-due-to-compromised_plc-yokogawa-stardom)",
#     "(has-fault-flame-detachment-due-to-compromised_plc-allen-bradley-micrologix-1100)",
#     "(has-fault-flame-detachment-due-to-compromised_plc-schneider-electric-modicon-m580)",
#     "(has-fault-flare-flameout)",
#     "(has-fault-instrumental-failure-due-to-compromised_plc-schneider-electric-modicon-m221)",
#     "(has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-yokogawa-stardom)",
#     "(has-fault-low-flow-gas-flaring-due-to-compromised_plc-allen-bradley-micrologix-1100)",
#     "(has-fault-manual-isolation-valve-close-due-to-compromised_plc-allen-brdley-controllogix)",
#     "(has-fault-mechanical-failure-due-to-compromised_plc-schneider-electric-modicon-m221)",
#     "(has-fault-nitrogen-valve-open-due-to-compromised_plc-siemens-s7-1200)",
#     "(has-fault-nitrogen-valve-open-due-to-compromised_plc-siemens-s7-300-or-400)",
#     "(has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-yokogawa-stardom)",
#     "(has-fault-pcv-faulty-due-to-compromised_plc-schneider-electric-modicon-m221)",
#     "(has-fault-pilot-extinction-due-to-compromised_plc-allen-brdley-controllogix)",
#     "(has-fault-pilot-extinction-due-to-compromised_plc-mitsubishi-melsec-q-series)",
#     "(has-fault-pilot-extinction-due-to-compromised_plc-schneider-electric-modicon-m221)",
#     "(has-fault-pilot-extinction-due-to-compromised_plc-siemens-s7-1200)",
#     "(has-fault-pilot-extinction-due-to-compromised_plc-siemens-s7-300-or-400)",
#     "(has-fault-pilot-extinction-due-to-compromised_plc-yokogawa-stardom)",
#     "(has-fault-pilot-low-supply-pressure-due-to-compromised_plc-allen-brdley-controllogix)",
#     "(has-fault-pilot-low-supply-pressure-due-to-compromised_plc-schneider-electric-modicon-m221)",
#     "(has-fault-pilot-low-supply-pressure-due-to-compromised_plc-yokogawa-stardom)",
#     "(has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-mitsubishi-melsec-q-series)",
#     "(has-fault-pipe-not-drained)",
#     "(has-fault-pumping-phenomenon-due-to-compromised_plc-schneider-electric-modicon-m580)",
#     "(has-fault-relief-pcv-closed-to-compromised_plc-allen-bradley-micrologix-1100)",
#     "(has-fault-switching-to-another-flare-due-to-compromised_plc-allen-bradley-micrologix-1100)",
#     "(has-fault-valve-blocked-close-due-to-compromised_plc-allen-brdley-controllogix)",
#     "(has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-schneider-electric-modicon-m580)"
# ]

faults = [
    "(has-fault-condensate-presence-in-fg-due-to-compromised_firewall-vpn)",
    "(has-fault-condensate-presence-in-fg-due-to-compromised_internal-network)",
    "(has-fault-condensate-presence-in-fg-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-condensate-presence-in-fg-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-condensate-presence-in-fg-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-condensate-presence-in-fg-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-condensate-presence-in-fg-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-condensate-presence-in-fg-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-condensate-presence-in-fg-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-condensate-presence-in-fg-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-condensate-presence-in-fg-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-defect-on-ignition-system-due-to-compromised_firewall-vpn)",
    "(has-fault-defect-on-ignition-system-due-to-compromised_internal-network)",
    "(has-fault-defect-on-ignition-system-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-defect-on-ignition-system-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-defect-on-ignition-system-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-defect-on-ignition-system-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-defect-on-ignition-system-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-defect-on-ignition-system-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-defect-on-ignition-system-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-defect-on-ignition-system-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-defect-on-ignition-system-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-failure-on-ignition-system-due-to-compromised_firewall-vpn)",
    "(has-fault-failure-on-ignition-system-due-to-compromised_internal-network)",
    "(has-fault-failure-on-ignition-system-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-failure-on-ignition-system-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-failure-on-ignition-system-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-failure-on-ignition-system-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-failure-on-ignition-system-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-failure-on-ignition-system-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-failure-on-ignition-system-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-failure-on-ignition-system-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-failure-on-ignition-system-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-fg-interrupted-at-source-due-to-compromised_firewall-vpn)",
    "(has-fault-fg-interrupted-at-source-due-to-compromised_internal-network)",
    "(has-fault-fg-interrupted-at-source-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-fg-interrupted-at-source-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-fg-interrupted-at-source-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-fg-interrupted-at-source-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-fg-interrupted-at-source-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-fg-interrupted-at-source-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-fg-interrupted-at-source-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-fg-interrupted-at-source-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-fg-interrupted-at-source-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-flame-detachment-due-to-compromised_firewall-vpn)",
    "(has-fault-flame-detachment-due-to-compromised_internal-network)",
    "(has-fault-flame-detachment-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-flame-detachment-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-flame-detachment-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-flame-detachment-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-flame-detachment-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-flame-detachment-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-flame-detachment-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-flame-detachment-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-flame-detachment-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-flare-flameout)",
    "(has-fault-ignition-pipe-clogged-due-to-compromised_firewall-vpn)",
    "(has-fault-ignition-pipe-clogged-due-to-compromised_internal-network)",
    "(has-fault-ignition-pipe-clogged-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-ignition-pipe-clogged-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-ignition-pipe-clogged-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-ignition-pipe-clogged-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-ignition-pipe-clogged-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-ignition-pipe-clogged-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-ignition-pipe-clogged-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-ignition-pipe-clogged-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-ignition-pipe-clogged-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-instrumental-failure-due-to-compromised_firewall-vpn)",
    "(has-fault-instrumental-failure-due-to-compromised_internal-network)",
    "(has-fault-instrumental-failure-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-instrumental-failure-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-instrumental-failure-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-instrumental-failure-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-instrumental-failure-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-instrumental-failure-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-instrumental-failure-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-instrumental-failure-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-instrumental-failure-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-isolation-of-fg-line-for-works-due-to-compromised_firewall-vpn)",
    "(has-fault-isolation-of-fg-line-for-works-due-to-compromised_internal-network)",
    "(has-fault-isolation-of-fg-line-for-works-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-low-flow-gas-flaring-due-to-compromised_firewall-vpn)",
    "(has-fault-low-flow-gas-flaring-due-to-compromised_internal-network)",
    "(has-fault-low-flow-gas-flaring-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-low-flow-gas-flaring-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-low-flow-gas-flaring-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-low-flow-gas-flaring-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-low-flow-gas-flaring-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-low-flow-gas-flaring-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-low-flow-gas-flaring-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-low-flow-gas-flaring-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-low-flow-gas-flaring-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-manual-isolation-valve-close-due-to-compromised_firewall-vpn)",
    "(has-fault-manual-isolation-valve-close-due-to-compromised_internal-network)",
    "(has-fault-manual-isolation-valve-close-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-manual-isolation-valve-close-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-manual-isolation-valve-close-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-manual-isolation-valve-close-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-manual-isolation-valve-close-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-manual-isolation-valve-close-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-manual-isolation-valve-close-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-manual-isolation-valve-close-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-manual-isolation-valve-close-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-mechanical-failure-due-to-compromised_firewall-vpn)",
    "(has-fault-mechanical-failure-due-to-compromised_internal-network)",
    "(has-fault-mechanical-failure-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-mechanical-failure-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-mechanical-failure-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-mechanical-failure-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-mechanical-failure-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-mechanical-failure-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-mechanical-failure-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-mechanical-failure-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-mechanical-failure-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-nitrogen-valve-open-due-to-compromised_firewall-vpn)",
    "(has-fault-nitrogen-valve-open-due-to-compromised_internal-network)",
    "(has-fault-nitrogen-valve-open-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-nitrogen-valve-open-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-nitrogen-valve-open-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-nitrogen-valve-open-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-nitrogen-valve-open-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-nitrogen-valve-open-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-nitrogen-valve-open-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-nitrogen-valve-open-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-nitrogen-valve-open-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-no-flow-of-fuel-gas-due-to-compromised_firewall-vpn)",
    "(has-fault-no-flow-of-fuel-gas-due-to-compromised_internal-network)",
    "(has-fault-no-flow-of-fuel-gas-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-opertor-fault-due-to-compromised_firewall-vpn)",
    "(has-fault-opertor-fault-due-to-compromised_internal-network)",
    "(has-fault-opertor-fault-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-opertor-fault-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-opertor-fault-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-opertor-fault-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-opertor-fault-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-opertor-fault-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-opertor-fault-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-opertor-fault-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-opertor-fault-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-pcv-faulty-due-to-compromised_firewall-vpn)",
    "(has-fault-pcv-faulty-due-to-compromised_internal-network)",
    "(has-fault-pcv-faulty-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-pcv-faulty-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-pcv-faulty-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-pcv-faulty-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-pcv-faulty-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-pcv-faulty-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-pcv-faulty-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-pcv-faulty-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-pcv-faulty-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-pilot-extinction-due-to-compromised_firewall-vpn)",
    "(has-fault-pilot-extinction-due-to-compromised_internal-network)",
    "(has-fault-pilot-extinction-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-pilot-extinction-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-pilot-extinction-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-pilot-extinction-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-pilot-extinction-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-pilot-extinction-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-pilot-extinction-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-pilot-extinction-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-pilot-extinction-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-pilot-low-supply-pressure-due-to-compromised_firewall-vpn)",
    "(has-fault-pilot-low-supply-pressure-due-to-compromised_internal-network)",
    "(has-fault-pilot-low-supply-pressure-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-pilot-low-supply-pressure-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-pilot-low-supply-pressure-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-pilot-low-supply-pressure-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-pilot-low-supply-pressure-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-pilot-low-supply-pressure-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-pilot-low-supply-pressure-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-pilot-low-supply-pressure-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-pilot-low-supply-pressure-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-pilot-supply-pipe-isolated-due-to-compromised_firewall-vpn)",
    "(has-fault-pilot-supply-pipe-isolated-due-to-compromised_internal-network)",
    "(has-fault-pilot-supply-pipe-isolated-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-pipe-not-drained)",
    "(has-fault-pumping-phenomenon-due-to-compromised_firewall-vpn)",
    "(has-fault-pumping-phenomenon-due-to-compromised_internal-network)",
    "(has-fault-pumping-phenomenon-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-pumping-phenomenon-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-pumping-phenomenon-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-pumping-phenomenon-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-pumping-phenomenon-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-pumping-phenomenon-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-pumping-phenomenon-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-pumping-phenomenon-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-pumping-phenomenon-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-relief-pcv-closed-to-compromised_firewall-vpn)",
    "(has-fault-relief-pcv-closed-to-compromised_internal-network)",
    "(has-fault-relief-pcv-closed-to-compromised_microsoft-windows-12-server)",
    "(has-fault-relief-pcv-closed-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-relief-pcv-closed-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-relief-pcv-closed-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-relief-pcv-closed-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-relief-pcv-closed-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-relief-pcv-closed-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-relief-pcv-closed-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-relief-pcv-closed-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-switching-to-another-flare-due-to-compromised_firewall-vpn)",
    "(has-fault-switching-to-another-flare-due-to-compromised_internal-network)",
    "(has-fault-switching-to-another-flare-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-switching-to-another-flare-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-switching-to-another-flare-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-switching-to-another-flare-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-switching-to-another-flare-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-switching-to-another-flare-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-switching-to-another-flare-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-switching-to-another-flare-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-switching-to-another-flare-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-valve-blocked-close-due-to-compromised_firewall-vpn)",
    "(has-fault-valve-blocked-close-due-to-compromised_internal-network)",
    "(has-fault-valve-blocked-close-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-valve-blocked-close-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-valve-blocked-close-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-valve-blocked-close-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-valve-blocked-close-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-valve-blocked-close-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-valve-blocked-close-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-valve-blocked-close-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-valve-blocked-close-due-to-compromised_plc-yokogawa-stardom)",
    "(has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_firewall-vpn)",
    "(has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_internal-network)",
    "(has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_microsoft-windows-12-server)",
    "(has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-allen-bradley-micrologix-1100)",
    "(has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-allen-brdley-controllogix)",
    "(has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-mitsubishi-melsec-q-series)",
    "(has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-schneider-electric-modicon-m221)",
    "(has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-schneider-electric-modicon-m580)",
    "(has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-siemens-s7-1200)",
    "(has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-siemens-s7-300-or-400)",
    "(has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-yokogawa-stardom)",
]



problem_file = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/iterative_goal/est_grounded_problem-flare.pddl"

start = datetime.now()

for f in faults:
    print(f"----Fault {f}----")
    new_problem_file = "iterative_goal/problem-"+network+"_f"+str(f)+".pddl"
    update_problem_goal_given_fault(problem_file, f, new_problem_file)

    #ground domain and problem for estimator
    # domain_estimator = "domain_all_faults-"+network+".pddl"
    # problem_estimator = new_problem_file
    start_time = datetime.now()
    # ground_domain_problem(domain_estimator, problem_estimator, "est")
    end_time = datetime.now()
    time_taken = end_time - start_time
    domain_estimator = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/iterative_goal/est_grounded_domain_all_faults-flare.pddl"
    problem_estimator = new_problem_file

    #ground domain and problem for simulator
    # domain_sim = "domain-"+network+".pddl"
    # problem_sim = new_problem_file
    start_time = datetime.now()
    # ground_domain_problem(domain_sim, problem_sim, "org")
    end_time = datetime.now()
    time_taken = time_taken + (end_time - start_time)
    domain_sim = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/iterative_goal/org_grounded_domain-flare.pddl"
    problem_sim = new_problem_file

    #generate plan for estimator
    grounded_domain_estimator = domain_estimator
    grounded_problem_estimator = problem_estimator
    output_est_plan_path = "iterative_goal/"+"output_est-"+network+"test.txt"
    est_plan_path = "iterative_goal/"+"est_plan-"+network+"test.txt"

    start_time = datetime.now()
    plan_e = generate_plan(grounded_domain_estimator, grounded_problem_estimator, output_est_plan_path)
    end_time = datetime.now()
    time_taken = time_taken + (end_time - start_time)
    if plan_e==0:
        continue
    store_sas_plan("sas_plan", est_plan_path)
    estimator_actions  = read_sas_plan_flag(est_plan_path)

    if estimator_actions==0:
        print("NO ESTIMATOR PLAN FOUND!")
        continue
    else:
        print("***Estimated Plan***")
        print(estimator_actions)


    #generate plan for simulator
    grounded_domain_sim = domain_sim
    grounded_problem_sim = problem_sim
    output_sim_plan_path = "iterative_goal/"+"output_org-"+network+"test.txt"
    sim_plan_path = "iterative_goal/"+"org_plan-"+network+"test.txt"

    start_time = datetime.now()
    plan_s = generate_plan(grounded_domain_sim, grounded_problem_sim, output_sim_plan_path)
    end_time = datetime.now()
    time_taken = time_taken + (end_time - start_time)
    if plan_s==0:
        continue
    store_sas_plan("sas_plan", sim_plan_path)
    sim_actions  = read_sas_plan_flag(sim_plan_path)
    if sim_actions==0:
        print("NO SIMULATOR PLAN FOUND!")
        # continue
    else:
        print("***Simulator Plan***")
        print(sim_actions)


    ##RG starts
    #Parse Simulator and Estimator
    parser_sim = PDDL_Parser()
    start_time = datetime.now()
    parser_sim.parse_domain(grounded_domain_sim)
    parser_sim.parse_problem(grounded_problem_sim)
    end_time = datetime.now()
    time_taken = time_taken + (end_time - start_time)

    parser_est = PDDL_Parser()
    start_time = datetime.now()
    parser_est.parse_domain(grounded_domain_estimator)
    parser_est.parse_problem(grounded_problem_estimator)
    end_time = datetime.now()
    time_taken = time_taken + (end_time - start_time)

    #initial state of Simulator
    sim_state = parser_sim.state
    print("Initial State of Simulator:")
    # print(sim_state)
    for item in sim_state:
        print(item)
    print("---------------------------")

    #Goal state of Simulator
    pos_goal = parser_sim.positive_goals
    neg_goal = parser_sim.negative_goals
    sim_goal_state = pos_goal | neg_goal

    #initial state of Estimator
    est_state = parser_est.state
    print("Initial State of Estimator:")
    # print(est_state)
    for item in est_state:
        print(item)
    print("---------------------------")

    # Goal state of Estimator
    pos_goal = parser_est.positive_goals
    neg_goal = parser_est.negative_goals
    est_goal_state = pos_goal | neg_goal

    a=0
    flag=0
    while 1:
        print(f"Iteration outside {a}")

        parser_est = PDDL_Parser()
        start_time = datetime.now()
        parser_est.parse_domain(grounded_domain_estimator)
        parser_est.parse_problem(grounded_problem_estimator)
        
        generate_plan(grounded_domain_estimator, grounded_problem_estimator, output_est_plan_path)
        end_time = datetime.now()
        time_taken = time_taken + (end_time - start_time)
        store_sas_plan("sas_plan", est_plan_path)
        estimator_actions  = read_sas_plan_flag(est_plan_path)
        print("***Estimated Plan***")
        print(estimator_actions)

        #Goal state of Estimator
        pos_goal = parser_est.positive_goals
        neg_goal = parser_est.negative_goals
        est_goal_state = pos_goal | neg_goal

        i = 0
        while(len(estimator_actions)>0):
            print(f"Iteration inside {i}")
            
            #Pop actions from Estimator to check the next state of the Simulator
            action = estimator_actions.pop(0)
            print("--POP Action from Estimated plan--")
            print(action)

            preCond_act_est = find_preCond(parser_est, action)
            print("--PreCond of EST Action--")
            print(preCond_act_est)

            is_subset_of_sim = set(preCond_act_est).issubset(set(sim_state))
            
            if is_subset_of_sim:
                print("It is a Subset of SIM")
                sim_state = current_state_sim(parser_sim, action, sim_state)
                print("Current State of Simulator:")
                # print(sim_state)
                for item in sim_state:
                    print(item)
                print("---------------------------")

                #estimator
                postCond_act_est = find_postCond(parser_est, action)
                print("--PostCond of EST Action--")
                print(postCond_act_est)

                est_state = est_state | postCond_act_est
                print("Current State of Estimator:")
                # print(est_state)
                for item in est_state:
                    print(item)
                print("---------------------------")

                if (sim_state!=est_state):
                    predicates_remove_from_est = est_state - sim_state
                    print("Remove Predicates:")
                    print(f"{predicates_remove_from_est} from Action:{action}")
                    
                    #remove predicates from EST action's post condition
                    for j in predicates_remove_from_est:
                        # print("removing extra predicates from EST")
                        # print(action)
                        # print("J")
                        # print(j[0])
                        parser_est.actions = remove_effect_from_action(parser_est.actions, action, j[0])
                    
                    #remove predicates from EST's current state
                    for k in predicates_remove_from_est:
                        est_state.remove(k)
                    
                    # print("Current State of after Removal Estimator:")
                    # # print(est_state)
                    # test = est_state - sim_state
                    # print(test)


                
                #check after modification of all actions is the current state of Estimator State
                is_subset_of_goal = set(est_goal_state).issubset(set(est_state))
                if is_subset_of_goal:
                    print("GOAL REACHED*")
                    flag=1
                    break
                else:
                    print("NO GOAL REACHED!")
            
            i=i+1

        print("***Domain Updated***")
        count_iter = count_iter + 1
        parser_est.generate_pddl_file(grounded_domain_estimator)
        if flag==1:
            break
            
        a=a+1



end = datetime.now()
td = (end - start).total_seconds() * 10**3
print(f"The TOTAL time of execution of above program is : {td:.03f}ms")  
tdx = ((end - start)-time_taken).total_seconds() * 10**3
print(f"The time of execution ONLY of above program is : {tdx:.03f}ms") 
print(f"Iteration {count_iter+1}") 
