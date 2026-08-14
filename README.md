# Resiliency Graphs for Cyber-Physical Systems

This repository contains the research prototype implementation of the **Resiliency Graph (RG)** framework for analyzing cyber-physical systems (CPS) using automated planning.

Resiliency Graphs connect cyber attacks in the Information Technology (IT) domain with faults and cascading failures in the Operational Technology (OT) domain. The implementation uses **AI planning**, a base system model, and an optimistic planning model to discover attack-fault paths, refine incorrect model assumptions, analyze different fault goals, and identify possible interventions that prevent undesirable system states.

The current implementation uses a **flare system** as the primary case study.

## Repository Overview

The main Python scripts are:

```text
RG_algo.py
RG_algo-iterative-goal-network.py
RG_extention_journal-flare.py
what_if_analysis.py
```

Each script implements a different component or version of the Resiliency Graph analysis.

---

## 1. `RG_algo.py`

This file contains the original iterative Resiliency Graph generation algorithm.

The algorithm works with two planning models:

- **Estimator / optimistic model** — represents the initially assumed system behavior.
- **Simulator / base model** — represents the system behavior used to validate the optimistic model.

The main workflow is:

1. Ground the estimator and simulator PDDL models.
2. Generate a plan from the optimistic model using Fast Downward.
3. Execute the actions against the base model.
4. Compare the resulting optimistic and base states.
5. Detect effects predicted by the optimistic model but unsupported by the base model.
6. Remove those effects from the optimistic model.
7. Replan using the updated model.
8. Repeat until the desired goal is reached.

This iterative refinement produces a planning model whose Resilience paths are consistent with the behavior represented by the base model for a single goal.

The script currently uses the Fast Downward `lama-first` configuration.

---

## 2. `RG_algo-iterative-goal-network.py`

This script extends the RG algorithm by evaluating **multiple goals**.

Instead of running RG for only one fixed goal, the program iterates through all the faults in the associated with a network.

For each combination, it:

1. Creates a new PDDL problem with the corresponding fault goal.
2. Grounds the optimistic and base models.
3. Generates plans for both models.
4. Executes the RG refinement procedure.
5. Updates the optimistic model when unsupported effects are detected.
6. Continues until the corresponding fault goal is validated or no estimator plan exists.

This implementation is useful for systematically generating and evaluating Resiliency Graph paths across multiple possible CPS failure conditions.

The current example configuration uses:

```python
network = "flare"
```

---

## 3. `RG_extention_journal-flare.py`

This file contains the extended RG implementation developed for the journal version of the Resiliency Graph work will covers all faults in the system at one pass instead of iterating over the faults.

Compared with the original implementation, this version includes additional mechanisms for representing and checking optimistic model behavior, including:

- conditional effects,
- `exe-*` predicates,
- `check-*` predicates,
- action-cost manipulation,
- handling of `total-cost`,
- optimistic/base-state comparison,
- removal of unsupported conditional and unconditional effects, and
- repeated replanning after model refinement.

The algorithm maintains a **base model** and an **optimistic model**.

For each generated optimistic plan, actions are checked against the base model. Effects that cannot be reproduced by the base model are removed from the optimistic model. A new plan is then generated from the refined model.

The implementation currently uses:

```text
astar(ff())
```

as the Fast Downward search configuration.

The default case study is the flare system:

```python
network = "flare"
```

---

## 4. `what_if_analysis.py`

This script implements the **what-if analysis / intervention search** component.

Its purpose is to determine which available cyber actions can be removed or disabled so that a target Resilience path or cascading failure is no longer reachable.

The workflow is approximately:

1. Ground the PDDL domain and problem.
2. Assign costs to actions.
3. Add the PDDL `total-cost` function.
4. Configure the problem to minimize total cost.
5. Identify candidate vulnerability-exploitation actions.
6. Generate combinations of candidate actions.
7. Temporarily remove each combination from the planning domain.
8. Run Fast Downward.
9. Determine whether a valid plan still exists.
10. Record action combinations for which no plan exists.
11. Restore the removed actions.
12. Compare intervention costs.
13. Return the minimum-cost intervention set.

