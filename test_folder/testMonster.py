import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))
from utils.map import Map
from utils.agent import Agent

level = Map(pony=True, level=1, enemies=True)
agent = Agent()
agent.percept(game_map=level)
level.render()

print('KB tells the agent to: ', agent.kb.query_for_action())
#agent.attack_enemy(level)

while(not level.is_episode_over()):
    agent.act(level)