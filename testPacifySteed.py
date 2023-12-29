from utils.map import Map
from utils.agent import Agent
import math
from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance

def calculate_throw_range(strength):
    return 0 + math.floor(strength/2)

#for i in range(3, 26):
#    print(i, ' range ', calculate_throw_range(i))

for i in range (100):
    level = Map()
    knight = Agent()

    #agent_strenght = level.get_agent_strength()

    knight.interact_with_pony(level=level, action='THROW', what='carrot', maxOffset=calculate_throw_range(level.get_agent_strength()), show_steps=False)



#knight.percept(level)
#level.render()

#go_to_closer_element potrebbe usare il maxOffsets

#knight.get_carrot(level = level, heuristic= lambda x,y: manhattan_distance([x],y)[1])
#level.render()

"""
# https://nethackwiki.com/wiki/Throw#Food
agent_strenght = level.get_agent_strength() 
max_throw_range = 6

knight.go_to_closer_element(level,element='pony',show_steps=True, delay=0.2, heuristic= lambda x,y: manhattan_distance([x],y)[1], maxDistance=max_throw_range)
#level.render()

#level.align_with_pony()
#level.render()

#pony_direction = level.get_pony_direction()
#level.render()

level.apply_action(actionName='THROW', what='carrot', where='S')
level.render()
"""
