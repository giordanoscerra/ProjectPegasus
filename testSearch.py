from utils.map import Map
from utils.agent import Agent


lvl = Map(pony=False, level=3)
lvl.render()
#the name of the knight is ninja
ninja = Agent()

ninja.percept(lvl)
ninja.explore_subtask(lvl, render=True, delay=0.0)
ninja.explore_subtask(lvl, render=True, delay=0.0)