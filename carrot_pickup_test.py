from utils.map import Map
from utils.agent import Agent

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

while(knight.kb.get_element_position_query(element='carrot') != []):
    knight.percept(level)
    #go to carrot
    knight.go_to_element(level,element='carrot',show_steps=True, delay=0.2, maxDistance=0, minDistance=0)
    #pick up carrot
    level.apply_action('PICKUP')
    level.render()

level.apply_action('S')
level.render()
#print rewards
print(level.rewards)
#print inventory
level.print_inventory()