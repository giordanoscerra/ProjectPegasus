import numpy as np
import time
from typing import Callable, Tuple
from utils.KBwrapper import *
from utils.map import Map
from utils import exceptions
from utils.heuristics import *
from .general import decode, are_aligned, are_close
from .algorithms import a_star

class Agent():
    def __init__(self):
        # I'd say that the initialization of the agent
        # also first initializes the (possibly, a) KB
        self.kb = KBwrapper()        # as of now, KBWrapper uses the kb from handson2!
        self.attributes = {}
        self.actions = {
            "getCarrot": self.get_carrot,
            "pacifySteed": self.pacify_steed,
            "feedSteed": self.feed_steed,
            "rideSteed": self.ride_steed
        }
        self.current_subtask = None

    def closest_element_position(self, element:str, heuristic:Callable=euclidean_distance):
        try:
            agent_pos = self.kb.get_element_position_query(element='agent')
            elements_pos = self.kb.get_element_position_query(element)
            return heuristic(elements_pos,agent_pos)
        except exceptions.ElemNotFoundException as exc:
            print(f'ElemNotFoundException: {exc}')
        except Exception as e:
            print(f'An error occurred: {e}')

    def percept(self, game_map:Map, interesting_item_list:list = ['carrot', 'saddle', 'pony', 'Agent']):
        '''removes the position of all the items in interesting_item_list
        from the kb. Then scans the whole map, looking for such elements and
        inserting in the kbthe position of the interesting items that 
        have been found.      
        '''

        # escamotage per fare il retract della posizione di tutti gli elementi :D
        # self.kb.retract_element_position('_')   

        for item in interesting_item_list:
            # we retract the positions of the elements of interest from the KB,
            # in order to re-add them (update)
            #
            # TODO: remove specific items? (is a problem also in the KBWrapper class)
            self.kb.retract_element_position(item)
            self.kb.retract_stepping_on(item)

        # Q: Consider an approach that uses np.where  
        # (cfr. get_location, in map.py). Maybe more efficient?    
        scr_desc = game_map.state['screen_descriptions']
        for i in range(len(scr_desc)):
            for j in range(len(scr_desc[0])):
                description = decode(scr_desc[i][j])
                if(description != '' and description != 'floor of a room'):
                    for interesting_item in interesting_item_list:
                        if interesting_item in description:
                            self.kb.assert_element_position(interesting_item.lower(),i,j)
        
        # get the agent level
        self.attributes["level"] = game_map.get_agent_level()
        # get the agent's health (percentage). It is stored also in the
        # KB, since it might be useful for taking decisions
        self.attributes["health"] = game_map.get_agent_health()
        self.kb.update_health(self.attributes["health"])

        self.process_message(message=decode(game_map.state['message']))

    def process_message(self, message:str):
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
            self.kb.assert_stepping_on(element)             

    def act(self):
        self.current_subtask = self.kb.query_for_action() # returns subtask to execute
        args = self.getArgs(self.current_subtask) # returns arguments for the subtask
        subtask = self.actions.get(self.current_subtask, lambda: None) # calls the function executing the subtask
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
    
    def get_carrot(self, carrotPos):
        return "TO BE CONTINUED"
    def get_saddle(self, saddlePos):
        return "TO BE CONTINUED"
    def pacify_steed(self, steedPos):
        return "TO BE CONTINUED"
    def feed_steed(self, steedPos):
        return "TO BE CONTINUED"
    def ride_steed(self, steedPos):
        return "TO BE CONTINUED"
    
    def get_best_path_to_element(self, game_map: Map, element, heuristic: callable) -> List[Tuple[int, int]]:
        agent_position = self.kb.get_element_position('agent')
        element_position = self.kb.get_element_position(element)
        game_map_array = game_map.get_map_as_nparray()
        return a_star(game_map_array, agent_position, element_position, heuristic)

    #TODO: discuss with the team on which algorithm to use
    #   things to consider:
    #       A* may be too much
    #       it is easy now but may be harder with monster and secondary task
    #       the environment will not always be a rectangle
    # this will take agent in distance that is <= maxDistance and >= minDistance from the object
    # The heuristic should take in the list of positions of an element, the tuple indicating 
    # the position of the agent and return a tuple indicating the position of the element to go to
    def go_to_element(self, game_map: Map, element, heuristic:Callable=euclidean_distance,\
                       show_steps=False, delay = 0.5, maxDistance = 3, minDistance = 1):
        #if(len(positions := game_map.get_element_position(element)) > 1): element_pos = heuristic(positions,game_map.get_agent_position())
        #else: element_pos = positions[0]
        agent_pos = self.closest_element_position(element='agent',heuristic=heuristic)
        element_pos = self.closest_element_position(element=element,heuristic=heuristic)
        #until we are not close to the pony
        while(not are_aligned(element_pos, agent_pos) or not are_close(element_pos, agent_pos, maxOffset=maxDistance)):
            if(not are_close(element_pos, agent_pos, maxOffset=maxDistance)):
                move = ''
                if(element_pos[0] < agent_pos[0] - minDistance):
                    move += 'N'
                elif(element_pos[0] > agent_pos[0] + minDistance):
                    move += 'S'
                if(element_pos[1] < agent_pos[1] - minDistance):
                    move += 'W'
                elif(element_pos[1] > agent_pos[1] + minDistance):
                    move += 'E'
                game_map.apply_action(move)
            else:
                game_map.align_with_pony()
            try:
                element_pos = self.closest_element_position(element=element,heuristic=heuristic)
            except:
                if(minDistance != 0):
                    raise Exception(f'No {element} is found in this state')
            agent_pos = game_map.get_agent_position()
            if(show_steps):
                time.sleep(delay)
                game_map.render()
