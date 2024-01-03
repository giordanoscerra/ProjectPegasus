import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))
from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance
from utils.map import Map
from utils.agent import Agent
from utils import exceptions

# spawn level
level = Map(pony=True, level=-1)
agent = Agent()
# this is important af
agent.percept(level)
# let him ACT !!!!!!!!!
while(not level.is_episode_over()):
    agent.act(level, show_steps=False, graphic=False, delay=0.0)

#save stats on a file called stats.txt
stats = open("stats.txt", "a")
stats.write(f'rewards:<{str(level.rewards[-1])}> steps:<{str(len(level.rewards))}>\n')
stats.close()

