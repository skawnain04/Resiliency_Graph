#!/usr/bin/env python
# Four spaces as indentation [no tabs]

import re
from action_updated import Action

class PDDL_Parser:
    SUPPORTED_REQUIREMENTS = [':strips', ':negative-preconditions', ':typing', ':conditional-effects']

    # -----------------------------------------------
    # Tokens
    # -----------------------------------------------

    def scan_tokens(self, filename):
        with open(filename) as f:
            content = re.sub(r';.*', '', f.read(), flags=re.MULTILINE).lower()
        stack = []
        token_list = []
        for t in re.findall(r'[()]|[^\s()]+', content):
            if t == '(':
                stack.append(token_list)
                token_list = []
            elif t == ')':
                if stack:
                    li = token_list
                    token_list = stack.pop()
                    token_list.append(li)
                else:
                    raise Exception('Missing open parentheses')
            else:
                token_list.append(t)
        if stack:
            raise Exception('Missing close parentheses')
        if len(token_list) != 1:
            raise Exception('Malformed expression')
        return token_list[0]

    # -----------------------------------------------
    # Parse domain
    # -----------------------------------------------

    def parse_domain(self, domain_filename, requirements=SUPPORTED_REQUIREMENTS):
        tokens = self.scan_tokens(domain_filename)
        if type(tokens) is list and tokens.pop(0) == 'define':
            self.domain_name = None
            self.requirements = []
            self.types = {}
            self.objects = {}
            self.actions = []
            self.predicates = {}
            self.functions = {}  # Initialize functions dictionary
            while tokens:
                group = tokens.pop(0)
                t = group.pop(0)
                if t == 'domain':
                    self.domain_name = group[0]
                elif t == ':requirements':
                    for req in group:
                        if req not in requirements:
                            raise Exception(f'Requirement {req} not supported')
                    self.requirements = group
                elif t == ':constants':
                    self.parse_objects(group, t)
                elif t == ':predicates':
                    self.parse_predicates(group)
                elif t == ':functions':
                    self.parse_functions(group)
                elif t == ':types':
                    self.parse_types(group)
                elif t == ':action':
                    self.parse_action(group)
                else:
                    self.parse_domain_extended(t, group)
        else:
            raise Exception(f'File {domain_filename} does not match domain pattern')
        
    
    def parse_domain_extended(self, t, group):
        print(str(t) + ' is not recognized in domain')

    
    # -----------------------------------------------
    # Parse functions
    # -----------------------------------------------

    def parse_functions(self, group):
        """
        Parses the :functions section of a PDDL domain file.
        Stores functions in a dictionary with their names and parameters.
        """
        self.functions = {}
        for func in group:
            if isinstance(func, list):
                func_name = func[0]
                parameters = func[1:] if len(func) > 1 else []
            else:
                func_name = func
                parameters = []

            if func_name in self.functions:
                raise Exception(f'Function {func_name} redefined')
            
            self.functions[func_name] = parameters
        
    # -----------------------------------------------
    # Parse objects
    # -----------------------------------------------

    def parse_objects(self, group, name):
        self.parse_hierarchy(group, self.objects, name, False)

    # -----------------------------------------------
    # Parse hierarchy
    # -----------------------------------------------

    def parse_hierarchy(self, group, structure, name, redefine):
        items = []
        while group:
            if redefine and group[0] in structure:
                raise Exception('Redefined supertype of ' + group[0])
            elif group[0] == '-':
                if not items:
                    raise Exception('Unexpected hyphen in ' + name)
                group.pop(0)
                typ = group.pop(0)
                if typ not in structure:
                    structure[typ] = []
                structure[typ] += items
                items = []
            else:
                items.append(group.pop(0))
        if items:
            if 'object' not in structure:
                structure['object'] = []
            structure['object'] += items
    
    # -----------------------------------------------
    # Parse action
    # -----------------------------------------------

    def parse_action(self, group):
        name = group.pop(0)
        parameters = []
        positive_preconditions = []
        negative_preconditions = []
        add_effects = []
        del_effects = []
        conditional_effects = []

        while group:
            t = group.pop(0)
            if t == ':parameters':
                parameters = self.parse_parameters(group.pop(0))
            elif t == ':precondition':
                self.split_predicates(group.pop(0), positive_preconditions, negative_preconditions, name, ' preconditions')
            elif t == ':effect':
                effects = group.pop(0)
                if isinstance(effects, list) and effects[0] == 'and':
                    effects.pop(0)
                else:
                    effects = [effects]

                for effect in effects:
                    if isinstance(effect, list) and effect[0] == 'when':
                        condition = effect[1]
                        effect_predicate = effect[2]
                        conditional_effects.append((condition, effect_predicate))
                    else:
                        if effect[0] == 'not':
                            del_effects.append(effect[1])
                        else:
                            add_effects.append(effect)

        # Ensure conditional_effects are tuples (inner structure remains nested)
        conditional_effects = [(tuple(condition), tuple(effect)) for condition, effect in conditional_effects]

        action = Action(name, parameters, positive_preconditions, negative_preconditions, add_effects, del_effects, conditional_effects)
        self.actions.append(action)

    def parse_parameters(self, group):
        parameters = []
        untyped_parameters = []
        while group:
            t = group.pop(0)
            if t == '-':
                if not untyped_parameters:
                    raise Exception('Unexpected hyphen in parameters')
                param_type = group.pop(0)
                while untyped_parameters:
                    parameters.append([untyped_parameters.pop(0), param_type])
            else:
                untyped_parameters.append(t)
        while untyped_parameters:
            parameters.append([untyped_parameters.pop(0), 'object'])
        return parameters

    # -----------------------------------------------
    # Parse problem
    # -----------------------------------------------

    def parse_problem(self, problem_filename):
        def set_of_tuples(data):
            result = set()
            for t in data:
                if isinstance(t, list) and t[0] == '=':
                    continue  # Skip assignments like (= (total-cost) 0)
                result.add(tuple(t))
            return result

        tokens = self.scan_tokens(problem_filename)
        if type(tokens) is list and tokens.pop(0) == 'define':
            self.problem_name = None
            self.state = set()
            self.assignments = {}  # To handle assignments separately
            self.positive_goals = set()
            self.negative_goals = set()
            self.metric = None  # To handle the metric
            while tokens:
                group = tokens.pop(0)
                t = group.pop(0)
                if t == 'problem':
                    self.problem_name = group[0]
                elif t == ':domain':
                    if not hasattr(self, 'domain_name'):
                        self.domain_name = group[0]
                    elif self.domain_name != group[0]:
                        raise Exception('Different domain specified in problem file')
                elif t == ':requirements':
                    pass  # Ignore requirements in problem, parse them in the domain
                elif t == ':objects':
                    self.parse_objects(group, t)
                elif t == ':init':
                    for item in group:
                        if isinstance(item, list) and item[0] == '=':
                            key = tuple(item[1])
                            value = item[2]
                            self.assignments[key] = value
                        else:
                            self.state.add(tuple(item))
                elif t == ':goal':
                    positive_goals = []
                    negative_goals = []
                    self.split_predicates(group[0], positive_goals, negative_goals, '', ' goals')
                    self.positive_goals = set_of_tuples(positive_goals)
                    self.negative_goals = set_of_tuples(negative_goals)
                elif t == ':metric':
                    self.metric = group  # Store the metric information
                else:
                    self.parse_problem_extended(t, group)
        else:
            raise Exception(f'File {problem_filename} does not match problem pattern')

    def parse_problem_extended(self, t, group):
        print(f'{t} is not recognized in problem')
    
    # -----------------------------------------------
    # Split predicates (Fix for Missing Function)
    # -----------------------------------------------
    
    def split_predicates(self, group, positive, negative, name, part):
        if type(group) is not list:
            raise Exception(f'Error with {name}{part}')
        if group:
            if group[0] == 'and':
                group.pop(0)
            else:
                group = [group]
            for predicate in group:
                if predicate[0] == 'not':
                    if len(predicate) != 2:
                        raise Exception(f'Unexpected not in {name}{part}')
                    negative.append(predicate[-1])
                else:
                    positive.append(predicate)
    
    def parse_predicates(self, group):
        """
        Parses the :predicates section of a PDDL domain file.
        Ensures proper handling of typed and untyped predicates.
        """
        for pred in group:
            predicate_name = pred.pop(0)
            if predicate_name in self.predicates:
                raise Exception(f'Predicate {predicate_name} redefined')
            arguments = {}
            untyped_variables = []
            while pred:
                t = pred.pop(0)
                if t == '-':
                    if not untyped_variables:
                        raise Exception('Unexpected hyphen in predicates')
                    typ = pred.pop(0)
                    while untyped_variables:
                        arguments[untyped_variables.pop(0)] = typ
                else:
                    untyped_variables.append(t)
            while untyped_variables:
                arguments[untyped_variables.pop(0)] = 'object'
            self.predicates[predicate_name] = arguments

    def to_pddl(self, item):
        if isinstance(item, str):
            return item
        elif isinstance(item, (list, tuple)):
            # If every element is a single-character string, join without spaces.
            if all(isinstance(x, str) and len(x) == 1 for x in item):
                return "".join(item)
            else:
                return "(" + " ".join(self.to_pddl(x) for x in item) + ")"
        else:
            return str(item)

    # -----------------------------------------------
    # Generate PDDL output
    # -----------------------------------------------
    
    def generate_pddl_file(self, filename):
        # print("Inside PDDL Writer")
        def write_effects(action, file, indent="            "):
            file.write(f"{indent}(and\n")
            # Write add effects
            for pred in action.add_effects:
                file.write(f"{indent}    {self.to_pddl(pred)}\n")
            # Write delete effects with not wrapper
            for pred in action.del_effects:
                file.write(f"{indent}    (not {self.to_pddl(pred)})\n")
            # Write conditional effects
            for cond, effect in action.conditional_effects:
                if not (isinstance(effect, (list, tuple)) and effect and effect[0] == 'and'):
                    effect = ("and",) + tuple(effect)
                file.write(f"{indent}    (when {self.to_pddl(cond)} {self.to_pddl(effect)})\n")
            file.write(f"{indent})\n")

        with open(filename, "w") as file:
            file.write(f"(define (domain {self.domain_name})\n")
            file.write("    (:requirements\n")
            for req in self.requirements:
                file.write(f"        {req}\n")
            file.write("    )\n")
            file.write("    (:predicates\n")
            for predicate, arguments in self.predicates.items():
                file.write(f"        ({predicate}")
                for arg, arg_type in arguments.items():
                    file.write(f" {arg} - {arg_type}")
                file.write(")\n")
            file.write("    )\n")
            # Insert functions block after predicates
            file.write("    (:functions\n")
            file.write("        (total-cost)\n")
            file.write("    )\n")
            for action in self.actions:
                file.write(f"    (:action {action.name}\n")
                file.write("        :parameters ()\n")
                if action.positive_preconditions or action.negative_preconditions:
                    file.write("        :precondition (and\n")
                    for pred in action.positive_preconditions:
                        file.write(f"            {self.to_pddl(pred)}\n")
                    for pred in action.negative_preconditions:
                        file.write(f"            (not {self.to_pddl(pred)})\n")
                    file.write("        )\n")
                file.write("        :effect\n")
                write_effects(action, file)
                file.write("    )\n")
            file.write(")\n")


    # -----------------------------------------------
    # Remove Action
    # -----------------------------------------------

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


