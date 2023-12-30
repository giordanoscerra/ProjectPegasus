from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance
from utils.map import Map
from utils.agent import Agent
from utils import exceptions

# spawn level
level = Map(pony=True, level=0)
agent = Agent()
# this percept could be useless
agent.percept(level)
# let him ACT !!!!!!!!!
while level.rewards[-1] != 100:
    agent.act(level)
    level.render()