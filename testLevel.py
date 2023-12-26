from utils.map import Map
from utils.agent import Agent

level = Map(pony=False)
agent = Agent()

level.render()

print(level.get_agent_level())