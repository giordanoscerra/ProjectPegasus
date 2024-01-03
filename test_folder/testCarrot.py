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
    bool_closer_list = []

    carrots_exist = True
    while carrots_exist:
        try:
            #go to carrot
            knight.percept(level)
            #agent_start_pos = level.get_agent_position()
            closer_carrot_pos = infinity_distance(
                knight.kb.get_element_position_query('carrot'),
                agent_start_pos)[0]
            knight.go_to_closer_element(level,element='carrot',show_steps=False, 
                                        delay=0.2,
                                        heuristic= lambda x,y: manhattan_distance([x],y)[1])

            agent_start_pos = level.get_agent_position()
            bool_closer = closer_carrot_pos == agent_start_pos
            #print(f'Agent went to closer: {bool_closer}')
            bool_closer_list.append(bool_closer)

            #pick up carrot
            level.apply_action('PICKUP')
            level.render()
        except exceptions.ElemNotFoundException:
            carrots_exist = False

    return bool_closer_list

def testSubtask(level:Map,knight:Agent):
    '''Test that the go_to_carrot subtask is chosen when appropriate,
    and is executed accordingly
    '''
    knight.percept(level)
    level.render()

    next_subtask = knight.kb.query_for_action()
    print('Next subtask is: ', next_subtask)
    if(next_subtask == 'getCarrot'):
        knight.get_carrot(level)
        knight.percept(level)
        level.print_inventory()
        print('get_carrot task completed')
    elif(next_subtask == 'pacifySteed'):
        print('Tameness level of the pony is ',
            knight.kb.get_steed_tameness('pony'), 'out of 20')
        print('Direct query for hostility yields: ',knight.kbQuery('hostile(X)'))
        knight.pacify_steed(level)
        print('After throwing one carrot, tameness level of the pony is ',
            knight.kb.get_steed_tameness('pony'), 'out of 20')
        print('And direct query for hostility now yields: ',knight.kbQuery('hostile(X)'))
    elif(next_subtask=='hoardCarrots'):
        try:
            pony_present = knight.kb.get_element_position_query('steed')
        except exceptions.ElemNotFoundException:
            pony_present = False
        print('The pony is present: ', bool(pony_present))
        knight.hoard_carrots(level)

def testHoard(level:Map,knight:Agent):
    knight.percept(level)
    knight.pacify_steed(level)

    knight.kb.query_for_action()    #will most likely return 'hoardCarrots'
    knight.hoard_carrots(level)


# Actual program starts here:
test_choice = input('Which test do you want to execute? (P : testPickup, T: testSubtask, H: hoardTest) ')

if test_choice.upper() == 'P':
    level = Map(pony=False)
    knight = Agent()
    lista = testPickup(level,knight)

    assert all(lista)
    print('testCarrot with pickup_carrot successfully completed')
elif test_choice.upper() == 'T':
    level = Map(level = 74, pony=True, peaceful=False, enemy=False)
    knight = Agent() 

    eat_all_carrots(knight,level)

    testSubtask(level,knight)

  
elif test_choice.upper() == 'H':
    level = Map(pony=True)
    knight = Agent()

    testHoard(level,knight)    
else:
    print('Invalid choice. Please enter P for testPickup or T for testSubtask.')

#level.apply_action('S')
#level.render()
##print rewards
#print(level.rewards)
##print inventory
#level.print_inventory()