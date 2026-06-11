#!/usr/bin/env python
# Four spaces as indentation [no tabs]

# This file is part of PDDL Parser, available at <https://github.com/pucrs-automated-planning/pddl-parser>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import re
from action import Action


class PDDL_Parser:
   


    SUPPORTED_REQUIREMENTS = [':strips', ':negative-preconditions', ':typing']

    # -----------------------------------------------
    # Tokens
    # -----------------------------------------------

    def scan_tokens(self, filename):
        with open(filename) as f:
            # Remove single line comments
            str = re.sub(r';.*', '', f.read(), flags=re.MULTILINE).lower()
        # Tokenize
        stack = []
        list = []
        for t in re.findall(r'[()]|[^\s()]+', str):
            if t == '(':
                stack.append(list)
                list = []
            elif t == ')':
                if stack:
                    li = list
                    list = stack.pop()
                    list.append(li)
                else:
                    raise Exception('Missing open parentheses')
            else:
                list.append(t)
        if stack:
            raise Exception('Missing close parentheses')
        if len(list) != 1:
            raise Exception('Malformed expression')
        return list[0]

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
            while tokens:
                group = tokens.pop(0)
                t = group.pop(0)
                if t == 'domain':
                    self.domain_name = group[0]
                elif t == ':requirements':
                    for req in group:
                        if req not in requirements:
                            raise Exception('Requirement ' + req + ' not supported')
                    self.requirements = group
                elif t == ':constants':
                    self.parse_objects(group, t)
                elif t == ':predicates':
                    self.parse_predicates(group)
                elif t == ':types':
                    self.parse_types(group)
                elif t == ':action':
                    self.parse_action(group)
                else: self.parse_domain_extended(t, group)
        else:
            raise Exception('File ' + domain_filename + ' does not match domain pattern')

    def parse_domain_extended(self, t, group):
        print(str(t) + ' is not recognized in domain')

    # -----------------------------------------------
    # Parse hierarchy
    # -----------------------------------------------

    def parse_hierarchy(self, group, structure, name, redefine):
        list = []
        while group:
            if redefine and group[0] in structure:
                raise Exception('Redefined supertype of ' + group[0])
            elif group[0] == '-':
                if not list:
                    raise Exception('Unexpected hyphen in ' + name)
                group.pop(0)
                type = group.pop(0)
                if type not in structure:
                    structure[type] = []
                structure[type] += list
                list = []
            else:
                list.append(group.pop(0))
        if list:
            if 'object' not in structure:
                structure['object'] = []
            structure['object'] += list

    # -----------------------------------------------
    # Parse objects
    # -----------------------------------------------

    def parse_objects(self, group, name):
        self.parse_hierarchy(group, self.objects, name, False)

    # -----------------------------------------------
    # Parse types
    # -----------------------------------------------

    def parse_types(self, group):
        self.parse_hierarchy(group, self.types, 'types', True)

    # -----------------------------------------------
    # Parse predicates
    # -----------------------------------------------

    def parse_predicates(self, group):
        for pred in group:
            predicate_name = pred.pop(0)
            if predicate_name in self.predicates:
                raise Exception('Predicate ' + predicate_name + ' redefined')
            arguments = {}
            untyped_variables = []
            while pred:
                t = pred.pop(0)
                if t == '-':
                    if not untyped_variables:
                        raise Exception('Unexpected hyphen in predicates')
                    type = pred.pop(0)
                    while untyped_variables:
                        arguments[untyped_variables.pop(0)] = type
                else:
                    untyped_variables.append(t)
            while untyped_variables:
                arguments[untyped_variables.pop(0)] = 'object'
            self.predicates[predicate_name] = arguments

    # -----------------------------------------------
    # Parse action
    # -----------------------------------------------

    def parse_action(self, group, action_name_to_remove_effect=None, effect_to_remove=None):
        name = group.pop(0)
        if type(name) is not str:
            raise Exception('Action without name definition')
        for act in self.actions:
            if act.name == name:
                raise Exception('Action ' + name + ' redefined')
        parameters = []
        positive_preconditions = []
        negative_preconditions = []
        add_effects = []
        del_effects = []
        extensions = []
        while group:
            t = group.pop(0)
            if t == ':parameters':
                if type(group) is not list:
                    raise Exception('Error with ' + name + ' parameters')
                parameters = []
                untyped_parameters = []
                p = group.pop(0)
                while p:
                    t = p.pop(0)
                    if t == '-':
                        if not untyped_parameters:
                            raise Exception('Unexpected hyphen in ' + name + ' parameters')
                        ptype = p.pop(0)
                        while untyped_parameters:
                            parameters.append([untyped_parameters.pop(0), ptype])
                    else:
                        untyped_parameters.append(t)
                while untyped_parameters:
                    parameters.append([untyped_parameters.pop(0), 'object'])
            elif t == ':precondition':
                self.split_predicates(group.pop(0), positive_preconditions, negative_preconditions, name, ' preconditions')
            elif t == ':effect':
                self.split_predicates(group.pop(0), add_effects, del_effects, name, ' effects')
            else:
                group.insert(0, t)
                extensions.append(group)
        action = Action(name, parameters, positive_preconditions, negative_preconditions, add_effects, del_effects)
        
        # Remove the specified effect if the action name matches
        if action_name_to_remove_effect and name == action_name_to_remove_effect:
            effect_to_remove = tuple(effect_to_remove)
            if effect_to_remove in add_effects:
                add_effects.remove(effect_to_remove)
            elif effect_to_remove in del_effects:
                del_effects.remove(effect_to_remove)
            else:
                print(f"Warning: Effect {effect_to_remove} not found in action {name}")
            action.add_effects = add_effects
            action.del_effects = del_effects

        self.parse_action_extended(action, extensions)
        self.actions.append(action)

    def parse_action_extended(self, action, group):
        while group:
            t = group.pop(0)
            print(str(t) + ' is not recognized in action ' + action.name)

    # -----------------------------------------------
    # Parse problem
    # -----------------------------------------------

    def parse_problem(self, problem_filename):
        def set_of_tuples(data):
            return set([tuple(t) for t in data])
        tokens = self.scan_tokens(problem_filename)
        if type(tokens) is list and tokens.pop(0) == 'define':
            self.problem_name = None
            self.state = set()
            self.positive_goals = set()
            self.negative_goals = set()
            while tokens:
                group = tokens.pop(0)
                t = group.pop(0)
                if t == 'problem':
                    self.problem_name = group[0]
                elif t == ':domain':
                    if self.domain_name != group[0]:
                        raise Exception('Different domain specified in problem file')
                elif t == ':requirements':
                    pass  # Ignore requirements in problem, parse them in the domain
                elif t == ':objects':
                    self.parse_objects(group, t)
                elif t == ':init':
                    self.state = set_of_tuples(group)
                elif t == ':goal':
                    positive_goals = []
                    negative_goals = []
                    self.split_predicates(group[0], positive_goals, negative_goals, '', 'goals')
                    self.positive_goals = set_of_tuples(positive_goals)
                    self.negative_goals = set_of_tuples(negative_goals)
                else: self.parse_problem_extended(t, group)
        else:
            raise Exception('File ' + problem_filename + ' does not match problem pattern')

    def parse_problem_extended(self, t, group):
        print(str(t) + ' is not recognized in problem')

    # -----------------------------------------------
    # Split predicates
    # -----------------------------------------------

    def split_predicates(self, group, positive, negative, name, part):
        if type(group) is not list:
            raise Exception('Error with ' + name + part)
        if group:
            if group[0] == 'and':
                group.pop(0)
            else:
                group = [group]
            for predicate in group:
                if predicate[0] == 'not':
                    if len(predicate) != 2:
                        raise Exception('Unexpected not in ' + name + part)
                    negative.append(predicate[-1])
                else:
                    positive.append(predicate)
    
    def hello_world():
        print("Hello!!!")

    # -----------------------------------------------
    # output.pddl
    # -----------------------------------------------
    def generate_pddl_file(self, filename):
        def write_predicates(predicates, file):
            file.write("    (:predicates\n")
            for predicate, arguments in predicates.items():
                file.write(f"        ({predicate}")
                for arg, arg_type in arguments.items():
                    file.write(f" {arg} - {arg_type}")
                file.write(")\n")
            file.write("    )\n")
        
        def write_action(action, file):
            file.write(f"    (:action {action.name}\n")
            file.write("        :parameters()\n")
            for param, param_type in action.parameters:
                file.write(f"            ({param} - {param_type})\n")
            file.write("        :precondition\n")
            write_predicates_list(action.positive_preconditions, action.negative_preconditions, file, "            ")
            file.write("        :effect\n")
            write_predicates_list(action.add_effects, action.del_effects, file, "            ")
            file.write("    )\n")
        
        def write_predicates_list(positive, negative, file, indent):
            if positive or negative:
                file.write(f"{indent}(and\n")
                for pred in positive:
                    pred_str = str(pred).replace("'", "").replace(",", "")
                    file.write(f"{indent}    {pred_str}\n")
                for pred in negative:
                    pred_str = str(pred).replace("'", "").replace(",", "")
                    file.write(f"{indent}    (not {pred_str})\n")
                file.write(f"{indent})\n")
            else:
                file.write(f"{indent}()\n")

        with open(filename, "w") as file:
            file.write(f"(define (domain {self.domain_name})\n")
            file.write("    (:requirements\n")
            for req in self.requirements:
                file.write(f"        {req}\n")
            file.write("    )\n")
            if self.types:
                file.write("    :types\n")
                for type_name, subtypes in self.types.items():
                    file.write(f"        {type_name}")
                    if subtypes:
                        file.write(" - " + " ".join(subtypes))
                    file.write("\n")
            # if self.objects:
            #     file.write("    :constants\n")
            #     for obj_type, objects in self.objects.items():
            #         for obj in objects:
            #             file.write(f"        {obj} - {obj_type}\n")
            write_predicates(self.predicates, file)
            for action in self.actions:
                write_action(action, file)
            file.write(")\n")
   

