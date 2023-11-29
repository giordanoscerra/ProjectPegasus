import gym
import numpy as np
from minihack import LevelGenerator
from nle import nethack

from typing import Optional
from utils.general import decode


DIRECTIONS = ['N','S','E','W','EN','NW','SE','SW']

# Most of the code is copied from Andrea's exercise
# if something does not works it is probably its fault
# if something does work it is probably thanks to him
class Map:
    def __init__(self):
        lvl = LevelGenerator(w=10,h=10)
        lvl.add_monster(name='pony', symbol="u", place=None)
        env = gym.make(
            'MiniHack-Skill-Custom-v0',
            actions = tuple(nethack.CompassDirection) + (
                nethack.Command.THROW,
                nethack.Command.RIDE,
                nethack.Command.EAT,
                nethack.Command.DROP,
                nethack.Command.APPLY
            ),
            character = "kn-hum-neu-mal",
            observation_keys = (
                'glyphs',
                'chars',
                'colors', # Some characters have special colors that represent different things.
                'screen_descriptions',  # descrizioni testuali di ogni cella della mappa 
                'message',
                'inv_strs',
                'inv_letters',
                'pixel'),
            des_file = lvl.get_des(),
        )
        self.state = env.reset()
        env.render()
        self._env = env

    #get the action number from high level string
    def _get_action_id(self, action: str) -> int:
        for az in self._env.actions:
            if action == az.name:
                action_index = self._env.actions.index(az)
                return action_index
        return -1
    
    #return the object letter from it's name
    def _get_item_char(self,item:str) -> Optional[str]:
        for item_char, stringa in zip(decode(self.state["inv_letters"]), self.state["inv_strs"]):
            if item in decode(stringa):
                return item_char
        return None
    
    def apply_action(self,actionName: str, what:str = None, where:str = None):
        
        if(self._get_action_id(action=actionName) == -1):
            raise Exception(f'Not valid action')
        if(where is not None and where not in DIRECTIONS):
            raise Exception(f'Valid directions are {DIRECTIONS}')
        if(what is not None and self._get_item_char(what) is None):
            raise Exception(f'Object <{what}> is not in inventory')
        elif(what is not None):
            what = self._get_item_char(what)

        if(what is None and where is None):
            #action that require no further info, probably move
            self.state,_,_,_ = self._env.step(self._get_action_id(action=actionName))# action
        elif(what is None and where is not None):
            #action that require a direction e.g. ride or throw
            self.state,_,_,_ = self._env.step(self._get_action_id(action=actionName))# action
            self.state,_,_,_ = self._env.step(self._get_action_id(action=where)) # direction
        elif(what is not None and where is None):
            #action that require a object e.g. wear or read
            self.state,_,_,_ = self._env.step(self._get_action_id(action=actionName))# action
            self.state,_,_,_ = self._env.step(self._env.actions.index(ord(what)))# object
        elif(what is not None and where is not None):
            #action that require a direction and object e.g. throw
            self.state,_,_,_ = self._env.step(self._get_action_id(action=actionName))
            self.state,_,_,_ = self._env.step(self._env.actions.index(ord(what)))# object
            self.state,_,_,_ = self._env.step(self._get_action_id(action=where))# direction
    
    def render(self):
        self._env.render()

    def printInventory(self):
        for letter, stringa in \
            zip(decode(self.state["inv_letters"]), self.state["inv_strs"]):
            print(letter, " - ", decode(stringa))

# ottiene la posizione dell'entità che nella mappa appare con symbol
# Ovviamente, se ce n'è più di una vanno cambiate delle cose...
def get_location(game_map: np.ndarray, symbol: str):
    x, y = np.where(game_map == ord(symbol))
    return x[0], y[0]