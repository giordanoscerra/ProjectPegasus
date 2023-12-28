from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance
from utils.map import Map
from utils.agent import Agent
from utils import exceptions


level = Map(pony=True, level=3)
#sam is a classical knight name
agent = Agent()
agent.percept(level)
level.apply_action('PICKUP')
level.render()
agent.interact_with_pony(level=level, action="APPLY",what="saddle", maxOffset=1)
level.print_inventory()
