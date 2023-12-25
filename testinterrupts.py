from utils.agent import Agent
# from utils.map import Map

def test_get_carrot():
    agent = Agent()
    agent.kb._kb.asserta("position(comestible,carrot,1,1)")
    print("any carrots in the map? " + str(bool(agent.kb.queryDirectly('position(comestible,carrot,1,1)'))))
    print("carrots in inventory: " + str(list(agent.kb.queryDirectly('carrots(X)'))))
    print("stepping on a carrot? " + str(bool(agent.kb.queryDirectly('stepping_on(agent,carrot,_)'))))
    agent.kb._kb.asserta("hostile(steed)")
    print("is the steed hostile? " + str(bool(agent.kb.queryDirectly('hostile(steed)'))))
    agent.current_subtask = agent.kb.query_for_action()
    print("inferred subtask: " + agent.current_subtask)
    print("Interrupt it? " + str(agent.check_interrupt()))
    agent.kb._kb.retractall("position(comestible,carrot,_,_)")
    print("all the carrots vanished!")
    print("Interrupt it? " + str(agent.check_interrupt()))

def test_get_saddle():
    agent = Agent()
    agent.kb._kb.asserta("position(applicable,saddle,1,1)")
    print("any saddles in the map? " + str(bool(agent.kb.queryDirectly('position(applicable,saddle,_,_)'))))
    print("saddles in inventory: " + str(list(agent.kb.queryDirectly('saddles(X)'))))
    print("stepping on a saddle? " + str(bool(agent.kb.queryDirectly('stepping_on(agent,saddle,_)'))))
    agent.kb._kb.asserta("hostile(steed)")
    print("is the steed hostile? " + str(bool(agent.kb.queryDirectly('hostile(steed)'))))
    agent.current_subtask = agent.kb.query_for_action()
    print("inferred subtask: " + agent.current_subtask)
    print("Interrupt it? " + str(agent.check_interrupt()))
    agent.kb._kb.retractall("position(applicable,saddle,_,_)")
    print("all the saddles vanished!")
    print("Interrupt it? " + str(agent.check_interrupt()))

def test_pacify_steed():
    agent = Agent()
    agent.kb._kb.asserta("hostile(steed)")
    print("Is the steed hostile? " + str(bool(agent.kb.queryDirectly('hostile(steed)'))))
    agent.kb._kb.retractall("carrots(_)")
    agent.kb._kb.asserta("carrots(1)")
    print("carrots in inventory: " + str(list(agent.kb.queryDirectly('carrots(X)'))))
    agent.current_subtask = agent.kb.query_for_action()
    print("inferred subtask: " + agent.current_subtask)
    print("Interrupt it? " + str(agent.check_interrupt()))
    agent.kb._kb.retractall("hostile(steed)")
    print("Steed pacified!")
    print("Interrupt it? " + str(agent.check_interrupt()))

def test_feed_steed():
    agent = Agent()
    agent.kb._kb.retractall("carrots(X)")
    agent.kb._kb.asserta("carrots(1)")
    print("carrots in inventory: " + str(list(agent.kb.queryDirectly('carrots(X)'))))
    agent.current_subtask = agent.kb.query_for_action()
    print("inferred subtask: " + agent.current_subtask)
    print("Interrupt it? " + str(agent.check_interrupt()))
    agent.kb._kb.retractall("carrots(X)")
    agent.kb._kb.asserta("carrots(0)")
    print("No more carrots!")
    print("Interrupt it? " + str(agent.check_interrupt()))

def test_ride_steed():
    agent = Agent()
    agent.current_subtask = agent.kb.query_for_action()
    print("inferred subtask: " + agent.current_subtask)
    print("Interrupt it? " + str(agent.check_interrupt()))
    agent.kb._kb.asserta("hostile(steed)")
    print("the steed is now hostile!")
    print("Interrupt it? " + str(agent.check_interrupt()))

# uncomment the interrupt(s) you wish to test!

# test_get_carrot()
# test_pacify_steed()
# test_get_saddle()
# test_feed_steed()
# test_ride_steed()