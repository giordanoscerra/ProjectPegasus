import numpy as np
import time
from typing import List, Callable, Tuple
from utils.KBwrapper import *
from utils.map import Map
from utils import exceptions
# from utils.exceptions import *
from utils.heuristics import *
from .general import actions_from_path, are_aligned, are_close, decode
from .algorithms import a_star

class Agent():
    def __init__(self):
        # I'd say that the initialization of the agent
        # also first initializes the (possibly, a) KB
        self.kb = KBwrapper()        # as of now, KBWrapper uses the kb from handson2!
        self.attributes = {}
        self.actions = {
            "getCarrot": self.get_carrot,
            "getSaddle": self.get_saddle,
            "pacifySteed": self.pacify_steed,
            "hoardCarrots": self.hoard_carrots,
            "feedSteed": self.feed_steed,
            "rideSteed": self.ride_steed
        }
        self.current_subtask = None

    def closest_element_position(self, element:str, distance:Callable=infinity_distance) -> Tuple[int,int]:
        '''Queries the kb for the position of all elements in the map, and
        returns the coordinates of the closer to the agent (according to a 
        given distance (default one is the infinity_distance)).
        If no elements are found, raises a ElemNotFoundException
        '''
        agent_pos = self.kb.get_element_position_query(element='agent')[0]
        elements_pos = self.kb.get_element_position_query(element)
        return distance(elements_pos,agent_pos)[0]


    def percept(self, game_map:Map, interesting_item_list:list = ['carrot', 'saddle', 'pony', 'Agent']) -> None:
        '''Removes the position of all the items in interesting_item_list
        from the kb. Then scans the whole map, looking for such elements and
        inserting in the kbthe position of the interesting items that 
        have been found.      
        '''

        # escamotage per fare il retract della posizione di tutti gli elementi :D
        # self.kb.retract_element_position('_')   
        
        self.kb.retractall_stepping_on()
        for item in interesting_item_list:
            # we retract the positions of the elements of interest from the KB,
            # in order to re-add them (update)
            #
            # TODO: remove specific items (is a problem also in the KBWrapper class)
            self.kb.retract_element_position(item)
      
        scr_desc = game_map.state['screen_descriptions']
        for i in range(len(scr_desc)):
            for j in range(len(scr_desc[0])):
                description = decode(scr_desc[i][j])
                if(description != '' and description != 'floor of a room'):
                    for interesting_item in interesting_item_list:
                        if interesting_item in description:
                            self.kb.assert_element_position(interesting_item.lower().replace(' ',''),i,j)
        
        self.process_attributes(game_map=game_map)
        self.process_message(message=decode(game_map.state['message']))
        self.process_inventory(game_map=game_map)

    def process_attributes(self, game_map:Map):
        # get the agent level
        self.attributes["level"] = game_map.get_agent_level()
        # get the agent's health (percentage). It is stored also in the
        # KB, since it might be useful for taking decisions
        self.attributes["health"] = game_map.get_agent_health()
        self.kb.update_health(self.attributes["health"])

    def process_message(self, message:str):
        '''Called by agent.percept(level). Reads the message and
        asserts in the agent.kb if the agent is stepping on an item.
        '''
        #TODO: process other important messages, if any

        if 'You see here' in message:
            # Remove "You see here" and trailing dot
            portion = message[message.find('You see here ')+13:message.find('.')]   
            # Remove article
            element = ' '.join(portion.split(' ')[1:])  
            # Maybe it doesn't make much sense to tell the kb that the agent
            # and an item that will (most probably) immediately be picked up
            # are in the same position
            x, y = self.kb.get_element_position_query(element='agent')[0]
            self.kb.assert_element_position(element.replace(' ',''),x,y) 
            # Actually assert that the agent is stepping on the element
            # Q: hopefully the message is processed correctly!
            #   I mean, if the message is like 'You see here a blessed carrot.
            #   we're screwed...
            self.kb.assert_stepping_on(element)             

    def process_inventory(self, game_map:Map, interesting_items:list = ['saddle', 'carrot', 'apple']):
        '''called to save the intresting element of the inventory in the kb
        an element is to be considered interesting if it is useful for riding
        '''
        interesting_collection = {item.lower():0 for item in interesting_items}
        for string in game_map.state["inv_strs"]:
            for item in interesting_items:
                if item in decode(string):
                    count = decode(string).split(' ')[0]
                    if count.isdigit():
                        interesting_collection[item] += int(count)
                    else:
                        # handle cases like 'a carrot' or 'an apple'
                        interesting_collection[item] += 1
        for item in interesting_collection:
            self.kb.update_quantity(item, interesting_collection[item])

    def act(self, level:Map):
        self.current_subtask = self.kb.query_for_action() # returns subtask to execute
        args = self.getArgs(self.current_subtask) # returns arguments for the subtask
        subtask = self.actions.get(self.current_subtask, lambda: None) # calls the function that executes the subtask
        if subtask is None: raise Exception(f'Action {self.current_subtask} is not defined')
        subtask(*args) # execute the subtask

    def chance_of_mount_succeeding(self, steed):
        if steed not in self.kb.get_rideable_steeds() or self.kb.is_slippery():
            return 0
        exp_lvl = self.attributes["level"]
        # Steed tameness isn't observable by the agent but can be inferred assuming it started as the lowest possible and
        # increased by a certain amount (in our case 1) everytime the agent feeds the steed. It starts as 1 and can go up to 20.
        # The tameness of new pets depends on their species, not on the method of taming. They usually start with 5. +1 everytime they eat
        steed_tameness = self.kb.get_steed_tameness(steed) # did not yet test this
        return 100/(5 * (exp_lvl + steed_tameness))
    
    def check_interrupt(self):
        return self.kb.query_for_interrupt(self.current_subtask) if self.current_subtask else False

    def kbQuery(self, query:str):
        '''For rapid-test purposes only.
        Dummy function that queries the kb for the string in input. 
        For the sake of cleanness, this is done by calling an appropriate
        method of the KBwrapper class
        '''
        return self.kb.queryDirectly(query)
    
    def get_carrot(self, level: Map, heuristic: callable = lambda t,s: manhattan_distance([t],s)[1]):
        # carrot_position = heuristic(self.kb.get_element_position_query("carrot"), self.kb.get_element_position_query("agent"))
        self.go_to_closer_element(level, element='carrot', heuristic=heuristic, show_steps=True, delay=0.5)
        self.percept(level)
        # Maybe a method for picking up, to do things in a fancy/flashy way?
        # check if the object is still there? (of course it will)
        if self.kb.query_stepping_on(spaced_elem='carrot'):
            level.apply_action(actionName='PICKUP')
            # percept here just for safety: mainly to update inventory
            self.percept(level)
            print('get_carrot task successful!')
        else:
            return 'There is no carrot here! (according to KB)'

    
    def get_saddle(self, level:Map, heuristic:callable = lambda t,s: manhattan_distance([t],s)[1]):
        self.go_to_closer_element(level, element='saddle', heuristic=heuristic, show_steps = True, delay=0.2)
        self.percept(level)
        if self.kb.query_stepping_on(spaced_elem='saddle'):
            level.apply_action(actionName='PICKUP')
            self.percept(level)
            print('get_saddle successful!')
        else:
            return 'There is no saddle here! (according to KB)'
    
    def pacify_steed(self, steedPos):
        return "TO BE CONTINUED"
    
    def hoard_carrots(self):
        return "TO BE CONTINUED"
    
    def feed_steed(self, steedPos):
        return "TO BE CONTINUED"
    
    def ride_steed(self, steedPos):
        return "TO BE CONTINUED"
    
    def explore(self, level: Map, heuristic: callable = lambda t,s: manhattan_distance(t,s)):
        toExplore = set()
        for i in range(len(level.state['screen_descriptions'])):
            for j in range(len(level.state['screen_descriptions'][0])):
                description = decode(level.state['screen_descriptions'][i][j])
                if(description != '' and description != 'wall'):
                    # check each surrounding cell,
                    # if it is empty, add it to the list of cells to explore
                    # '' means that the cell is not explored yet
                    if decode(level.state['screen_descriptions'][i][j-1]) == '':
                        toExplore.add((i,j-1))
                    if decode(level.state['screen_descriptions'][i][j+1]) == '':
                        toExplore.add((i,j+1))
                    if decode(level.state['screen_descriptions'][i-1][j]) == '':
                        toExplore.add((i-1,j))
                    if decode(level.state['screen_descriptions'][i+1][j]) == '':
                        toExplore.add((i+1,j))
        # now we have a set of cells to explore
        # we need to find the closest one
        if len(toExplore) == 0:
            return ''
        try:
            agent_pos = self.kb.get_element_position_query('agent')[0]
        except exceptions.ElemNotFoundException:
            agent_pos = level.get_agent_position()
        place = heuristic(list(toExplore), agent_pos)[0]
        next_cell = a_star(level.get_map_as_nparray(),start=agent_pos, target=place, maxDistance=1, minDistance=1)[1]
        #now we get the direction to go to reach the cell
        return actions_from_path(agent_pos, [next_cell])[0]

    # TODO: deal with maxDistance and minDistance
    def _get_best_path_to_target(self, game_map: Map, target,
                                heuristic:callable = lambda t,s: manhattan_distance([t],s)[1],
                                maxDistance:int=0,minDistance:int=0) -> List[Tuple[int, int]]:
        '''Returns the best path (as a list of tuples (i.e. coordinates)) from
        the agent's position to the closer element given as argument.
        Best path is computed using a* (with a given heuristic)
        '''
        agent_pos = self.kb.get_element_position_query('agent')[0]
        closest_element_pos = self.closest_element_position(element=target)
        game_map_array = game_map.get_map_as_nparray()
        return a_star(game_map_array, start=agent_pos,
                        target=closest_element_pos, heuristic=heuristic,
                        maxDistance=maxDistance, minDistance=minDistance)

    def go_to_closer_element(self,level:Map,element:str='carrot', show_steps=False,
                             heuristic:callable = lambda t,s: manhattan_distance([t],s)[1],
                              delay=0.5, maxDistance:int=0, minDistance:int=0):   
        self.percept(level)
        agent_pos = self.kb.get_element_position_query('agent')[0]
        path = self._get_best_path_to_target(level, target = element,
                                             heuristic=heuristic,
                                             maxDistance=maxDistance, minDistance=minDistance)
        # translate the path into a sequence of actions to perform
        actions = actions_from_path(agent_pos, path[1:])

        # follow the path (i.e. actually move) as long as the 
        # kb gives green light.
        for move_dir in actions:
            # TODO: a true query for greenlight
            try:
                # Hopefully this is the way to go: at each step the agent
                # senses the environment, checks if it can proceed by 
                # querying the kb for a greenlight (otherwise control 
                # is returned to the action picker I guess (agent.act maybe))
                # and moves
                self.percept(level)
                #greenlight_status = self.kb.query_for_greenlight()
                interrupt = self.check_interrupt()
                if not interrupt:
                    level.apply_action(actionName = move_dir)
                    if(show_steps):
                        time.sleep(delay)
                        level.render()
                else:
                    break
            # Who knows, maybe the query_for_greenlight raises an exception...
            except:
                break

