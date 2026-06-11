# from subprocess import Popen, PIPE
# import os
# import sys

# # fastdownward_path = "/s/chopin/l/grad/shadaab/Downloads/downward-release-22.06.0/fast-downward.py"

# # #domain and problem file for test
# # domain_file = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/grounded_domain.pddl"
# # problem_file = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/grounded_problem.pddl"
# # # Set the output file path
# # output_file = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/output_grounded.txt"

# # #PLAN
# # # Define the search configuration
# # search_config = "lama-first"

# # # Construct the FastDownward command
# # command = [
# #     fastdownward_path,
# #     "--alias", 
# #     search_config,
# #     domain_file,
# #     problem_file,
# # ]

# # print("Command:")
# # print(command)

# # # Run the planner
# # process = Popen(command, stdout=PIPE, stderr=PIPE)
# # stdout, stderr = process.communicate()

# # # Decode the output
# # output = stdout.decode("utf-8")

# # # Write the output to a file
# # with open(output_file, "w") as file:
# #     file.write(output)

# # print(f"Plan stored in {output_file}")

# if __name__ == '__main__':
#     # domain_file = sys.argv[1]
#     # problem_file = sys.argv[2]
#     # output_file = sys.argv[3]

#     # Set the paths to the FastDownward executable and the PDDL files
#     fastdownward_path = "/s/chopin/l/grad/shadaab/Downloads/downward/fast-downward.py"

#     #domain and problem file for test
#     domain_file = "RG_ext/est_grounded_domain_all_faults-n3_v3_f3.pddl"
#     problem_file = "RG_ext/est_grounded_problem-n3_v3_f3.pddl"
#     # # Set the output file path
#     output_file = "RG_ext/plan/output_est-n3_v3_f3.txt"

#     #PLAN
#     # Define the search configuration
#     search_config = "astar(lmcut())"

#     # Construct the FastDownward command
#     command = [
#         fastdownward_path,
#         domain_file,
#         problem_file,
#         "--search",
#         search_config
#     ]

#     print("Command:")
#     print(command)

#     # Run the planner
#     process = Popen(command, stdout=PIPE, stderr=PIPE)
#     stdout, stderr = process.communicate()

#     # Decode the output
#     output = stdout.decode("utf-8")

#     # Write the output to a file
#     with open(output_file, "w") as file:
#         file.write(output)

#     print(f"Plan stored in {output_file}")

import sys
from subprocess import Popen, PIPE

if __name__ == '__main__':
    fastdownward_path = "/s/chopin/l/grad/shadaab/Downloads/downward/fast-downward.py"
    domain_file = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/RG_ext/est_grounded_domain_all_faults-flare.pddl"
    problem_file = "/s/chopin/l/grad/shadaab/Documents/Resiliency_Graph/RG_ext/est_grounded_problem-flare.pddl"
    output_file = "RG_ext/plan/est_flare_manual.txt"

    # Use FF heuristic for conditional effects
    search_config = "astar(ff())"
    
    # Simplified command without time/memory limits for now
    command = [
        fastdownward_path,
        domain_file,
        problem_file,
        "--search",
        search_config
    ]


    print("Command:")
    print(" ".join(command))

    process = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    output = stdout.decode("utf-8")
    errors = stderr.decode("utf-8")

    if "Solution found" in output:
        with open(output_file, "w") as file:
            file.write(output)
        print(f"Plan stored in {output_file}")
    else:
        print("No solution found.")

    if errors:
        print(f"Errors:\n{errors}")

    print(output)