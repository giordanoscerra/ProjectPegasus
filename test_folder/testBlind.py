from utils.map import Map
from utils.agent import Agent



# spawn level WITHOUT PONY.
level = Map(pony=False, level=-1)
agent = Agent()
# this is important af
agent.percept(level)
print("is agent blind? should be false",agent.kb.is_agent_blind())
(agent.kb.assert_blindness())
print("is agent blind? should be true",agent.kb.is_agent_blind())
(agent.kb.retract_blindness())
print("is agent blind? should be false",agent.kb.is_agent_blind())

