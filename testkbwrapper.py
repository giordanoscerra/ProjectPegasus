from utils.KBwrapper import *

def test_init():
    kb = KBwrapper()
    assert kb is not None

def test_query_for_no_action():
    kb = KBwrapper()
    action = kb.query_for_action()
    assert action is None

# need to test if query_for_action() returns the correct action given the KB and the necessary asserts for the action

test_init()
test_query_for_no_action()