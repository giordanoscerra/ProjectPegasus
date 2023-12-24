from utils.KBwrapper import *

def test_init():
    kb = KBwrapper()
    assert kb is not None

def test_query_for_no_action():
    kb = KBwrapper()
    action = kb.query_for_action()
    assert action is None

def print_dynamic_predicates():
    kb = KBwrapper()
    all_predicates = list(kb.queryDirectly("predicate_property(P, dynamic)"))
    print(all_predicates)

test_init()
test_query_for_no_action()