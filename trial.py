from pddl_parser_updated import PDDL_Parser

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


if __name__ == '__main__':
    import sys, pprint
    # domain = "original-blocksworld/grounded_domain.pddl"
    grounded_domain_sim = "converted_test.pddl"
    # problem = "original-blocksworld/grounded_problem.pddl"
    parser = PDDL_Parser()
    print('----------------------------')
    parser.parse_domain(grounded_domain_sim)
    print('Domain name: ' + str(parser.domain_name))
    print('----------------------------')
    # parser.parse_problem(problem)
    # print('Domain name: ' + str(parser.domain_name))
    # parser.generate_pddl_file("original-blocksworld/domain_output.pddl")

    
    #Parse Simulator and Estimator
    parser_sim = PDDL_Parser()
    parser_sim.parse_domain(grounded_domain_sim)

    # predicates_remove_from_est = ["fault-clean-room1"]
    # action = "fault-clean-room-1"
    # for j in predicates_remove_from_est:
    #     print("removing extra predicates from EST")
    #     print(action)
    #     print("J")
    #     print(j[0])
    #     parser_sim.actions = remove_effect_from_action(parser_sim.actions, action, j[0])