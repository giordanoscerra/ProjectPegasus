import numpy as np
import time
from typing import Callable
from utils.KBwrapper import *
from utils.map import Map
from utils.exceptions import *
from .general import are_aligned, are_close



class Agent():
    def __init__(self):
        # I'd say that the initialization of the agent
        # also first initializes the (possibly, a) KB
        self.kb = KBwrapper()        # as of now, KBWrapper uses the kb from handson2!
        self.attributes = {}
        self.actions = {
            "getCarrot": self.get_carrot,
            "pacifySteed": self.pacify_steed,
            "feedSteed": self.feedSteed,
            "rideSteed": self.rideSteed
        }

    def percept(self, game_map:Map):
        # IDEA: game_map.get_element_position for all things of 
        # interest.
        # PROS: The semantic is clear & clean, based on the context 
        # (e.g. the agent performing subtasks) the "interesting things"
        # to perceive may be different (i.e. the things to assert in the kb)
        #
        # CONS: it is very inefficient, as the whole map is scanned multiple
        # times!

        # look for pony
        try:
            x,y = game_map.get_pony_position()
            print(f'pony is in position ({x},{y})')
            self.kb.retract_element_position('pony')
            self.kb.assert_element_position('pony',x,y)
        # Ci sono due eccezioni: quando l'elemento non 
        # viene trovato (e quindi basta levare l'info dalla kb), e le altre
        # eccezioni a caso che boh potrebbero accadere perché il mondo fa schifo
        # please leave your comments in english :) - Yuri
        except Exception as e:
            if e is ElemNotFoundException: self.kb.retract_element_position('pony')
            else: print(f"An error occurred: {e}")
        
        # get the agent level
            self.attributes["level"] = game_map.get_agent_level()

    def act(self):
        action = self.kb.query_for_action() # returns subtask to execute
        args = self.getArgs(action) # returns arguments for the subtask
        subtask = self.actions.get(action, lambda: None) # calls the function executing the subtask
        if subtask is None: raise Exception(f'Action {action} is not defined')
        subtask(*args) # execute the subtask


    def chance_of_mount_succeeding(self, steed):
        if steed not in self.kb.get_rideable_steeds():
            return 0
        exp_lvl = self.attributes["level"]
        # Steed tameness isn't observable by the agent but can be inferred assuming it started as the lowest possible and
        # increased by a certain amount (in our case 1) everytime the agent feeds the steed. It starts as 1 and can go up to 20.
        # The tameness of new pets depends on their species, not on the method of taming. They usually start with 5. +1 everytime they eat
        steed_tameness = self._kb.get_steed_tameness(steed) # did not yet test this
        return 100/(5 * (exp_lvl + steed_tameness))
    
    def getCarrot(self, carrotPos):
        return "TO BE CONTINUED"
    def getSaddle(self, saddlePos):
        return "TO BE CONTINUED"
    def pacifySteed(self, steedPos):
        return "TO BE CONTINUED"
    def feedSteed(self, steedPos):
        return "TO BE CONTINUED"
    def rideSteed(self, steedPos):
        return "TO BE CONTINUED"
        

    #TODO: discuss with the team on which algorithm to use
    #   things to consider:
    #       A* may be too much
    #       it is easy now but may be harder with monster and secondary task
    #       the environment will not always be a rectangle
    # this will take agent in distance that is <= maxDistance and >= minDistance from the object
    # The heuristic should take in the list of positions of an element, the tuple indicating 
    # the position of the agent and return a tuple indicating the position of the element to go to
    def go_to_element(self, game_map:Map, element:str, heuristic: Callable[[list(tuple),tuple],tuple], show_steps:bool=False, delay:float = 0.5, maxDistance:int = 3, minDistance:int = 1) -> None:
        if(positions := game_map.get_element_position(element) > 1): element_pos = heuristic(positions)
        else: element_pos = positions[0]
        agent_pos = game_map.get_agent_position()
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
                element_pos = game_map.get_element_position(element=element)
            except:
                if(minDistance != 0):
                    raise Exception(f'No {element} is found in this state')
            agent_pos = game_map.get_agent_position()
            if(show_steps):
                time.sleep(delay)
                self.render()