from read_plan import read_sas_plan, store_sas_plan_as_txt
from pddl_parser_updated import PDDL_Parser
from subprocess import Popen, PIPE
import os
import sys
from datetime import datetime
import subprocess
import domain_problem_update


def remove_increase_tuples(tuples_set):
    """
    Remove tuples that have the structure ('increase', ('total-cost',), some_value)
    
    Args:
        tuples_set (set): A set of tuples.
        
    Returns:
        set: A new set with the specified tuples removed.
    """
    filtered = {
        t for t in tuples_set 
        if not (len(t) == 3 and t[0] == 'increase' and t[1] == ('total-cost',))
    }
    return filtered


def remove_exe_check_tuples(input_set):
    result_set = set()

    for item in input_set:
        if isinstance(item, tuple) and len(item) > 0:
            element = item[0]
            # Check if the string starts with 'exe' or 'check'
            if not (element.startswith('exe') or element.startswith('check')):
                result_set.add(item)

    return result_set

def remove_effect_from_action(parsed_actions, action_name, effect):
    def effect_matches(eff, effect_to_remove):
        """
        Check if an effect tuple contains effect_to_remove or "exe-" + effect_to_remove.
        For effects starting with 'and', only the subsequent elements are checked.
        For other effects, all tokens in the tuple are checked.
        """
        tokens = []
        if isinstance(eff, tuple):
            if len(eff) > 0 and eff[0] == 'and':
                # Only check tokens after the "and" keyword.
                for elem in eff[1:]:
                    if isinstance(elem, tuple):
                        tokens.extend(elem)
                    elif isinstance(elem, str):
                        tokens.append(elem)
            else:
                # For simple effects, check all elements.
                for elem in eff:
                    if isinstance(elem, tuple):
                        tokens.extend(elem)
                    elif isinstance(elem, str):
                        tokens.append(elem)
        for token in tokens:
            if token == effect_to_remove or token == "exe-" + effect_to_remove:
                return True
        return False

    for act in parsed_actions:
        if act.name == action_name:
            # Remove from unconditional effect if it exists.
            if hasattr(act, 'effect') and act.effect is not None:
                if effect_matches(act.effect, effect):
                    # Reset to a neutral effect; adjust as needed for your representation.
                    act.effect = ('and',)
            # Remove the effect from add effects if present.
            if hasattr(act, 'add_effects'):
                act.add_effects = {eff for eff in act.add_effects if not effect_matches(eff, effect)}
            # Remove matching effects from conditional effects.
            new_cond_effects = set()
            for cond, eff in act.conditional_effects:
                if not effect_matches(eff, effect):
                    new_cond_effects.add((cond, eff))
            act.conditional_effects = new_cond_effects
    return parsed_actions


def current_state_sim(parser, action, sim_state):
    postCond_act = find_postCond(parser, action, type="opt")
    # print("--PostCond of SIM Action--")
    # print(postCond_act)
    current_state = sim_state | postCond_act
    # print("Inside Current State Function")
    # print("Current State of Base:")
    # print(current_state)

    return current_state, postCond_act

def extract_and_tuples(input_set):
    result_set = set()

    for item in input_set:
        # Check if item is a tuple and contains 'and'
        if isinstance(item, tuple):
            for sub_item in item:
                if isinstance(sub_item, tuple) and 'and' in sub_item:
                    # Extract all elements except 'and' and add to result_set
                    for element in sub_item:
                        if element != 'and':
                            result_set.add(element)
                            
    return result_set

def find_postCond(parser, action_name, type):
    for act in parser.actions:
        if act.name==action_name:
            if type=="base":
                postCond = act.add_effects | act.del_effects
                # print((postCond))
            else:
                postCond = act.add_effects | act.del_effects
                # print("Inside Before removing cost Post Condition:-----")
                # print(postCond)
                eff_cond = act.conditional_effects
                # print("Inside Before removing cost Post Condition:-----")
                postCond = remove_increase_tuples(postCond)
                # print((postCond))
                postCond = postCond | extract_and_tuples(eff_cond)
                # print("Inside Before removing Condition-effect Post Condition:-----")
                postCond = remove_increase_tuples(postCond)
                # print(postCond)
            
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

    print(f"Plan generation command:{command}")
    # Run the planner
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    # Decode the output
    output = stdout.decode("utf-8")

    # Write the output to a file
    with open(output_file, "w") as file:
        file.write(output)

    print(f"Plan stored in {output_file}")


