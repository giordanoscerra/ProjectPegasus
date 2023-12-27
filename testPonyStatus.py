from utils.map import Map
from utils.agent import Agent

def test_pony_hostility():
    level = Map()
    agent = Agent()
    agent.percept(level)
    level.render()
    print("is the steed hostile? " + str(bool(agent.kbQuery('hostile(steed)'))))

test_pony_hostility()