import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))
from utils.map import Map
from utils.agent import Agent

level = Map(pony=False, level=74, enemy=True)
agent = Agent()
agent.percept(game_map=level)
level.render()

agent.attack_enemy(level)