def ground_domain_problem(domain, problem, type):
    command = [
    "python3",
    "grounder/grounder_interface.py",
    domain,
    problem,
    "RG_ext/"+type+"_grounded_"+domain,
    "RG_ext/"+type+"_grounded_"+problem
    ]

    # print(f"Command: {command}")
    # Execute the command
    result = subprocess.run(command, capture_output=True, text=True)

    # Print the output and errors (if any)
    # print("Output:")
    # print(result.stdout)

    # print("Errors:")
    # print(result.stderr)


start = datetime.now()

#ground domain and problem for estimator
# network = sys.argv[1]
network = "flare"

# domain_estimator = "domain_all_faults-"+network+".pddl"
# problem_estimator = "problem-"+network+".pddl"
start_time = datetime.now()
# ground_domain_problem(domain_estimator, problem_estimator, "est")
# end_time = datetime.now()
# time_taken = end_time - start_time

#ground domain and problem for Base
# domain_sim = "domain-"+network+".pddl"
# problem_sim = "problem-"+network+".pddl"
# start_time = datetime.now()
# ground_domain_problem(domain_sim, problem_sim, "org")
# end_time = datetime.now()
# time_taken = time_taken + (end_time - start_time)

# #Add Conditional-Effect to grounded_domain file for Optimistic Model
# start_time = datetime.now()
# # domain_estimator = "domain_all_faults-"+network+".pddl"
# domain_estimator = "RG_ext/est_grounded_"+domain_estimator
# print(f"Path:{domain_estimator}")
# domain_problem_update.add_conditional_effect_to_domain(domain_estimator, domain_estimator)
# end_time = datetime.now()
# time_taken = end_time - start_time

# #Add "exe" and "check" predicates for faults
# start_time = datetime.now()
# domain_problem_update.add_exe_check_predicates_to_domain(domain_estimator, domain_estimator)
# end_time = datetime.now()
# time_taken = end_time - start_time

# #Add actions to convert from "exe" to "check" variables
# start_time = datetime.now()
# domain_problem_update.add_conversion_actions_to_domain(domain_estimator, domain_estimator)
# end_time = datetime.now()
# time_taken = end_time - start_time

# #Add actions to convert from "exe" to "check" variables with cost
# start_time = datetime.now()
# domain_problem_update.add_total_cost_function(domain_estimator)
# end_time = datetime.now()
# time_taken = end_time - start_time

# #Add actions to convert from not "exe" to "check" with cost variables
# start_time = datetime.now()
# domain_problem_update.add_exe_to_checked_actions_with_cost(domain_estimator, domain_estimator)
# end_time = datetime.now()
# time_taken = end_time - start_time

# #Add cost=1 to every action
# start_time = datetime.now()
# domain_problem_update.add_cost_to_actions(domain_estimator, domain_estimator)
# end_time = datetime.now()
# time_taken = end_time - start_time

# #Problem file update for extended RG with cond-eff
# start_time = datetime.now()
# # problem_estimator = "problem-"+network+".pddl"
# problem_estimator = "RG_ext/est_grounded_"+problem_estimator
# domain_problem_update.modify_problem_file(problem_estimator, problem_estimator)
# end_time = datetime.now()
# time_taken = end_time - start_time

# #Add all faults to the problem file
# start_time = datetime.now()
# domain_problem_update.replace_goal_with_only_check_predicates(domain_estimator, problem_estimator, problem_estimator)
# end_time = datetime.now()
# time_taken = end_time - start_time


#generate plan for estimator
grounded_domain_estimator = "RG_ext/est_grounded_domain_all_faults-"+network+".pddl"
grounded_problem_estimator = "RG_ext/est_grounded_problem-"+network+".pddl"
output_est_plan_path = "RG_ext/plan/"+"output_est-"+network+".txt"
est_plan_path = "RG_ext/plan/"+"est_plan-"+network+".txt"

