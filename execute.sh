#/usr/bin/env bash

# STEP-1: Ground both domain and problem file without all faults:
# python3 grounder/grounder_interface.py domain.pddl problem.pddl original_grounded_domain.pddl original_grounded_problem.pddl

# STEP-2: Ground both domain with all faults:
# python3 grounder/grounder_interface.py domain_faults.pddl problem.pddl copy_grounded_domain_faults.pddl copy_grounded_problem_faults.pddl

# STEP-3: Execute plan original and store it to a .txt file will all details of plan
# python3 execute_plan.py original_grounded_domain.pddl original_grounded_problem.pddl original_output_grounded.txt

# STEP-4: Store the original plan from sas plan to a .txt file
# python3 read_plan.py sas_plan original_plan_grounded.txt

# STEP-5: Execute plan doamin with all faults and store it to a .txt file will all details of plan
# python3 execute_plan.py grounded_domain_faults.pddl grounded_problem_faults.pddl output_copy_grounded.txt

# STEP-6: Store the copy plan from sas plan to a .txt file
# python3 read_plan.py sas_plan copy_plan_grounded.txt

#----------------------------------------------
#/usr/bin/env bash

# STEP-1: Ground both domain and problem file without all faults:
python3 grounder/grounder_interface.py domain_all_faults-flare.pddl problem-flare.pddl iterative_goal/est_grounded_domain_all_faults-flare.pddl iterative_goal/est_grounded_problem-flare.pddl

# STEP-2: Ground both domain with all faults:
#python3 grounder/grounder_interface.py flare-domain_all_faults.pddl flare-problem.pddl flare-ext_grounded-domain_all_faults.pddl flare-ext_grounded-problem_all_faults.pddl

# # STEP-3: Execute plan original and store it to a .txt file will all details of plan
# python3 execute_plan.py RG_ext/est_grounded_domain_all_faults-n3_v3_f3.pddl RG_ext/est_grounded_problem-n3_v3_f3.pddl RG_ext/plan/output_est-n3_v3_f3.txt

# # STEP-4: Store the original plan from sas plan to a .txt file
# python3 read_plan.py sas_plan original_plan_grounded-n50_v30_f30.txt

# # STEP-5: Execute plan doamin with all faults and store it to a .txt file will all details of plan
# python3 execute_plan.py copy_grounded_domain_faults-n50_v30_f30.pddl copy_grounded_problem_faults-n50_v30_f30.pddl output_copy_grounded-n50_v30_f30.txt

# # STEP-6: Store the copy plan from sas plan to a .txt file
# python3 read_plan.py sas_plan copy_plan_grounded-n50_v30_f30.txt
