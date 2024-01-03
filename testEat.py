from utils.map import Map
from utils.agent import Agent
from utils.heuristics import *

'''
FOR BETTER VISIBILITY DECOMMENT ROW 177 AND 178 IN AGENT.PY
or copy these lines in act after deciding the better action
print("\n\n UHM. the voices in my head are telling me to", self.current_subtask, "!!!!!!!!!!!!!!")
time.sleep(0.5)
'''

# spawn level WITHOUT PONY.
# our poor agent won't survive, unfortunately. 
# but he will try to eat his apples !!! 
# WARNING: may turn blind and never move again. idk why.
level = Map(pony=False, level=-1)
agent = Agent()
# this is important af
agent.percept(level)
level.render()
# let him ACT !!!!!!!!!
while(not level.is_episode_over()):
    agent.act(level=level, delay=0.01, heuristic=manhattan_distance)

print(level.rewards)
exit(agent.actions_performed)