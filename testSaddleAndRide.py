from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance
from utils.map import Map
from utils.agent import Agent
from utils import exceptions


level = Map(pony=True, level=3)
#sam is a classical knight name
sam = Agent()
sam.percept(level)
level.render()
level.apply_action('PICKUP')
level.render()
print("is the steed hostile? " + str(bool(sam.kbQuery('hostile(steed)'))))
