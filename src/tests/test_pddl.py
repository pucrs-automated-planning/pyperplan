from pddl.pddl import Type, Predicate, Domain, Problem, PDDLWriter
from pddl.parser import Parser
from pddl.lisp_parser import parse_lisp_iterator


def test_type():
    test = Type("test", "parent")
    assert (str(test) == repr(test))


def test_predicate():
    test = Predicate("test", list(("a", list())))
    assert (str(test) == repr(test))


def test_domain():
    test = Domain('domain', dict(), list(), list(), dict())
    assert (str(test) == repr(test))


def test_problem():
    domain = Domain('domain', dict(), list(), list(), dict())
    test = Problem('problem', domain, dict(), list(), list())
    assert (str(test) == repr(test))


def test_writer_simple():
    domain = Domain('domain1', {}, [], [], {})
    problem = Problem('problem1', domain, dict(), list(), list())
    writer = PDDLWriter()
    # print(writer.write_domain(domain))
    # print(writer.write_problem(problem))


def test_writer_complex():
    test = ["""
        (define (domain BLOCKS)
      (:requirements :strips :typing)
      (:types block)
      (:predicates (on ?x - block ?y - block)
                   (ontable ?x - block)
                   (clear ?x - block)
                   (handempty)
                   (holding ?x - block)
                   )

      (:action pick-up
                 :parameters (?x - block)
                 :precondition (and (clear ?x) (ontable ?x) (handempty))
                 :effect
                 (and (not (ontable ?x))
                       (not (clear ?x))
                       (not (handempty))
                       (holding ?x)))

      (:action put-down
                 :parameters (?x - block)
                 :precondition (holding ?x)
                 :effect
                 (and (not (holding ?x))
                       (clear ?x)
                       (handempty)
                       (ontable ?x)))
      (:action stack
                 :parameters (?x - block ?y - block)
                 :precondition (and (holding ?x) (clear ?y))
                 :effect
                 (and (not (holding ?x))
                       (not (clear ?y))
                       (clear ?x)
                       (handempty)
                       (on ?x ?y)))
      (:action unstack
                 :parameters (?x - block ?y - block)
                 :precondition (and (on ?x ?y) (clear ?x) (handempty))
                 :effect
                 (and (holding ?x)
                       (clear ?y)
                       (not (clear ?x))
                       (not (handempty))
                       (not (on ?x ?y)))))
        """,
            """
                (define (problem BLOCKS-4-0)
                (:domain BLOCKS)
                (:objects D B A C - block)
                (:INIT (CLEAR C) (CLEAR A) (CLEAR B) (CLEAR D) (ONTABLE C) (ONTABLE A)
                (ONTABLE B) (ONTABLE D) (HANDEMPTY))
                (:goal (AND (ON D C) (ON C B) (ON B A)))
                )
                """
            ]
    parser = Parser(None)
    parser.domInput = test[0]
    parser.probInput = test[1]
    domain = parser.parse_domain(False)
    problem = parser.parse_problem(domain,False)
    writer = PDDLWriter()
    domain_string = writer.write_domain(domain)
    # print(domain_string)
    parser.domInput = domain_string
    domain = parser.parse_domain(False) # Checking if our output is valid pddl
    assert domain is not None
    # print(writer.write_domain(domain))
    # assert domain_string == writer.write_domain(domain)
    print(writer.write_problem(problem))
