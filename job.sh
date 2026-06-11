#!/bin/bash
#
#SBATCH --job-name="RG" 	# a name for your job
#SBATCH --partition=peregrine-cpu	# partition to which job should be submitted
#SBATCH --qos=cpu_short           # qos type
#SBATCH --nodes=1                	# node count
#SBATCH --ntasks=1               	# total number of tasks across all nodes
#SBATCH --cpus-per-task=8        	# cpu-cores per task
#SBATCH --mem-per-cpu=1G         	# memory per cpu-core
#SBATCH --time=24:00:00          	# total run time limit (HH:MM:SS)
#
module purge
module load python/anaconda

srun python3 test_1.py