#Add "exe" and "check" predicates for faults
start_time = datetime.now()
domain_problem_update.add_exe_check_predicates_to_domain(grounded_domain_estimator, grounded_domain_estimator)
end_time = datetime.now()
time_taken = end_time - start_time

#Add actions to convert from "exe" to "check" variables
start_time = datetime.now()
domain_problem_update.add_conversion_actions_to_domain(grounded_domain_estimator, grounded_domain_estimator)
end_time = datetime.now()
time_taken = end_time - start_time

#Add actions to convert from "exe" to "check" variables with cost
start_time = datetime.now()
domain_problem_update.add_total_cost_function(grounded_domain_estimator)
end_time = datetime.now()
time_taken = end_time - start_time

#Add actions to convert from not "exe" to "check" with cost variables
start_time = datetime.now()
domain_problem_update.add_exe_to_checked_actions_with_cost(grounded_domain_estimator, grounded_domain_estimator)
end_time = datetime.now()
time_taken = end_time - start_time

#Add cost=1 to every action
start_time = datetime.now()
domain_problem_update.add_cost_to_actions(grounded_domain_estimator, grounded_domain_estimator)
end_time = datetime.now()
time_taken = end_time - start_time

# start_time = datetime.now()
# generate_plan(grounded_domain_estimator, grounded_problem_estimator, output_est_plan_path)
end_time = datetime.now()
# # time_taken = time_taken + (end_time - start_time)
time_taken = (end_time - start_time)
# store_sas_plan_as_txt("sas_plan", est_plan_path)
# estimator_actions  = read_sas_plan(est_plan_path)
# print("***Initial Optimistic Plan***")
# print(estimator_actions)

#Base Model Path
grounded_domain_sim = "RG_ext/org_grounded_domain-"+network+".pddl"
grounded_problem_sim = "RG_ext/org_grounded_problem-"+network+".pddl"
output_sim_plan_path = "RG_ext/plan/"+"output_org-"+network+".txt"
sim_plan_path = "RG_ext/plan/"+"org_plan-"+network+".txt"

#No need
# start_time = datetime.now()
# generate_plan(grounded_domain_sim, grounded_problem_sim, output_sim_plan_path)
# end_time = datetime.now()
# time_taken = time_taken + (end_time - start_time)
# store_sas_plan_as_txt("sas_plan", sim_plan_path)
# sim_actions  = read_sas_plan(sim_plan_path)
# print("***Base Plan***")
# print(sim_actions)
# length_base = len(sim_actions)


#RG starts
#Parse Base and Estimator
parser_sim = PDDL_Parser()
start_time = datetime.now()
parser_sim.parse_domain(grounded_domain_sim)
parser_sim.parse_problem(grounded_problem_sim)
end_time = datetime.now()
time_taken = time_taken + (end_time - start_time)

parser_est = PDDL_Parser()
start_time = datetime.now()
print(grounded_domain_estimator)
print(grounded_problem_estimator)
parser_est.parse_domain(grounded_domain_estimator)
parser_est.parse_problem(grounded_problem_estimator)
end_time = datetime.now()
time_taken = time_taken + (end_time - start_time)

#Initial state of Base
# sim_state = parser_sim.state
# print("Initial State of Base:")
# # print(sim_state)
# for item in sim_state:
#     print(item)
# print("---------------------------")

#Goal state of Base
pos_goal = parser_sim.positive_goals
neg_goal = parser_sim.negative_goals
sim_goal_state = pos_goal | neg_goal

# #Initial state of Optimistic Model
# est_state = parser_est.state
# print("Initial State of Optimistic Model:")
# # print(est_state)
# for item in est_state:
#     print(item)
# print("---------------------------")

