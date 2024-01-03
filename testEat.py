from utils.map import Map
from utils.agent import Agent

# spawn level
level = Map(pony=False, level=-1)
agent = Agent()
# this is important af
agent.percept(level)
level.render()
# let him ACT !!!!!!!!!
while(not level.is_episode_over()):
    agent.act(level)

print(level.rewards)
exit(agent.actions_performed)