from utils.general import decode
from utils.KBwrapper import *
from utils.map import Map
from utils import exceptions 
import numpy as np

class Agent():
    def __init__(self):
        # I'd say that the initialization of the agent
        # also first initializes the (possibly, a) KB
        self.kb = KBwrapper()        # as of now, KBWrapper uses the kb from handson2!
        self.attributes = {}

    def look_for_element(self, game_map:Map, element:str='pony', return_coord:bool=False):
        '''Scans the whole map, via the get_element_position method of the
        Map class, looking for the position of a specific element.
        The kb is updated with this info, and the coordinates can be returned
        if one so chooses.        
        '''

        # look for specific element, then store position in the KB
        try:
            x,y = game_map.get_element_position(element)
            #self.kb.retract_element_position(element,x,y)
            self.kb.retract_element_position(element)
            self.kb.assert_element_position(element,x,y)
            if return_coord:
                return x,y
        except exceptions.ElemNotFoundException:
            # Q: if the element is not perceived, does it mean that isn't there?
            # (e.g. a local perception for an element that isn't in viewing range
            # because for example the room is dark, or is in another room)
            self.kb.retract_element_position(element)
        except Exception as e:
            print(f"An error occurred: {e}")


    def percept(self, game_map:Map, interesting_item_list:list = ['carrot', 'saddle', 'pony', 'Agent']):
        '''removes the position of all the items in interesting_item_list
        from the kb. Then scans the whole map, looking for such elements and
        inserting in the kbthe position of the interesting items that 
        have been found.      
        '''
        
        # IDEA: rimediare all'inefficienza della versione precedente,
        # (nel frattempo riadattata a uno scan per un elemento specifico nella mappa)
        # facendo un unico scan della mappa, alla ricerca di elementi interessanti.
        #
        # PROS: più efficiente, customizzabile. Dovrebbe essere semplice manipolare il 
        # "range" della percezione, per fare dei percept più "locali"
        #
        # CONS: (nella versione attuale) fa il retract di tutto, e questo potrebbe
        # non essere ciò che si vuole (ad esempio, si vuole non aggiornare la 
        # posizione di un qualche elemento specifico. Boh). 

        # escamotage per fare il retract della posizione di tutti gli elementi :D
        # self.kb.retract_element_position('_')   

        for item in interesting_item_list:
            # we retract the positions of the elements of interest from the KB,
            # in order to re-add them (update)
            #
            # TODO: remove specific items (is a problem also in the KBWrapper class)
            self.kb.retract_element_position(item)

        # Q: Consider an approach that uses np.where  
        # (cfr. get_location, in map.py). Maybe more efficient?         
        scr_desc = game_map.state['screen_descriptions']
        for i in range(len(scr_desc)):
            for j in range(len(scr_desc[0])):
                description = decode(scr_desc[i][j])
                if(description != '' and description != 'floor of a room'):
                    for interesting_item in interesting_item_list:
                        if interesting_item in description:
                            # Q: store the position of different items of the same
                            # "type" by keeping distinction (see comments in KBwrapper).
                            # Maybe is not a real issue, maybe it is...
                            self.kb.assert_element_position(interesting_item.lower(),i,j)
        
        # get the agent level
        self.attributes["level"] = game_map.get_agent_level()
        # get the agent's health (percentage). It is stored also in the
        # KB, since it might be useful for taking decisions
        self.attributes["health"] = game_map.get_agent_health()
        self.kb.update_health(self.attributes["health"])

    def chance_of_mount_succeeding(self, steed):
        if steed not in self.kb.get_rideable_steeds():
            return 0
        exp_lvl = self.attributes["level"]
        # Steed tameness isn't observable by the agent but can be inferred assuming it started as the lowest possible and
        # increased by a certain amount (in our case 1) everytime the agent feeds the steed. It starts as 1 and can go up to 20.
        # The tameness of new pets depends on their species, not on the method of taming. They usually start with 5. +1 everytime they eat
        steed_tameness = self._kb.get_steed_tameness(steed) # did not yet test this
        return 100/(5 * (exp_lvl + steed_tameness))

    def kbQuery(self, query:str):
        '''For rapid-test purposes only.
        Dummy function that queries the kb for the string in input. 
        For the sake of cleanness, this is done by calling an appropriate
        method of the KBwrapper class
        '''
        return self.kb.queryDirectly(query)