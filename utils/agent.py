import numpy as np
import time
import math
import re
from typing import List, Callable, Tuple
from utils.KBwrapper import *
from utils.map import Map, DIRECTIONS
from utils import exceptions
from utils.heuristics import *
from utils.map_graph import MapGraph
from .general import actions_from_path, are_aligned, are_close, decode
from .algorithms import a_star

class Agent():
    def __init__(self):
        # I'd say that the initialization of the agent
        # also first initializes the (possibly, a) KB
        self.kb = KBwrapper()        # as of now, KBWrapper uses the kb from handson2!
        self.attributes = {
            'encumbrance' : "unencumbered"
        } # easy to access attributes about the agent: see it as a sort of cache
        self.actions = {
            "getCarrot": self.get_carrot,
            "getSaddle": self.get_saddle,
            "feedSteed": self.feed_steed,
            "applySaddle": self.apply_saddle,
            "rideSteed": self.ride_steed,
            "explore": self.explore_subtask,
        }
        self.current_subtask = None
        self.actions_performed = 0

    def closest_element_position(self, element:str, distance:Callable=infinity_distance) -> Tuple[int,int]:
        '''Queries the kb for the position of all elements in the map, and
        returns the coordinates of the closer to the agent (according to a 
        given distance (default one is the infinity_distance)).
        If no elements are found, raises a ElemNotFoundException
        '''
        agent_pos = self.kb.get_element_position_query(element='agent')[0]
        elements_pos = self.kb.get_element_position_query(element)
        return distance(elements_pos,agent_pos)[0]


    # --------- Percept-related methods START ---------
    def percept(self, game_map:Map, interesting_item_list:list = ['carrot', 'saddle', 'pony', 'Agent', 'wall']) -> None:
        '''Removes the position of all the items in interesting_item_list
        from the kb. Then scans the whole map, looking for such elements and
        inserting in the kb the position of the interesting items that 
        have been found.      
        '''
        # When the episode ends all values in the blstats and other pointers are deleted.
        if game_map.is_episode_over(): return

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
                if(description not in ['','floor of a room','wall']):
                    for interesting_item in interesting_item_list:
                        if interesting_item in description:
                            if "pony" in description:
                                if any(property in description for property in ["tame", "peaceful"]): 
                                    self.kb.retract_hostile("pony") # it's that easy
                                else: 
                                    self.kb.assert_hostile("pony")
                                if "saddled" in description: 
                                  self.kb.assert_saddled_steed("pony")
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
        self.attributes["strength"] = game_map.get_agent_strength()
        self.attributes["charisma"] = game_map.get_agent_charisma()
        self.attributes["dexterity"] = game_map.get_agent_dexterity()
        self.attributes["constitution"] = game_map.get_agent_constitution()
        self.attributes["riding"] = self.kb.query_riding("steed")
        self.attributes["carrying_capacity"] = 1000 if self.attributes["riding"] else (25*(self.attributes["strength"]+self.attributes["constitution"])) + 50
        self.kb.update_health(self.attributes["health"])

    def process_message(self, message:str):
        '''Called by agent.percept(level). Reads the message and
        asserts in the agent.kb if the agent is stepping on an item.
        '''
        #TODO: process other important messages, if any
        #submex_list = message.split('. ')
        pattern = '|'.join(map(re.escape, ['.', '!']))
        submex_list = re.split(pattern, message)
        for msg in submex_list:
            msg = msg.lstrip(' ')
            if 'You see here' in msg:
                # Remove "You see here" and trailing dot
                portion = msg[msg.find('You see here ')+13:]
                portion = portion.strip('.')   
                # Remove article
                element = ' '.join(portion.split(' ')[1:])  
                #print(f'You see here a {element}')
                for x in ['saddle', 'carrot']:
                    if x in element:
                        element = x
                # assert position of element in the KB
                x, y = self.kb.get_element_position_query(element='agent')[0]
                self.kb.assert_element_position(element.replace(' ',''),x,y) 
                # Actually assert that the agent is stepping on the element
                # Q: hopefully the message is processed correctly!
                #   I mean, if the message is like 'You see here a blessed carrot.
                #   we're screwed...
                self.kb.assert_stepping_on(element)
            for x in ['saddle', 'carrot']:    #add other interesting stuff here
                if 'picks up a '+x in msg:
                    # 4: all those messages (hopefully!) start with 'The '
                    picker = msg[4:msg.find(' picks up a '+x)]
                    if('pony' in picker):
                        picker='pony'
                    self.kb.assert_has(owner=picker,item=x)
                if 'drops a '+x in msg:
                    dropper = msg[4:msg.find(' drops a '+x)]
                    if('pony' in dropper):
                        dropper = 'pony'
                    self.kb.retract_has(owner=dropper,item=x)
                for steed in self.kb._categories['steed']:
                    for synonimous in ['eats','devours']:
                        # we assume that 
                        if 'The '+steed+' '+synonimous in msg and x in msg:
                            # print(f'Increase tameness of {steed} due to {synonimous}')
                            self.kb.update_tameness(inc=1,steed=steed)

            for key, value in self.kb.encumbrance_messages.items():
                if msg in value: 
                    self.kb.update_encumbrance(key)
                    self.attributes["encumbrance"] = key

    def process_inventory(self, game_map:Map, interesting_items:list = ['saddle', 'carrot', 'apple']):
        '''called to save the intresting element of the inventory in the kb
        an element is to be considered interesting if it is useful for riding
        '''
        interesting_collection = {item.lower():0 for item in interesting_items}
        for string in game_map.state["inv_strs"]:
            for item in interesting_items:
                if item in decode(string).lower():
                    count = decode(string).split(' ')[0]
                    if 'uncursed carrot' not in decode(string).lower():
                        if count.isdigit():
                            interesting_collection[item] += int(count)
                        else:
                            # handle cases like 'a carrot' or 'an apple'
                            interesting_collection[item] += 1
        for item in interesting_collection:
            self.kb.update_quantity(item, interesting_collection[item])

    # --------- Percept-related methods END ---------

    def act(self, level:Map, show_steps:bool=True, graphic:bool = False, delay:float = 0.1):
        self.current_subtask = self.kb.query_for_action() # returns subtask to execute
        #print("\n\n UHM. the voices in my head are telling me to", self.current_subtask, "!!!!!!!!!!!!!!")
        subtask = self.actions.get(self.current_subtask, lambda: None) # calls the function that executes the subtask
        if subtask is None: 
            raise Exception(f'Action {self.current_subtask} is not defined')
        #yeah so most of the time we just need the map, other stuff is optional
        try:
            subtask(level, show_steps=show_steps, graphic=graphic, delay=delay)
        except exceptions.SubtaskInterruptedException as exc: pass
            # Oh nooo, someone passed the exception up to this level !!!! :O
            #print(f"SubtaskInterruptedExceptions caught with message: {exc}")
        except exceptions.TerminalStateReachedException as exc: pass

    def chance_of_mount_succeeding(self, steed):
        if steed not in self.kb.get_rideable_steeds() or self.kb.is_slippery():
            return 0
        exp_lvl = self.attributes["level"]
        # Steed tameness isn't observable by the agent but can be inferred assuming it started as the lowest possible and
        # increased by a certain amount (in our case 1) everytime the agent feeds the steed. It starts as 1 and can go up to 20.
        # The tameness of new pets depends on their species, not on the method of taming. They usually start with 5. +1 everytime they eat
        steed_tameness = self.kb.get_steed_tameness(steed) # did not yet test this
        return 100/(5 * (exp_lvl + steed_tameness))
    
    # returns an approximate of the "chance" variable calculated in steed.c of the nethack code https://github.com/NetHack/NetHack/blob/NetHack-3.6.0_Release/src/steed.c
    # if a random number picked between 0 and 100 is lower than the chance variable, the agent will mount the steed.
    def chance_of_saddle_apply_succeeding(self, steed):
        if steed not in self.kb.get_rideable_steeds() or self.kb.is_slippery():
            return 0
        chance = self.attributes["dexterity"] + self.attributes["charisma"] / 2 + 2 * self.kb.get_steed_tameness(steed)
        chance += self.attributes["level"] * 20 if self.kb.get_steed_tameness(steed) > 0 else (5 - 10) # it should be 5 - 10*monster_level but how the hell do we infer that.
        # if (self.attributes["role"] == "knight"): 
        chance += 20
        # chance += self.kb.riding_skill.get(self.attributes["riding_skill"])
        chance += 30 # the knight is expert in riding.
        # if self.kb.is_saddle_cursed(): -= 50
        if self.kb.is_agent_confused() or self.kb.is_agent_fumbling(): chance -= 50

    def check_interrupt(self):
        return self.kb.query_for_interrupt(self.current_subtask) if self.current_subtask else False

    def kbQuery(self, query:str):
        '''For rapid-test purposes only.
        Dummy function that queries the kb for the string in input. 
        For the sake of cleanness, this is done by calling an appropriate
        method of the KBwrapper class
        '''
        return self.kb.queryDirectly(query)
    
    def _perform_action(self, level: Map, actionName: str, what:str = None, where:str = None, show_steps:bool=True, graphic:bool = False, delay:float = 0.1):
        level.apply_action(actionName, what, where)
        self.actions_performed += 1
        if (show_steps):
            level.render(delay=delay, graphic=graphic)
        if (level.is_episode_over()):
            raise exceptions.TerminalStateReachedException("Terminal state reached after performing an action.")
        self.percept(level)
        interrupt = self.check_interrupt()
        if interrupt:
            # Situation changed, the plan is no good
            #if (actionName in DIRECTIONS and self.current_subtask != 'explore'):
                #print(f"According to KB, the {self.current_subtask} has to be "f"interrupted after the action {actionName} that has just ""been applied")
            raise exceptions.SubtaskInterruptedException("Exception raised after performing an action.")



    # --------- Carrot-related subtasks (Andrea) START ---------
    
    def get_carrot(self, level: Map, heuristic: callable = lambda t,s: manhattan_distance([t],s)[1], show_steps:bool=True, graphic:bool = False, delay:float = 0.1):
        while self.interact_with_element(level=level, element='carrot', action="PICKUP", maxOffset=0, show_steps=show_steps, graphic=graphic, delay=delay): pass


    # --------- Saddle and ride subtask (Giordano) START ---------
    def get_saddle(self, level:Map, heuristic:callable = lambda t,s: manhattan_distance([t],s)[1], show_steps:bool=True, graphic:bool = False, delay:float = 0.1):
        self.interact_with_element(level=level, element='saddle', action="PICKUP", maxOffset=0, show_steps=show_steps, graphic=graphic, delay=delay)
    
    # Calculated from the table here: https://nethackwiki.com/wiki/Throw#Food for objects weighting less than 40
    def _get_throw_range(self, level:Map):
        return math.floor(level.get_agent_strength()/2)
    
    def feed_steed(self, level, show_steps:bool=True, graphic:bool = False, delay:float = 0.1):
        while self.interact_with_element(level=level, element='pony', action="THROW",what="carrot", maxOffset=self._get_throw_range(level), show_steps=show_steps, graphic=graphic, delay=delay): pass
    
    def apply_saddle(self, level, show_steps:bool=True, graphic:bool = False, delay:float = 0.1):
        self.interact_with_element(level=level, element='pony', action="APPLY",what="saddle", maxOffset=1, show_steps=show_steps, graphic=graphic, delay=delay)

    def ride_steed(self, level, show_steps:bool=True, graphic:bool = False, delay:float = 0.1):
        self.interact_with_element(level=level, element='pony', action="RIDE", maxOffset=1, show_steps=show_steps, graphic=graphic, delay=delay)

    # To interact with the pony walking step by step, and each time recalculating the best step from zero
    def interact_with_element(self, level: Map, element: str=None, action: str=None, what: str=None, maxOffset: int=1, show_steps:bool=True, delay:float=0.1,heuristic: callable = lambda t,s: manhattan_distance([t],s)[1], graphic:bool = False) -> bool:

        try:
            # this baddie here could raise interestings exceptions if it's interrupted. be ready to catch 'em all !
            stop = False
            while not stop:
                try:
                    self.go_to_closer_element(level, element=element, 
                                            heuristic=heuristic, 
                                            show_steps=show_steps, 
                                            delay=delay, maxDistance=maxOffset, 
                                            dynamic=(element == 'pony'), graphic=graphic)
                    stop = True
                except exceptions.ElemNotInDestinationException as exc1: pass
                    # You sure about that? Catching this exception means the target moved. 
                    # We just need to call again the go_to_closer_element and try harder
                    #print(f"Caught ElemNotInDestinationException with message: {exc1}")

            direction = None
            if (maxOffset > 0):
                agent_pos = self.kb.get_element_position_query('agent')[0]
                elem_pos = self.kb.get_element_position_query(element)[0]

                delta = (agent_pos[0] - elem_pos[0], agent_pos[1] - elem_pos[1])
                direction = ''
                if delta[0] > 0:
                    direction += 'N'
                elif delta[0] < 0:
                    direction += 'S'
                if delta[1] > 0:
                    direction += 'W'
                elif delta[1] < 0:
                    direction += 'E'

            self._perform_action(level=level,actionName=action,what=what,where=direction,show_steps=show_steps,delay=delay,graphic=graphic)
            #print("is the steed hostile? " + str(bool(self.kbQuery('hostile(steed)'))))
        except exceptions.SubtaskInterruptedException as exc2:
            #print(f"SubtaskInterruptedExceptions caught with message: {exc2}")
            return False    
        except Exception as exc3:
            #Here control returns to agent main action loop, we need another agent.act !
            #print(f"Caught Exception with message: {exc3}")
            return False   
        return True 
        



    # --------- Explore subtask (DavideB) START ---------
    def explore_subtask(self, level:Map, heuristic:callable = lambda t,s: manhattan_distance(t,s), show_steps:bool = False, graphic:bool = False, delay:float = 0.1):
        if not self.explore_step(level=level, heuristic=heuristic, show_steps=show_steps, graphic=graphic, delay=delay): # if there is nothing to explore
            searchGraph = MapGraph(level)
            if searchGraph.fullVisited(): # handle rectangular room case
                self.kb.assert_full_visited()
                self._perform_action(level=level,actionName='WAIT',show_steps=show_steps, graphic=graphic, delay=delay)
            while not searchGraph.fullVisited(): # while there are places to search
                self.search_step(searchGraph=searchGraph, level=level, heuristic=heuristic, show_steps=show_steps, graphic=graphic, delay=delay)
        else: # if there is something to explore
            while self.explore_step(level=level, heuristic=heuristic, show_steps=show_steps, graphic=graphic, delay=delay): pass
        self.kb.assert_full_visited()
    
    def search_step(self, searchGraph:MapGraph, level:Map, heuristic:callable = lambda t,s: manhattan_distance(t,s), show_steps:bool = False, graphic:bool = False, delay:float = 0.1):
        agent_pos = self.kb.get_element_position_query('agent')[0]
        closestUnsearched = heuristic(searchGraph.lastVisit, agent_pos)[0]
        next_cells = a_star(level.get_map_as_nparray(),start=agent_pos, target=closestUnsearched, maxDistance=1, minDistance=1)[1:]
        path = actions_from_path(agent_pos, next_cells)
        for move in path:
            new_agent_pos = agent_pos
            while new_agent_pos == agent_pos: # wait until the agent moves
                self._perform_action(level=level, actionName=move, show_steps=show_steps, graphic=graphic, delay=delay)
                new_agent_pos = self.kb.get_element_position_query('agent')[0]
            agent_pos = new_agent_pos
            if searchGraph.update(): # if something has been visited
                break

            
    def explore_step(self, level: Map, heuristic: callable = lambda t,s: manhattan_distance(t,s), show_steps:bool = False, graphic:bool = False, delay:float = 0.1) -> bool:
        toExplore = self.get_unexplored_cells(level)
        if len(toExplore) == 0:
            return False
        try:
            agent_pos = self.kb.get_element_position_query('agent')[0]
        except exceptions.ElemNotFoundException:
            agent_pos = level.get_agent_position()
        place = heuristic(list(toExplore), agent_pos)[0]
        next_cells = a_star(level.get_map_as_nparray(),start=agent_pos, target=place, maxDistance=1, minDistance=1)[1:]
        #now we get the direction to go to reach the cell
        path = actions_from_path(agent_pos, next_cells)
        for move in path:
            new_agent_pos = agent_pos
            while new_agent_pos == agent_pos:
                self._perform_action(level=level,actionName=move, show_steps=show_steps, graphic=graphic, delay=delay)
                new_agent_pos = self.kb.get_element_position_query('agent')[0]
            agent_pos = new_agent_pos
            if self.check_something_explored(level, toExplore):
                return True

    
    def get_unexplored_cells(self, level: Map) -> set:
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
        return toExplore
    
    def check_something_explored(self, level: Map, ex_unexplored:set) -> bool:
        for element in ex_unexplored:
            if decode(level.state['screen_descriptions'][element[0]][element[1]]) != '':
                return True

    # --------- Explore subtask END ---------


    # --------- General stuff for pathfinding ---------
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
        pony_hostile = self.kb.query_hostile(creature='pony')
        return a_star(game_map_array, start=agent_pos,
                        target=closest_element_pos, heuristic=heuristic,
                        maxDistance=maxDistance, minDistance=minDistance,
                        pony_hostile=pony_hostile)

    def go_to_closer_element(self,level:Map,element:str='carrot', show_steps=False,
                             heuristic:callable = lambda t,s: manhattan_distance([t],s)[1],
                              delay=0.5, maxDistance:int=0, minDistance:int=0, dynamic:bool=False, graphic:bool = False):   
        ###self.percept(level)
        agent_pos = self.kb.get_element_position_query('agent')[0]
        path = self._get_best_path_to_target(level, target = element,
                                             heuristic=heuristic,
                                             maxDistance=maxDistance, minDistance=minDistance)

        # translate the path into a sequence of actions to perform
        # If the target is dynamic i can only keep the first step
        actions = actions_from_path(agent_pos, path[1:] if not dynamic else path[1:2])

        # follow the path (i.e. actually move) as long as the 
        # kb gives green light.
        while actions:            
            destination = path[-1]
            try:
                if not dynamic and destination not in self.kb.get_element_position_query(element):
                    raise exceptions.ElemNotInDestinationException\
                            (f'Somebody got to {destination} before the agent'
                                f' and took the {element}.')
            except exceptions.ElemNotFoundException as exc:
                #print(f"go_to_closer_element caught a ElemNotFoundException with message: {exc}")
                #print("This means that the element that was trying to be reached is not in sight anymore. ")
                raise Exception("The best thing to do is to raise another exception that "
                                "gets caught by interact_with_element, which in turn will "
                                "give back control to agent.act")
            


            self._perform_action(level=level,actionName = actions.pop(0), delay=delay, show_steps=show_steps, graphic=graphic)

            if dynamic:
                ###self.percept(level)
                agent_pos = self.kb.get_element_position_query('agent')[0]
                path = self._get_best_path_to_target(level, target = element,
                                        heuristic=heuristic,
                                        maxDistance=maxDistance, minDistance=minDistance)

                # translate the path into a sequence of actions to perform
                actions = actions_from_path(agent_pos, path[1:2])
            
