#!/usr/bin/env python3
# Four spaces as indentation [no tabs]

import itertools


def freeze(x):
    """
    Recursively convert lists/tuples into tuples so the structure becomes hashable
    (required to store predicates/effects inside Python sets).
    """
    if isinstance(x, list):
        return tuple(freeze(i) for i in x)
    if isinstance(x, tuple):
        return tuple(freeze(i) for i in x)
    return x


def set_of_tuples(data):
    """
    Convert a list of predicate-like lists into a set of (possibly nested) tuples.

    Example:
      ['p', ['a','b']] -> ('p', ('a','b'))  (hashable)
    """
    return set(freeze(t) for t in data)


class Action:
    # -----------------------------------------------
    # Initialize
    # -----------------------------------------------
    def __init__(self, name, parameters, positive_preconditions, negative_preconditions, add_effects, del_effects):
        self.name = name

        # Parameters are a tuple so they are hashable if needed
        # Expected format: [['?x','type'], ...] or [('?x','type'), ...]
        self.parameters = tuple(freeze(parameters))

        # Preconditions / Effects stored as sets of tuples for fast membership/diff operations
        self.positive_preconditions = set_of_tuples(positive_preconditions)
        self.negative_preconditions = set_of_tuples(negative_preconditions)
        self.add_effects = set_of_tuples(add_effects)
        self.del_effects = set_of_tuples(del_effects)

    # -----------------------------------------------
    # to String
    # -----------------------------------------------
    def __str__(self):
        # Convert nested tuples back to lists for readable printing
        def thaw(x):
            if isinstance(x, tuple):
                return [thaw(i) for i in x]
            return x

        return (
            "action: " + self.name +
            "\n  parameters: " + str(thaw(self.parameters)) +
            "\n  positive_preconditions: " + str([thaw(i) for i in self.positive_preconditions]) +
            "\n  negative_preconditions: " + str([thaw(i) for i in self.negative_preconditions]) +
            "\n  add_effects: " + str([thaw(i) for i in self.add_effects]) +
            "\n  del_effects: " + str([thaw(i) for i in self.del_effects]) + "\n"
        )

    # -----------------------------------------------
    # Equality
    # -----------------------------------------------
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    # -----------------------------------------------
    # Groundify
    # -----------------------------------------------
    def groundify(self, objects, types):
        if not self.parameters:
            yield self
            return

        type_map = []
        variables = []

        # parameters format assumed: (var, type)
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
            yield Action(self.name, assignment, positive_preconditions, negative_preconditions, add_effects, del_effects)

    # -----------------------------------------------
    # Replace
    # -----------------------------------------------
    def replace(self, group, variables, assignment):
        new_group = []
        for pred in group:
            # pred is a tuple (maybe nested); convert to list for substitution
            pred_list = list(pred)
            for i, p in enumerate(pred_list):
                if p in variables:
                    pred_list[i] = assignment[variables.index(p)]
            new_group.append(pred_list)
        return new_group


# -----------------------------------------------
# Main
# -----------------------------------------------
if __name__ == "__main__":
    a = Action(
        "move",
        [["?ag", "agent"], ["?from", "pos"], ["?to", "pos"]],
        [["at", "?ag", "?from"], ["adjacent", "?from", "?to"]],
        [["at", "?ag", "?to"]],
        [["at", "?ag", "?to"]],
        [["at", "?ag", "?from"]],
    )
    print(a)

    objects = {
        "agent": ["ana", "bob"],
        "pos": ["p1", "p2"],
    }
    types = {"object": ["agent", "pos"]}

    for act in a.groundify(objects, types):
        print(act)