# -----------------------------------------------
# Main
# -----------------------------------------------
if __name__ == '__main__':
    import sys, pprint
    domain = "RG_ext/est_grounded_domain_all_faults-n3_v3_f3.pddl"
    # problem = "Condition-Test/problem_v1.pddl"
    parser = PDDL_Parser()
    # print('---------Parse Domain-------------------')
    # pprint.pprint(parser.scan_tokens(domain))
    # print('---------Parse Problem-------------------')
    # pprint.pprint(parser.scan_tokens(problem))
    print('----------------------------')
    parser.parse_domain(domain)
    print('Domain name: ' + str(parser.domain_name))
    print('----------------------------')
    # print('----------After Parsing Domain.pddl output------------------')
    # parser.generate_pddl_file("RG_ext/test.pddl")
    # parser.parse_problem(problem)
    # print('Problem name: ' + str(parser.problem_name))

    # print('----------Parse Action------------------')
    # for act in parser.actions:
    #     print('----------Name------------------')
    #     print(act.name)
    #     print('----------Parameters------------------')
    #     print(act.parameters)
    #     print('----------Pos Pre-Con------------------')
    #     print(act.positive_preconditions)
    #     print('----------Neg Pre-Con------------------')
    #     print(act.negative_preconditions)
    #     print('----------Add eff------------------')
    #     print(act.add_effects)
    #     print('----------Del eff------------------')
    #     print(act.del_effects)
    #     print('----------Cond eff------------------')
    #     print(act.conditional_effects)

    parser.actions = remove_effect_from_action(parser.actions, 'cause_fault_f3_due_to_compromised_n3', 'fault_f1_occurs_due_to_compromised_node_n3')
    for act in parser.actions:
        print('----------Name------------------')
        print(act.name)
        print('----------Parameters------------------')
        print(act.parameters)
        print('----------Pos Pre-Con------------------')
        print(act.positive_preconditions)
        print('----------Neg Pre-Con------------------')
        print(act.negative_preconditions)
        print('----------Add eff------------------')
        print(act.add_effects)
        print('----------Del eff------------------')
        print(act.del_effects)
        print('----------Cond eff------------------')
        print(act.conditional_effects)

    print('----------After Parsing Domain.pddl output------------------')
    parser.generate_pddl_file("RG_ext/test.pddl")
