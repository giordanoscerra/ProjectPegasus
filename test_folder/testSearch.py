import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))
from utils.map import Map
from utils.agent import Agent

#this test can't work if you don't change the explore_subtask method in agent.py
#please don't

lvl = Map(pony=False, level=3)
lvl.render()
#the name of the knight is ninja
ninja = Agent()

ninja.percept(lvl)
ninja.explore_subtask(lvl, render=True, delay=0.0)
ninja.explore_subtask(lvl, render=True, delay=0.0)