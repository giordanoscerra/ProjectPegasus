from utils.map import Map
from utils.agent import Agent


lvl = Map(pony=False, level=3)
lvl.render()
agent = Agent()

agent.percept(lvl)
agent.explore_subtask(lvl, render=True, delay=0.0)
agent.explore_subtask(lvl, render=True, delay=0.0)