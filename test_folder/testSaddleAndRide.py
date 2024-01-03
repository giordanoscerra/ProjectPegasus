from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance
from utils.map import Map
from utils.agent import Agent
from utils import exceptions

# spawn simple square level with our best pal the PACIFIC PONY 
level = Map(pony=True, level=4)
agent = Agent()
# this percept could be useless
agent.percept(level)
level.apply_action('PICKUP')
level.render()
# this could be better with condition of tameness probability
for _ in range(10):
    agent.interact_with_element(level=level, element='pony', action="THROW",what="carrot", maxOffset=7, delay=0)
agent.ride_steed(level)


