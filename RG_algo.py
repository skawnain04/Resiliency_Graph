from read_plan import read_sas_plan, store_sas_plan_as_txt
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
    domain_file = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/"+domain
    problem_file = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/"+problem
    # Set the output file path
    output_file = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/"+output

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


def ground_domain_problem(domain, problem, type):
    
    command = [
    "python3",
    "grounder/grounder_interface.py",
    domain,
    problem,
    "performance_evaluation/"+type+"_grounded_"+domain,
    "performance_evaluation/"+type+"_grounded_"+problem
    ]

    # Execute the command
    result = subprocess.run(command, capture_output=True, text=True)

    # Print the output and errors (if any)
    print("Output:")
    print(result.stdout)

    print("Errors:")
    print(result.stderr)

start = datetime.now()

#ground domain and problem for estimator
network = "flare"

domain_estimator = "domain_all_faults-"+network+".pddl"
problem_estimator = "problem-"+network+".pddl"
start_time = datetime.now()
ground_domain_problem(domain_estimator, problem_estimator, "est")
end_time = datetime.now()
time_taken = end_time - start_time

#ground domain and problem for simulator
domain_sim = "domain-"+network+".pddl"
problem_sim = "problem-"+network+".pddl"
start_time = datetime.now()
ground_domain_problem(domain_sim, problem_sim, "org")
end_time = datetime.now()
time_taken = time_taken + (end_time - start_time)

#generate plan for estimator

grounded_domain_estimator = "performance_evaluation/"+"est_grounded_"+domain_estimator
grounded_problem_estimator = "performance_evaluation/"+"est_grounded_"+problem_estimator
output_est_plan_path = "performance_evaluation/"+"output_est-"+network+".txt"
est_plan_path = "performance_evaluation/"+"est_plan-"+network+".txt"

start_time = datetime.now()
generate_plan(grounded_domain_estimator, grounded_problem_estimator, output_est_plan_path)
end_time = datetime.now()
time_taken = time_taken + (end_time - start_time)
store_sas_plan_as_txt("sas_plan", est_plan_path)
estimator_actions  = read_sas_plan(est_plan_path)
print("***Estimated Plan***")
print(estimator_actions)

#generate plan for simulator
grounded_domain_sim = "performance_evaluation/"+"org_grounded_"+domain_sim
grounded_problem_sim = "performance_evaluation/"+"org_grounded_"+problem_sim
output_sim_plan_path = "performance_evaluation/"+"output_org-"+network+".txt"
sim_plan_path = "performance_evaluation/"+"org_plan-"+network+".txt"

start_time = datetime.now()
generate_plan(grounded_domain_sim, grounded_problem_sim, output_sim_plan_path)
end_time = datetime.now()
time_taken = time_taken + (end_time - start_time)
store_sas_plan_as_txt("sas_plan", sim_plan_path)
sim_actions  = read_sas_plan(sim_plan_path)
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
    store_sas_plan_as_txt("sas_plan", est_plan_path)
    estimator_actions  = read_sas_plan(est_plan_path)
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
                print("GOAL REACHED!")
                flag=1
                break
            else:
                print("NO GOAL REACHED!")
        
        i=i+1

    print("***Domain Updated***")
    parser_est.generate_pddl_file(grounded_domain_estimator)
    if flag==1:
        break

    a=a+1


end = datetime.now()
td = (end - start).total_seconds() * 10**3
print(f"The TOTAL time of execution of above program is : {td:.03f}ms")  
tdx = ((end - start)-time_taken).total_seconds() * 10**3
print(f"The time of execution ONLY of above program is : {tdx:.03f}ms") 
print(f"Iteration {a+1}") 



    

