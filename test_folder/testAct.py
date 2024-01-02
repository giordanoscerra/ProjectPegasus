import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))
from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance
from utils.map import Map
from utils.agent import Agent
from utils import exceptions

# spawn level
level = Map(pony=True, level=3)
agent = Agent()
# this is important af
agent.percept(level)
# let him ACT !!!!!!!!!
while(level.get_agent_position() != level.get_pony_position()):
    agent.act(level)