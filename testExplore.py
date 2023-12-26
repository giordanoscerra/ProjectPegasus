from utils.map import Map
from utils.agent import Agent

lvl = Map(pony=False, level=1)
#this is a knight whose name is samurai
samurai = Agent()

for i in range(120):
    to_explore = samurai.explore(lvl)
    if to_explore == '':
        break
    lvl.apply_action(actionName=to_explore)
print("lvl explore 1: Done")

lvl = Map(pony=False, level=2)
#this is a knight whose name is samurai
samurai = Agent()

for i in range(120):
    to_explore = samurai.explore(lvl)
    if to_explore == '':
        break
    lvl.apply_action(actionName=to_explore)
print("lvl explore 2: Done")