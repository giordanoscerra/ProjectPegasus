import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))
from utils.map import Map
from utils.agent import Agent

lvl = Map(pony=False, level=1)
#this is a knight whose name is samurai
samurai = Agent()

for i in range(120):
    to_explore = samurai.explore_step(lvl)
    if to_explore == '':
        print("lvl explore 1: Done in", i, "steps")
        break
    if i == 119:
        print("lvl explore 1: NOT Done in", i, "steps")
    lvl.apply_action(actionName=to_explore)

lvl = Map(pony=False, level=2)
samurai = Agent()
for i in range(120):
    to_explore = samurai.explore_step(lvl)
    if to_explore == '':
        print("lvl explore 2: Done in", i, "steps")
        break
    if i == 119:
        print("lvl explore 2: NOT Done in", i, "steps")
    lvl.apply_action(actionName=to_explore)

lvl = Map(pony=False, level=3)
samurai = Agent()
for i in range(1200):
    to_explore = samurai.explore_step(lvl)
    if to_explore == '':
        print("lvl explore 3: Done in", i, "steps")
        break
    if i == 1190:
        print("lvl explore 3: NOT Done in", i, "steps")
    lvl.apply_action(actionName=to_explore)