The resulting candidate intervention sets are stored in:

```text
action_to_change.json
```

The script finally reports the selected intervention and its total action cost.

---

# Requirements

The code requires Python 3 and an installation of **Fast Downward**.

The scripts also depend on project-specific Python modules, including:

```text
read_plan.py
pddl_parser.py
pddl_parser_updated.py
domain_problem_update.py
```

and the grounding utility:

```text
grounder/grounder_interface.py
```

A typical environment therefore requires:

```text
Python 3.x
Fast Downward
PDDL domain/problem files
Project PDDL parser
Project grounding scripts
```

Most Python packages used directly by these scripts are from the Python standard library, including:

```python
os
sys
subprocess
datetime
itertools
json
re
```

---

# Fast Downward

The implementation uses [Fast Downward](https://www.fast-downward.org/) for automated planning.

Several scripts currently contain a hard-coded path similar to:

```python
fastdownward_path = "/s/chopin/l/grad/shadaab/Downloads/downward/fast-downward.py"
```

Before running the code on another system, change this path to the location of your Fast Downward installation.

For example:

```python
fastdownward_path = "/path/to/downward/fast-downward.py"
```

The scripts also contain hard-coded repository paths such as:

```text
/s/chopin/l/grad/x/Documents/Resiliency_Graph/
```

These paths must also be changed to match the location of the repository on your machine.

A future version of the implementation should move these settings to a configuration file or command-line arguments.

---

# Expected Project Structure

The scripts reference files and directories approximately following this organization:

```text
Resiliency_Graph/
│
├── RG_algo.py
├── RG_algo-iterative-goal-network.py
├── RG_extention_journal-flare.py
├── what_if_analysis.py
│
├── read_plan.py
├── pddl_parser.py
├── pddl_parser_updated.py
├── domain_problem_update.py
│
├── grounder/
│   └── grounder_interface.py
│
├── performance_evaluation/
│
├── iterative_goal/
│
├── RG_ext/
│   └── plan/
│
├── what_if_analysis/
│
├── domain-flare.pddl
├── domain_all_faults-flare.pddl
├── problem-flare.pddl
│
└── ...
```

The exact PDDL files required depend on the experiment being executed.

---

# Running the Code

Clone the repository:

```bash
git clone <repository-url>
cd Resiliency_Graph
```

Update the Fast Downward and repository paths in the Python scripts.

Then run the desired experiment.

### Original RG algorithm

```bash
python3 RG_algo.py
```

### Iterative fault/node analysis

```bash
python3 RG_algo-iterative-goal-network.py
```

### Extended journal implementation

```bash
python3 RG_extention_journal-flare.py
```

### What-if intervention analysis

```bash
python3 what_if_analysis.py
```

---

# Reproducibility Notes

Before attempting to reproduce experiments, verify:

1. The correct version of Fast Downward is installed.
2. All required PDDL files are available.
3. The grounding scripts are available.
4. The repository paths in the Python scripts are updated.
5. Required output directories exist.
6. Previous `sas_plan` files are removed when appropriate before starting a new planning experiment.

Because the current implementation was developed as research code, several experimental settings are defined directly inside the Python scripts.

---

# Citation

If you use this implementation in academic work, please cite the corresponding Resiliency Graph publication.

```bibtex
@INPROCEEDINGS{bashir2024,
  author={Bashir, Shadaab Kawnain and Podder, Rakesh and Sreedharan, Sarath and Ray, Indrakshi and Ray, Indrajit},
  booktitle={2024 IEEE 6th International Conference on Trust, Privacy and Security in Intelligent Systems, and Applications (TPS-ISA)}, 
  title={{Resiliency Graphs: Modelling the Interplay between Cyber Attacks and System Failures through AI Planning}}, 
  year={2024},
  volume={},
  number={},
  pages={292-302},
```

# Status

This repository contains an experimental research implementation. Interfaces, file paths, PDDL models, and experiment configurations may change as the research evolves.
