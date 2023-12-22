from utils.map import Map
from utils.agent import Agent

level = Map(pony=False)
agent = Agent('KBS/kb.pl', level)

level.render()

print(level.get_agent_level())