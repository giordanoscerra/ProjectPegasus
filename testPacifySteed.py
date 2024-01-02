from utils.map import Map
from utils.agent import Agent
import math
from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance

def calculate_throw_range(strength):
    return 0 + math.floor(strength/2)

#for i in range(3, 26):
#    print(i, ' range ', calculate_throw_range(i))

level = Map()
knight = Agent()
#knight.interact_with_element(level=level, element='pony', action='THROW', what='carrot', maxOffset=calculate_throw_range(level.get_agent_strength()), show_steps=True)

knight.percept(level)
knight.get_carrot(level, graphic=False)
print('########################### get_carrot COMPLETED ###########################')
for i in range (12):
    knight.feed_steed(level)
print('########################### feed_steed COMPLETED ###########################')
knight.get_saddle(level)
print('########################### get_saddle COMPLETED ###########################')
knight.apply_saddle(level)
print('########################### apply_saddle COMPLETED ###########################')
knight.ride_steed(level)
print('########################### ride_steed COMPLETED ###########################')