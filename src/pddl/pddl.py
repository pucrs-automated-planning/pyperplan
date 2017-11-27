#
# This file is part of pyperplan.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#

"""
This module contains all data structures needed to represent a PDDL domain and
possibly a task definition.
"""


class Type:
    """
    This class represents a PDDL type.
    """
    def __init__(self, name, parent):
        self.name = name.lower()
        self.parent = parent

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Predicate:
    def __init__(self, name, signature):
        """
        name: The name of the predicate.
        signature: A list of tuples (name, [types]) to represent a list of
                   parameters and their type(s).
        """
        self.name = name
        self.signature = signature

    def __repr__(self):
        return self.name + str(self.signature)

    def __str__(self):
        return self.name + str(self.signature)


# Formula is unused right now!
#class Formula:
#    def __init__(self, operator, operands=[]):
#        # right now we only need AND
#        self._operator = operator # 'AND' | 'OR' | 'NOT'
#        self._operands = operands
#
#    def getOperator(self):
#        return self._operator
#    operator = property(getOperator)
#
#    def getOperands(self):
#        return self._operands
#    operands = property(getOperands)


class Effect:
    def __init__(self):
        """
        addlist: Set of predicates that have to be true after the action
        dellist: Set of predicates that have to be false after the action
        """
        self.addlist = set()
        self.dellist = set()


class Action:
    def __init__(self, name, signature, precondition, effect):
        """
        name: The name identifying the action
        signature: A list of tuples (name, [types]) to represent a list of
                   parameters an their type(s).
        precondition: A list of predicates that have to be true before the
                      action can be applied
        effect: An effect instance specifying the postcondition of the action
        """
        self.name = name
        self.signature = signature
        self.precondition = precondition
        self.effect = effect


class Domain:
    def __init__(self, name, types, predicates, actions, constants={}):
        """
        name: The name of the domain
        types: A dict of typename->Type instances in the domain
        predicates: A list of predicates in the domain
        actions: A list of actions in the domain
        constants: A dict of name->type pairs of the constants in the domain
        """
        self.name = name
        self.types = types
        self.predicates = predicates
        self.actions = actions
        self.constants = constants

    def __repr__(self):
        return ('< Domain definition: %s Predicates: %s Actions: %s '
                'Constants: %s >' % (self.name,
                                     [str(p) for p in self.predicates],
                                     [str(a) for a in self.actions],
                                     [str(c) for c in self.constants]))

    __str__ = __repr__


class Problem:
    def __init__(self, name, domain, objects, init, goal):
        """
        name: The name of the problem
        domain: The domain in which the problem has to be solved
        objects: A dict name->type of objects that are used in the problem
        init: A list of predicates describing the initial state
        goal: A list of predicates describing the goal state
        """
        self.name = name
        self.domain = domain
        self.objects = objects
        self.initial_state = init
        self.goal = goal

    def __repr__(self):
        return ('< Problem definition: %s '
                'Domain: %s Objects: %s Initial State: %s Goal State : %s >' %
                (self.name, self.domain.name,
                 [self.objects[o].name for o in self.objects],
                 [str(p) for p in self.initial_state],
                 [str(p) for p in self.goal]))

    __str__ = __repr__


