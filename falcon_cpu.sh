#!/bin/bash
#
# Scheduler specific section
# --------------------------
# SBATCH --job-name="RG_ext" 	# a name for your job
# SBATCH --partition=peregrine-cpu	# partition to which job should be submitted
# SBATCH --qos=cpu_short			# qos type
# SBATCH --nodes=1                	# node count
# SBATCH --ntasks=1               	# total number of tasks across all nodes
# SBATCH --cpus-per-task=1        	# cpu-cores per task (>1 if multi-threaded tasks)
# SBATCH --mem-per-cpu=10G         	# memory per cpu-core
# SBATCH --time=10:00:00          	# total run time limit (HH:MM:SS)
# SBATCH --output=n3_v15_f15.out 		# output log file
# SBATCH --error=n3_v15_f15.err  		# error file
# SBATCH --mail-type=begin        	# send email when job begins
# SBATCH --mail-type=end          	# send email when job ends
# SBATCH --mail-user=shadaab@colostate.edu
#
# Job specific section
# -----------------------
module load python/anaconda
srun python3 RG_extention_journal.py 