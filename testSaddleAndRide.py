from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance
from utils.map import Map
from utils.agent import Agent
from utils import exceptions


level = Map(pony=True, level=3)
#sam is a classical knight name
agent = Agent()
agent.percept(level)
level.render()

level.apply_action('PICKUP')
level.render()
print("is the steed hostile? " + str(bool(agent.kbQuery('hostile(steed)'))))
agent.percept(level)
agent.go_to_closer_element(level,element="pony",show_steps=False,delay=0.2,heuristic=lambda x,y: manhattan_distance([x],y)[1])
level.render()
