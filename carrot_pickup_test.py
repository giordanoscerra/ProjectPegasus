from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance
from utils.map import Map
from utils.agent import Agent
from utils import exceptions

level = Map(pony=False)
knight = Agent()

knight.percept(level)
level.render()
for i in range(12):
    #eat carrot
    #the number 12 is picked at random, so to test the reward correctly
    #this should be changed to the number of carrots in the inventory
    try:
        level.apply_action('EAT',what='carrot')
        level.render()
    except:
        print('No carrot')
        break

agent_start_pos = level.get_agent_position()
carrots_pos = knight.kb.get_element_position_query('carrot')

carrots_exist = True
while carrots_exist:
    try:
        #go to carrot
        knight.percept(level)
        #agent_start_pos = level.get_agent_position()
        #closer_carrot_pos = infinity_distance(knight.kb.get_element_position_query('carrot'),agent_start_pos)[0]
        knight.go_to_closer_element(level,element='carrot',show_steps=True, 
                                    delay=0.2,
                                    heuristic= lambda x,y: manhattan_distance([x],y)[1])
        #knight.go_to_element(level,element='carrot',show_steps=True, delay=0.2, maxDistance=0, minDistance=0)
        
        #print(f'Agent went to closer: {closer_carrot_pos == level.get_agent_position()}')

        #pick up carrot
        level.apply_action('PICKUP')
        level.render()
    except exceptions.ElemNotFoundException:
        carrots_exist = False


level.apply_action('S')
level.render()
#print rewards
print(level.rewards)
#print inventory
level.print_inventory()