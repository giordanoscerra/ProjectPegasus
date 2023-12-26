from utils.map import Map
from utils.agent import Agent
from utils.heuristics import euclidean_distance

level = Map()
agent = Agent()

#print pony direction
print(level.get_pony_direction())
#print carrots direction
print(level.get_target_direction('carrot'))
#print saddle direction
print(level.get_target_direction('saddle'))
import time
level.render()
time.sleep(100)

#go to saddle
agent.go_to_element(game_map=level,element='saddle',heuristic=euclidean_distance,show_steps=True, maxDistance=0, minDistance=0)
level.render()

#pick up saddle
level.apply_action('PICKUP')
level.render()

#go to pony and throw carrots
for i in range(3):
    agent.go_to_element(game_map=level,element='pony',heuristic=euclidean_distance,show_steps=True)
    throw_direction = level.get_pony_direction()
    level.apply_action('THROW', what='carrot', where=throw_direction)
    level.render(delay=1)

#saddle pony
agent.go_to_element(game_map=level,element='pony',heuristic=euclidean_distance, show_steps=True, maxDistance=1)
saddle_direction = level.get_pony_direction()
level.apply_action('APPLY', what='saddle', where=saddle_direction)
level.render()

#ride pony
agent.go_to_element(game_map=level, element='pony',heuristic=euclidean_distance, show_steps=True, maxDistance=1)
ride_direction = level.get_pony_direction()
level.apply_action('RIDE', where=ride_direction)
level.render()
print(level.rewards)
#print(level.get_agent_position())
#print(level.get_pony_position())
#level.print_every_position()