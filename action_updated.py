#!/usr/bin/env python
# Four spaces as indentation [no tabs]

import itertools

class Action:
    def __init__(self, name, parameters, positive_preconditions, negative_preconditions, add_effects, del_effects, conditional_effects=None):
        def deep_convert(x):
            # If x is a list:
            if isinstance(x, list):
                # If it's a list of one element and that element is a string,
                # return a tuple with that string (do not iterate over the string).
                if len(x) == 1 and isinstance(x[0], str):
                    return (x[0],)
                else:
                    # Otherwise, recursively convert each element.
                    return tuple(deep_convert(item) for item in x)
            # If x is a tuple, convert its elements.
            elif isinstance(x, tuple):
                return tuple(deep_convert(item) for item in x)
            else:
                # Otherwise (if x is a string or another primitive), return it as is.
                return x

        self.name = name
        self.parameters = tuple(parameters)
        self.positive_preconditions = set(deep_convert(p) for p in positive_preconditions)
        self.negative_preconditions = set(deep_convert(p) for p in negative_preconditions)
        self.add_effects = set(deep_convert(p) for p in add_effects)
        self.del_effects = set(deep_convert(p) for p in del_effects)
        self.conditional_effects = set((deep_convert(cond), deep_convert(effect))
                                       for cond, effect in (conditional_effects or []))

    def __str__(self):
        return f"""action: {self.name}
    parameters: {list(self.parameters)}
    positive_preconditions: {list(self.positive_preconditions)}
    negative_preconditions: {list(self.negative_preconditions)}
    add_effects: {list(self.add_effects)}
    del_effects: {list(self.del_effects)}
    conditional_effects: {list(self.conditional_effects)}
"""

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def groundify(self, objects, types):
        if not self.parameters:
            yield self
            return
        type_map = []
        variables = []
        for var, typ in self.parameters:
            type_stack = [typ]
            items = []
            while type_stack:
                t = type_stack.pop()
                if t in objects:
                    items += objects[t]
                if t in types:
                    type_stack += types[t]
            type_map.append(items)
            variables.append(var)
        for assignment in itertools.product(*type_map):
            positive_preconditions = self.replace(self.positive_preconditions, variables, assignment)
            negative_preconditions = self.replace(self.negative_preconditions, variables, assignment)
            add_effects = self.replace(self.add_effects, variables, assignment)
            del_effects = self.replace(self.del_effects, variables, assignment)
            conditional_effects = self.replace_conditional(self.conditional_effects, variables, assignment)
            yield Action(self.name, assignment, positive_preconditions, negative_preconditions, add_effects, del_effects, conditional_effects)

    def replace(self, group, variables, assignment):
        new_group = []
        for pred in group:
            pred = list(pred)
            for i, p in enumerate(pred):
                if p in variables:
                    pred[i] = assignment[variables.index(p)]
            new_group.append(pred)
        return new_group

    def replace_conditional(self, group, variables, assignment):
        new_group = []
        for cond, effect in group:
            cond = self.replace([cond], variables, assignment)[0]
            effect = self.replace([effect], variables, assignment)[0]
            new_group.append((tuple(cond), tuple(effect)))
        return new_group
