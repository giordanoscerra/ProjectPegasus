import numpy as np
import time
import math
from typing import List, Callable, Tuple
from utils.KBwrapper import *
from utils.map import Map
from utils import exceptions
# from utils.exceptions import *
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


    # --------- Percept-related methods START ---------
    def percept(self, game_map:Map, interesting_item_list:list = ['carrot', 'saddle', 'pony', 'Agent', 'wall']) -> None:
        '''Removes the position of all the items in interesting_item_list
        from the kb. Then scans the whole map, looking for such elements and
        inserting in the kb the position of the interesting items that 
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
        submex_list = message.split('. ')
        for msg in submex_list:
            if 'You see here' in msg:
                # Remove "You see here" and trailing dot
                portion = msg[msg.find('You see here ')+13:]
                portion = portion.strip('.')   
                # Remove article
                element = ' '.join(portion.split(' ')[1:])  
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
                    self.kb.assert_has(owner=picker,item=x)
                if 'drops a '+x in msg:
                    dropper = msg[4:msg.find(' drops a '+x)]
                    self.kb.retract_has(owner=dropper,item=x)
                for steed in self.kb._categories['steed']:
                    for synonimous in ['eats','devours','catches']:
                        # we assume that 
                        if 'The '+steed+' '+synonimous in msg and x in msg:
                            print(f'Increase tameness of {steed} due to {synonimous}')
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
                    if count.isdigit():
                        interesting_collection[item] += int(count)
                    else:
                        # handle cases like 'a carrot' or 'an apple'
                        interesting_collection[item] += 1
        for item in interesting_collection:
            self.kb.update_quantity(item, interesting_collection[item])

    # --------- Percept-related methods END ---------
    # this function is for testing purposes. don't ask. used only in "act", hopefully not for long.
    def randomSubtask(self):
        #actions = ["getCarrot", "getSaddle", "pacifySteed", "hoardCarrots", "feedSteed", "rideSteed"]
        # without feedSteed because davidem is slow af
        actions = ["getCarrot", "getSaddle", "pacifySteed", "hoardCarrots", "rideSteed"]
        return np.random.choice(actions)

    def act(self, level:Map):
        self.current_subtask = self.kb.query_for_action() # returns subtask to execute
        # yeah for now we have it like this because yeah query be like difficult
        # self.current_subtask = self.randomSubtask()
        print("\n\n UHM. the voices in my head are telling me to", self.current_subtask)
        time.sleep(0.5)
        #args = self.getArgs(self.current_subtask) # returns arguments for the subtask
        subtask = self.actions.get(self.current_subtask, lambda: None) # calls the function that executes the subtask
        if subtask is None: 
            raise Exception(f'Action {self.current_subtask} is not defined')
        #subtask(*args) # execute the subtask
        #yeah so most of the time we just need the map, other stuff is optional
        subtask(level)

    # is this useless ?
    def getArgs(subtask:str):
        args = []

        return args

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
    



    # --------- Carrot-related subtasks (Andrea) START ---------
    #def throw_element(self, level, throwDir:str, element:str='carrot'):
    #    '''Calls the apply_action() method from the Map class to 
    #    throw an element (given as input) in a direction given as input.
    #    If the thrown element is a carrot and it is eaten by the steed,
    #    the tameness of the pony is increased by 1'''
    #    try:
    #        level.apply_action(actionName='THROW',what=element,where=throwDir)
    #        # TODO: update tameness only if the pony catches the carrot
    #        self.percept(level)
    #        #if 'carrot' in element:
    #        #    for steed in ['pony','horse','warhorse']:
    #        #        for synonimous in ['eats', 'devours', 'cathces']:
    #        #            if 'The '+steed+' '+synonimous in decode(level.state['message']):
    #        #                self.kb.update_tameness(inc = 1,steed=steed)
    #    except Exception as exc:
    #        print(f'throw_element catched Exception with message: {exc}')
    
    def get_carrot(self, level: Map, show_steps:bool=True, delay=0.5,
                   heuristic: callable = lambda t,s: manhattan_distance([t],s)[1]):
        '''Performs the getCarrot task: the agent goes towards the closer carrots,
        picks it up and then goes towards the pony to throw the first carrot at it
        to make it not aggressive.
        '''
        # carrot_position = heuristic(self.kb.get_element_position_query("carrot"), self.kb.get_element_position_query("agent"))
        # Experiment!
        arrived = False
        while not arrived:
            try:
                self.go_to_closer_element(level, element='carrot', heuristic=heuristic, show_steps=show_steps, delay=delay)
            except exceptions.ElemNotInDestinationException as exc:
                #TODO: for some reason, this doesn't get printed even though
                #       the program gets to this point: it seems to be behaving
                #       as expected for what concerns the pathfinding
                print(f'go_to_carrot raised a ElemNotInDestinationException'
                    f' with the following message: {exc}.\n'
                    f'Recomputing best path to closer carrot.')
                continue
            arrived = True

        ###self.percept(level)

        if self.kb.query_stepping_on(spaced_elem='carrot'):
            level.apply_action(actionName='PICKUP')
            # percept here just for safety: mainly to update inventory
            self.percept(level)
                   
        else:
            # return exception? Nothing?
            return 'There is no carrot here! (according to KB)'
        
    def hoard_carrots(self, level:Map, show_steps:bool=True, delay=0.5,heuristic: callable = lambda t,s: manhattan_distance([t],s)[1]):
        carrots_exist = True
        while carrots_exist:
            try:
                carrots_exist = bool(self.kb.get_element_position_query('carrot'))
                self.percept(level)
                # Q: rn the agent is blindly going towards the element.
                #   I think that for this task it is important that
                #   the interrupts are seriously implemented
                # Q2: this is basically get_carrots multiple times!
                # Q3: remember that an ElemNotFoundException can still
                #   be risen by closest_element_position. The question of
                #   who catches this and to do what remains open...
                ###self.go_to_closer_element(level,element='carrot',show_steps=show_steps,
                ###                          delay=delay, heuristic=heuristic)
                
                # Experiment!
                arrived = False
                while not arrived:
                    try:
                        self.go_to_closer_element(level, element='carrot', heuristic=heuristic, show_steps=show_steps, delay=delay)
                    except exceptions.ElemNotInDestinationException as exc:
                        print('Eccezzzionale!')
                        print(f'go_to_closer_element raised a ElemNotInDestinationException'
                            f' with the following message: {exc}.\n'
                            f'Recomputing best path to closer carrot.')
                        continue
                    arrived = True
                    print('arrivato')
                
                ###self.percept(level)

                if self.kb.query_stepping_on(spaced_elem='carrot'):
                    level.apply_action(actionName='PICKUP')
                    # percept here just for safety: mainly to update inventory
                    self.percept(level)  
                else:
                    # return exception? Nothing?
                    # this could happen if another entity (e.g. pony)
                    # gets to the carrot before the agent. It's unlikely
                    return 'There is no carrot here! (according to KB)'
            except exceptions.ElemNotFoundException as exc:
                print('Apparently, the pony snagged away the last carrot, '
                      'and there aren\'t any more in sight.')
                print(f'hoard_carrots catched and exception with message: {exc}')
                break

    # --------- Saddle and ride subtask (Giordano) START ---------
    def get_saddle(self, level:Map, heuristic:callable = lambda t,s: manhattan_distance([t],s)[1]):
        self.go_to_closer_element(level, element='saddle', heuristic=heuristic, show_steps = True, delay=0.2)
        ###self.percept(level)
        if self.kb.query_stepping_on(spaced_elem='saddle'):
            level.apply_action(actionName='PICKUP')
            self.percept(level)
            print('get_saddle successful!')
        else:
            return 'There is no saddle here! (according to KB)'
    
    def _calculate_throw_range(self, strength):
        return math.floor(strength/2)

    def pacify_steed(self, level):
        # Calculated from the table here: https://nethackwiki.com/wiki/Throw#Food
        self.interact_with_element(level=level, element='pony', action="THROW",what="carrot", maxOffset=self._calculate_throw_range(level.get_agent_strength()))
    
    def feed_steed(self, level):
        carrots_to_feed = self.kb.queryDirectly('carrots(X)')[0]['X']
        while not self.check_interrupt() and carrots_to_feed > 0:
            self.interact_with_element(level=level, element='pony', action="THROW",what="carrot", maxOffset=self._calculate_throw_range(level.get_agent_strength()))
            carrots_to_feed -= 1
    
    def ride_steed(self, level):
        self.interact_with_element(level=level, element='pony', action="APPLY",what="saddle", maxOffset=1)
        self.interact_with_element(level=level, element='pony', action="RIDE", maxOffset=1)

    # To interact with the pony walking step by step, and each time recalculating the best step from zero
    def interact_with_element(self, level: Map, element: str=None, action: str=None, what: str=None, maxOffset: int=1, show_steps:bool=True, delay=0.5,heuristic: callable = lambda t,s: manhattan_distance([t],s)[1]):

        # TODO: May throw exceptions that have to be handled
        self.go_to_closer_element(level, element=element, 
                                  heuristic=heuristic, 
                                  show_steps=show_steps, 
                                  delay=delay, maxDistance=maxOffset, 
                                  dynamic=(element == 'pony'))
        ###self.percept(level)
        #agent_pos, pony_pos, closeness_condition = self._check_if_near_pony(maxOffset)
        agent_pos = self.kb.get_element_position_query('agent')[0]
        elem_pos = self.kb.get_element_position_query(element)[0]
        #perform the action!
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

        # TODO: Now if go_to_closer_element fails it still perform the action
        # TODO: May throw exceptions that have to be handled
        level.apply_action(actionName=action,what=what,where=direction)
        self.percept(level)
        level.render()
        #print("is the steed hostile? " + str(bool(self.kbQuery('hostile(steed)'))))


    # --------- Explore subtask (DavideB) START ---------
    def explore_subtask(self, level:Map, heuristic:callable = lambda t,s: manhattan_distance(t,s), render:bool = False, graphic:bool = False, delay:float = 0.5):
        next_action = self.explore_step(level, heuristic)
        if next_action == '': # if there is nothing to explore
            searchGraph = MapGraph(level)
            while not searchGraph.fullVisited() and not self.kb.query_for_interrupt('explore'):
                next_action = self.search_step(searchGraph, level, heuristic)
                level.apply_action(actionName=next_action)
                if render: level.render(delay=delay, graphic=graphic)
                self.percept(level)
                searchGraph.update()
        else: # if there is something to explore
            while next_action != '' and not self.kb.query_for_interrupt('explore'):
                level.apply_action(actionName=next_action)
                if render: level.render(delay=delay, graphic=graphic)
                self.percept(level)
                next_action = self.explore_step(level, heuristic)
    
    def search_step(self, searchGraph:MapGraph, level:Map, heuristic:callable = lambda t,s: manhattan_distance(t,s)):
        try:
            agent_pos = self.kb.get_element_position_query('agent')[0]
        except:
            agent_pos = level.get_agent_position()
        closestUnsearched = heuristic(searchGraph.lastVisit, agent_pos)[0]
        next_cell = a_star(level.get_map_as_nparray(),start=agent_pos, target=closestUnsearched, maxDistance=1, minDistance=1)[1]
        #now we get the direction to go to reach the cell
        return actions_from_path(agent_pos, [next_cell])[0]
            
        

    def explore_step(self, level: Map, heuristic: callable = lambda t,s: manhattan_distance(t,s)):
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
                              delay=0.5, maxDistance:int=0, minDistance:int=0, dynamic:bool=False):   
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

            # TODO: a true query for greenlight
            try:
                # Hopefully this is the way to go: at each step the agent
                # senses the environment, checks if it can proceed by 
                # querying the kb for a greenlight (otherwise control 
                # is returned to the action picker I guess (agent.act maybe))
                # and moves
                self.percept(level)

                # sort of a homemade interrupt: if someone else 
                # (e.g. the pony) gets to the element (e.g.) carrot 
                # earlier and steals it, 
                
                destination = path[-1]
                if not dynamic and destination not in self.kb.get_element_position_query(element):
                    raise exceptions.ElemNotInDestinationException\
                            (f'Somebody got to {destination} before the agent'
                             f' and took the {element}.')
                

                interrupt = self.check_interrupt()
                if not interrupt:
                    level.apply_action(actionName = actions.pop(0))
                    if(show_steps):
                        time.sleep(delay)
                        level.render()

                    if dynamic:
                        ###self.percept(level)
                        agent_pos = self.kb.get_element_position_query('agent')[0]
                        path = self._get_best_path_to_target(level, target = element,
                                             heuristic=heuristic,
                                             maxDistance=maxDistance, minDistance=minDistance)

                        # translate the path into a sequence of actions to perform
                        actions = actions_from_path(agent_pos, path[1:2])
                    
                else:
                    break
            # Who knows, maybe the query_for_greenlight raises an exception...
            except:
                break

