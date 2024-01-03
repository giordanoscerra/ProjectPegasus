from utils.map import Map
from utils.agent import Agent

# spawn labirinth level
level = Map(pony=True, level=1)
agent = Agent()
# this percept could be useless
agent.percept(level)
while(True):
    agent.explore_subtask(level)