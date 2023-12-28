from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance
from utils.map import Map
from utils.agent import Agent
from utils import exceptions


level = Map(pony=True, level=3)
agent = Agent()
agent.percept(level)
level.apply_action('PICKUP')
level.render()
for _ in range(10):
    agent.interact_with_pony(level=level, action="THROW",what="carrot", maxOffset=7, delay=0)
agent.ride_steed(level)