def remove_effect_from_action(parsed_actions, action, effect):
    flag=0
    for act in parsed_actions:
        print('----------Action Name------------------')
        print(act.name)
        if act.name == action:
            print("I am inside pickup")
            for x in act.add_effects:
                print(x)
                print(x[0])
                if x[0] == effect:
                    remove_tuple=x
                    flag=1
                if flag==1:
                    act.add_effects.discard(remove_tuple)
                    print("Removed tuple")
                    print(act.add_effects)
                    break
                print("loop x")
    
    return parsed_actions
    

    


# -----------------------------------------------
# Main
# -----------------------------------------------
if __name__ == '__main__':
    import sys, pprint
    domain = "original-blocksworld/grounded_domain.pddl"
    problem = "original-blocksworld/grounded_problem.pddl"
    parser = PDDL_Parser()
    # remove_effect_from_action('cook', 'dinner')
    print('----------------------------')
    # pprint.pprint(parser.scan_tokens(domain))
    print('----------------------------')
    # pprint.pprint(parser.scan_tokens(problem))
    print('----------------------------')
    parser.parse_domain(domain)
    print('Domain name: ' + str(parser.domain_name))
    print('----------------------------')
    # print('----------After Parsing Domain.pddl output------------------')
    # parser.generate_pddl_file("output.pddl")
    parser.parse_problem(problem)
    print('Domain name: ' + str(parser.domain_name))
    
    parser.actions = remove_effect_from_action(parser.actions, 'pick-up_b', 'holding_b')
    print('----------After Parsing Domain.pddl output------------------')
    parser.generate_pddl_file("original-blocksworld/domain_output.pddl")
    
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



    
    # print('----------After Parsing Domain.pddl output------------------')
    # parser.generate_pddl_file("output.pddl")

    domain = "original-blocksworld/domain_output.pddl"
    problem = "original-blocksworld/grounded_problem.pddl"
    parser = PDDL_Parser()
    # remove_effect_from_action('cook', 'dinner')
    print('----------------------------')
    # pprint.pprint(parser.scan_tokens(domain))
    print('----------------------------')
    # pprint.pprint(parser.scan_tokens(problem))
    print('----------------------------')
    parser.parse_domain(domain)
    print('Domain name: ' + str(parser.domain_name))
    print('----------------------------')
    # print('----------After Parsing Domain.pddl output------------------')
    # parser.generate_pddl_file("output.pddl")
    
    
    # print('----------------------------')
    # print('Problem name: ' + str(parser.problem_name))
    # print('Objects: ' + str(parser.objects))
    # print('State: ' + str([list(i) for i in parser.state]))
    # print('Positive goals: ' + str([list(i) for i in parser.positive_goals]))
    # print('Negative goals: ' + str([list(i) for i in parser.negative_goals]))