# # Goal state of Optimistic Model
# pos_goal = parser_est.positive_goals
# neg_goal = parser_est.negative_goals
# est_goal_state = pos_goal | neg_goal
prev_plan= []
prev_sim_state = []
a=0
flag=0
while 1:
    print(f"Iteration outside {a}")

    sim_state = parser_sim.state
    # print("Initial State of Base:")
    # print(sim_state)
    # for item in sim_state:
    #     print(item)
    # print("---------------------------")

    parser_est = PDDL_Parser()
    start_time = datetime.now()
    parser_est.parse_domain(grounded_domain_estimator)
    parser_est.parse_problem(grounded_problem_estimator)

    #Initial state of Optimistic Model
    est_state = parser_est.state
    # print("Initial State of Optimistic Model:")
    # # print(est_state)
    # for item in est_state:
    #     print(item)
    # print("---------------------------")
    
    #Generate Plan for Optimistic Model
    generate_plan(grounded_domain_estimator, grounded_problem_estimator, output_est_plan_path)
    end_time = datetime.now()
    time_taken = time_taken + (end_time - start_time)
    store_sas_plan_as_txt("sas_plan", est_plan_path)
    estimator_actions  = read_sas_plan(est_plan_path)
    print("***Optimistic Inside Loop Model Plan***")
    print(estimator_actions)
    temp_actions = estimator_actions.copy() 
    print(f"Previous Plan {prev_plan} and Est Plan {temp_actions}_1")
    if prev_plan!= estimator_actions:  
        print(f"after check Previous Plan {prev_plan} and Est Plan {temp_actions}_2")
        # print("---Optimistic Model Plan Length---")
        # print(len(estimator_actions))

        #Goal state of Optimistic Model
        pos_goal = parser_est.positive_goals
        neg_goal = parser_est.negative_goals
        est_goal_state = pos_goal | neg_goal

        i = 0
        while(len(estimator_actions)>0):
            print(f"Iteration inside {i}")
            print(f"after check Previous Plan {prev_plan} and Est Plan {temp_actions}_3")
            #Pop actions from Optimistic Model to check the next state of the Base
            action = estimator_actions.pop(0)
            print("--POP Action from Estimated plan--")
            print(action)

            preCond_act_est = find_preCond(parser_est, action)
            # print("--PreCond of EST Action--")
            # print(preCond_act_est)

            is_subset_of_sim = set(preCond_act_est).issubset(set(sim_state))
            
            if is_subset_of_sim:
                print("It is a Subset of SIM")
                prev_sim_state = sim_state.copy()
                sim_state, new_pred_sim = current_state_sim(parser_sim, action, sim_state)
                # print("***Current State of Base***:")
                # # print(sim_state)
                # for item in sim_state:
                #     print(item)
                # print("---------------------------")

                #Optimistic Model
                postCond_act_est = find_postCond(parser_est, action, type="opt")
                # print("--PostCond of EST Action--")
                # print(postCond_act_est)

                #current state of Optimistic Model after executing "action"
                est_state = est_state | postCond_act_est
                # print("Current State of Estimator:")
                # print(est_state)
                # for item in est_state:
                #     print(item)
                # print("---------------------------")

                remove_var_est_state = remove_exe_check_tuples(est_state)

                if (sim_state!=remove_var_est_state):
                    x = sim_state & new_pred_sim
                    y = sim_state - prev_sim_state
                    z =  x | y
                    predicates_remove_from_est = remove_var_est_state - z
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
                        remove_var_est_state.remove(k)
                    
                    # print("Current State of after Removal Estimator:")
                    # # print(est_state)
                    # test = est_state - sim_state
                    # print(test)

                # print("Current State of Estimator Before Checking GOAL:")
                # print(est_state)
                # for item in est_state:
                #     print(item)
                # print("---------------------------")
                
                
                #check after modification of all actions is the current state of Estimator State
                is_subset_of_goal = set(est_goal_state).issubset(set(est_state))
                if is_subset_of_goal:
                    print("GOAL REACHED!")
                    flag=1
                    break;
                else:
                    print("NO GOAL REACHED!")
            i=i+1

        print("***Domain Updated***")
        prev_plan = temp_actions.copy()
        print(f"after domain update Previous Plan {prev_plan} and Est Plan {temp_actions}_4")   
        # print(grounded_domain_estimator)
        parser_est.generate_pddl_file(grounded_domain_estimator)
        # break;
        if flag==1:
            break;

        a=a+1
    else:
        break;


end = datetime.now()
td = (end - start).total_seconds() * 10**3
print(f"The TOTAL time of execution of above program is : {td:.03f}ms")  
tdx = ((end - start)-time_taken).total_seconds() * 10**3
print(f"The time of execution ONLY of above program is : {tdx:.03f}ms") 
print(f"Iteration {a+1}") 
# print(f"Base Plan: {length_base}") 
