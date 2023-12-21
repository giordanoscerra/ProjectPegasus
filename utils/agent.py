from utils.general import decode
from utils.KBwrapper import *
from utils.map import Map
from utils.exceptions import *
import numpy as np

class Agent():
    def __init__(self):
        # I'd say that the initialization of the agent
        # also first initializes the (possibly, a) KB
        self.kb = KBwrapper()        # as of now, KBWrapper uses the kb from handson2!
        attributes = {}

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
        # Ho dichiarato un'altra eccezione perché mi sta sulle balle il fatto 
        # che quando si fa il catch Exception as e qualsiasi eccezione viene
        # catturata. Ma ci sono due eccezioni: quando l'elemento non 
        # viene trovato (e quindi basta levare l'info dalla kb), e le altre
        # eccezioni a caso che boh potrebbero accadere perché il mondo fa schifo
        except ElemNotFoundException as e:
            self.kb.retract_element_position('pony')
            #print(e)
        except Exception as e:
            print(f"An error occurred: {e}")
        
        # get the agent level
            self.attributes["level"] = game_map.get_agent_level()

    def chance_of_mount_succeeding(self, steed):
        if steed not in self.kb.get_rideable_steeds():
            return 0
        exp_lvl = self.attributes["level"]
        # Steed tameness isn't observable by the agent but can be inferred assuming it started as the lowest possible and
        # increased by a certain amount (in our case 1) everytime the agent feeds the steed. It starts as 1 and can go up to 20.
        # The tameness of new pets depends on their species, not on the method of taming. They usually start with 5. +1 everytime they eat
        steed_tameness = self._kb.get_steed_tameness(steed) # did not yet test this
        return 100/(5 * (exp_lvl + steed_tameness))