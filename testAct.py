from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance
from utils.map import Map
from utils.agent import Agent
from utils import exceptions

# spawn level
level = Map(pony=False, level=0)
agent = Agent()
# this is important af
agent.percept(level)
# let him ACT !!!!!!!!!
while(True):
    agent.act(level)
