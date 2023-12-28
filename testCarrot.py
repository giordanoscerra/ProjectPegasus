from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance
from utils.map import Map
from utils.agent import Agent
from utils import exceptions


def eat_all_carrots(knight:Agent,level:Map):
    '''Makes the agent eat all the carrots in its inventory
    '''
    knight.percept(level)
    for _ in range(knight.kbQuery('carrots(X)')[0]['X']):
        level.apply_action('EAT',what='carrot')
        knight.percept(level)
        level.render()

def testPickup(level:Map, knight:Agent):
    '''Test if the simple task of going arount picking up carrots
    goes according to plan
    '''
    knight.percept(level)
    level.render()

    eat_all_carrots(knight,level)

    agent_start_pos = level.get_agent_position()
    carrots_pos = knight.kb.get_element_position_query('carrot')

    carrots_exist = True
    while carrots_exist:
        try:
            #go to carrot
            knight.percept(level)
            #agent_start_pos = level.get_agent_position()
            closer_carrot_pos = infinity_distance(knight.kb.get_element_position_query('carrot'),agent_start_pos)[0]
            knight.go_to_closer_element(level,element='carrot',show_steps=True, 
                                        delay=0.2,
                                        heuristic= lambda x,y: manhattan_distance([x],y)[1])

            print(f'Agent went to closer: {closer_carrot_pos == level.get_agent_position()}')

            #pick up carrot
            level.apply_action('PICKUP')
            level.render()
        except exceptions.ElemNotFoundException:
            carrots_exist = False

def testSubtask(level:Map,knight:Agent):
    '''Test that the go_to_carrot subtask is chosen when appropriate,
    and is executed accordingly
    '''
    knight.percept(level)
    level.render()

    eat_all_carrots(knight,level)

# Actual program starts here:
test_choice = input('Which test do you want to execute? (P : testPickup, T: testSubtask) ')

if test_choice.upper() == 'P':
    level = Map(pony=False)
    knight = Agent()
    testPickup(level,knight)
elif test_choice.upper() == 'T':
    level = Map(level = 74, pony=True, peaceful=False, enemy=False)
    knight = Agent()
    testSubtask(level,knight)

    print('Next subtask is: ', knight.kb.query_for_action())
    knight.kb.query_for_action()    #will most likely return 'getCarrot'
    knight.get_carrot(level)
    level.print_inventory()
    print('Next subtask is: ', knight.kb.query_for_action())
    knight.kb.query_for_action()    #will most likely return 'pacifySteed'
    print('Tameness level of the pony is ',
          knight.kb.get_steed_tameness('pony'), 'out of 20')
    #knight.pacify_steed(level)
    #print('After throwing one carrot, tameness level of the pony is ',
    #      knight.kb.get_steed_tameness('pony'), 'out of 20')
    #print('Next subtask is: ', knight.kb.query_for_action())
else:
    print('Invalid choice. Please enter P for testPickup or T for testSubtask.')

level.apply_action('S')
level.render()
#print rewards
print(level.rewards)
#print inventory
level.print_inventory()