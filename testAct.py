from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance
from utils.map import Map
from utils.agent import Agent
from utils import exceptions

# spawn level
level = Map(pony=True, level=0)
agent = Agent()
# this percept could be useless
level.render()

agent.percept(level)
print(f'pony hostile? : {agent.kb.query_hostile()}')
print(f'pony position: {agent.kb.get_element_position_query("pony")}')
print(f'carrot position: {agent.kb.get_element_position_query("carrot")}')
carrots = agent.kb.query_quantity("carrot")
print(f'how many carrots? : {agent.kb.query_quantity("carrot")}')
agent.kb.update_quantity("carrot", 0)

agent.act(level)
# let him ACT !!!!!!!!!
while level.rewards[-1] != 100:
    level.render()
    agent.percept(level)
    agent.kb.update_quantity("carrot", agent.kb.query_quantity("carrot")-carrots)
    agent.act(level)