class PDDLWriter:

    def __init__(self):
        # 0 - domain name
        # 1 - requirements
        # 2 - types
        # 3 - constants
        # 4 - predicates
        # 5 - actions
        self.domain_template = "(define (domain {0})\n\n" \
                               "  {1}\n\n" \
                               "  {2}\n\n" \
                               "  {3}\n\n" \
                               "  {4}\n\n" \
                               "  {5}" \
                               ")"
        # 0 - problem name
        # 1 - domain name
        # 2 - objects
        # 3 - initial state
        # 4 - goal state
        self.problem_template = "(define (problem {0})\n " \
                                "   (:domain {1})\n" \
                                "   {2}\n" \
                                "   {3}\n" \
                                "   {4}\n" \
                                ")"

        self.requirements_template = "(:requirements {0})"
        self.types_template = "(:types {0})"
        self.constants_template = "(:constants {0})"
        self.predicates_template = "(:predicates {0})"
        self.and_template = "(and {0})"
        self.not_template = "(not {0})"
        # For actions
        # 0 - name
        # 1 - parameters
        # 2 - precondition
        # 3 - effect
        # 4 - cost - not in use
        self.action_template = "(:action {0}" \
                               "   :parameters {1}" \
                               "   :precondition {2}" \
                               "   :effect {3}" \
                               ")"

    def write_requirements(self, domain):
        assert isinstance(domain, Domain)
        requirements = ":strips"
        if domain.types: requirements += " :types"
        return self.requirements_template.format(requirements)

    def write_types(self, domain):
        assert isinstance(domain, Domain)
        if domain.types:
            types = ""
            for t in domain.types:
                types += str(t)+" "
            return self.types_template.format(types)
        else:
            return ""

    def write_constants(self, domain):
        assert isinstance(domain, Domain)
        if domain.constants:
            c_list = ""
            for c in domain.constants:
                c_list += repr(c)+"\n"
            return self.constants_template.format(c_list)
        else:
            return ""

    def write_predicates(self,domain):
        assert isinstance(domain, Domain)
        preds = ""
        for p in domain.predicates:
            preds += " "+self.pddl_predicate(domain.predicates[p])

        return self.predicates_template.format(preds)

    def write_actions(self,domain):
        act = ""
        for a in domain.actions:
            act+=self.pddl_action(domain.actions[a])+"\n\n"
        return act

    def pddl_action(self,action):
        assert isinstance(action, Action)
        # print (str(action.name))
        return self.action_template.format(action.name,
                                           "("+self.pddl_signature(action.signature)+")",
                                           self.pddl_precondition(action.precondition),
                                           self.pddl_effect(action.effect))

    def pddl_signature(self,signature, typed=False):
        sig = ""
        for o in signature:
            sig += " "+(self.pddl_typed_object(o) if typed else self.pddl_untyped_object(o))
        return sig



    def pddl_precondition(self,precondition):
        precond = ""
        for literal in precondition:
            precond += " "+self.pddl_literal(literal)
        return self.and_template.format(precond)

    def pddl_effect(self,effect):
        assert isinstance(effect,Effect)
        eff = ""
        for literal in effect.addlist:
            eff+=" "+self.pddl_literal(literal)
        for literal in effect.dellist:
            eff+=" "+self.pddl_literal(literal,False)
        return self.and_template.format(eff)

    def pddl_predicate(self, predicate):
        assert isinstance(predicate, Predicate)
        pars = self.pddl_signature(predicate.signature, True)
        return "({0} {1})".format(predicate.name, pars)

    def pddl_literal(self, literal, positive=True):
        pars = self.pddl_signature(literal.signature)
        lit = "({0} {1})".format(literal.name, pars)
        if not positive:
            lit = self.not_template.format(lit)
        return lit

    def pddl_untyped_object(self, o):
        return o[0]

    def pddl_typed_object(self, o):
        return "{0} - {1}".format(o[0],o[1][0])

    def write_domain(self, domain):
        assert isinstance(domain, Domain)
        return self.domain_template.format(
            domain.name,
            self.write_requirements(domain),
            self.write_types(domain),
            self.write_constants(domain),
            self.write_predicates(domain),
            self.write_actions(domain))

    def write_problem(self, problem):
        assert isinstance(problem, Problem)
        objects = ""
        for o in problem.objects:
            if problem.domain.types:
                objects += " {0} - {1}\n\t".format(o,str(problem.objects[o]))
            else:
                objects += " " + self.pddl_untyped_object(o)
        objects = "(:objects {0})\n\n".format(objects)
        init = ""
        for literal in problem.initial_state:
            init += " "+self.pddl_literal(literal)
        init = "(:init {0})".format(init)

        goal = ""
        for literal in problem.goal:
            goal += " " + self.pddl_literal(literal)
        goal = "(:goal {0})".format(self.and_template.format(goal))

        return self.problem_template.format(problem.name,
                                            problem.domain.name,
                                            objects,
                                            init,
                                            goal)