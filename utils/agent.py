from pyswip import Prolog
from utils.map import Map

class Agent:
    def __init__(self, kbPath:str = None, map:Map = None):
        self.kb = Prolog()
        if kbPath is None: raise Exception("No kbPath provided")
        else: self.kb.consult(kbPath)
        if map is None: raise Exception("No map provided")
        else: self.map = map

    def chance_of_mount_succeeding(self, steed):
        if steed not in self.kb.query("rideable(X)"):
            return 0
        exp_lvl = self.map.get_agent_level()
        # Steed tameness isn't observable by the agent but can be inferred assuming it started as the lowest possible and
        # increased by a certain amount (got to find it) everytime the agent feeds the steed. It starts as 1 and can go up to 20.
        # The tameness of new pets depends on their species, not on the method of taming. They usually start with 5. +1 everytime they eat
        steed_tameness = self.kb.query(f"steed_tameness({steed}, X)")[0]['X'] # did not yet test this
        return 100/(5 * (exp_lvl + steed_tameness))
        