import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))
from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance
from utils.map import Map
from utils.agent import Agent
from utils import exceptions
import signal

def handler(signum, frame):
    stats = open("stats.txt", "a")
    stats.write(f'rewards:<{str(-1)}> steps:<{str(-1)}>\n')
    stats.close()
    sys.exit(0)

signal.signal(signal.SIGTERM, handler)

# spawn level
level = Map(pony=True, level=2, enemies=True)
agent = Agent()
# this is important af
agent.percept(level)
# let him ACT !!!!!!!!!
while(not level.is_episode_over()):
    agent.act(level, show_steps=True, graphic=False, delay=0.0)

print(level.rewards)
#save stats on a file called stats.txt
stats = open("stats.txt", "a")
stats.write(f'rewards:<{str(level.rewards[-1])}> steps:<{str(len(level.rewards))}>\n')
stats.close()

