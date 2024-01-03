import time
import numpy as np
import math

from utils.customLevels.generator import createLevel

import matplotlib.pyplot as plt
import IPython.display as display

from typing import Optional, List, Tuple
from .general import decode
from . import exceptions 


DIRECTIONS = ['N','S','E','W','NE','NW','SE','SW']

# Most of the code is copied from Andrea's exercise
# if something does not work it's probably his fault
# if something does work it's probably thanks to him
class Map:
    def __init__(self, pony:bool = True, level:int = 0, **kwargs):
        env, (self.minXCG, self.maxXCG) = createLevel(level=level, pony=pony, **kwargs)
        self.rewards = []
        self.state = env.reset()
        #leftmost_wall = self.state['pixel']
        #env.render()
        self._env = env
        self.done = False

    #get the action number from high level string
    def _get_action_id(self, action: str) -> int:
        for az in self._env.actions:
            if action == az.name:
                action_index = self._env.actions.index(az)
                return action_index
        return -1
    
    #return the object letter from its name
    def _get_item_char(self,item:str) -> Optional[str]:
        for item_char, stringa in zip(decode(self.state["inv_letters"]), self.state["inv_strs"]):
            if item in decode(stringa):
                if 'uncursed carrot' not in decode(stringa):
                    return item_char
        return None

    def apply_action(self,actionName: str, what:str = None, where:str = None):   
        if(self._get_action_id(action=actionName) == -1):
            raise Exception(f'Not valid action <{actionName}>')
        if(where is not None and where not in DIRECTIONS):
            raise Exception(f'Valid directions are {DIRECTIONS}, you gave: {where}')
        if(what is not None and self._get_item_char(what) is None):
            raise Exception(f'Object <{what}> is not in inventory')
        elif(what is not None):
            #print(f'Object <{what}> is in inventory')
            #print inventory
            #self.print_inventory()
            what = self._get_item_char(what)
            #print(f'Object <{what}> is in inventory')
      
        self.state,reward,self.done,_ = self._env.step(self._get_action_id(action=actionName)) # action 
        if(what is not None): self.state,reward,self.done,_ = self._env.step(self._env.actions.index(ord(what)))# object
        if(where is not None): self.state,reward,self.done,_ = self._env.step(self._get_action_id(action=where)) # direction

        self.rewards.append(reward)

    def render(self, graphic:bool=False,delay:float = 0.5):
        time.sleep(delay)
        if(not graphic):
            self._env.render()
        else:
            image = plt.imshow(self.state['pixel'][15:, self.minXCG:self.maxXCG])
            #save image
            #plt.savefig(f'./images/img{self.imageID}.png')
            #self.imageID += 1
            display.display(plt.gcf())
            print(bytes(self.state['message']).decode('utf-8').rstrip('\x00'))
            display.clear_output(wait=True)
    
    # This function is used only by the testagent.py script
    def get_element_position(self, element:str) -> List[Tuple[int,int]]:
        positions = []
        for i in range(len(self.state['screen_descriptions'])):
            for j in range(len(self.state['screen_descriptions'][0])):
                description = decode(self.state['screen_descriptions'][i][j])
                if(element in description):
                    positions.append((i,j))
        if(not positions): raise exceptions.ElemNotFoundException(f'no {element} is found in this state') 
        return positions
        
    # Instances of get_element_position()    
    def get_agent_position(self) -> (int,int):
        return list(self.get_element_position('Agent'))[0]
    
    def get_agent_level(self) -> int:
        return self.state['blstats'][18] # https://arxiv.org/pdf/2006.13760.pdf lmao
    
    def get_agent_health(self) -> int:
        current_health = self.state['blstats'][10]
        max_health = self.state['blstats'][11]
        return math.floor((current_health/max_health)*100)
    
    def get_agent_strength(self) -> int:
        return self.state['blstats'][3] # https://arxiv.org/pdf/2006.13760.pdf
    
    def get_agent_dexterity(self) -> int:
        return self.state['blstats'][4]

    def get_agent_constitution(self) -> int:
        return self.state['blstats'][5]
    
    def get_agent_charisma(self) -> int:
        return self.state['blstats'][8]
    
    def get_agent_hunger(self) -> int:
        return self.state['blstats'][21]

    def get_pony_position(self) -> (int,int):
        try:
            return list(self.get_element_position('pony'))[0]
        except exceptions.ElemNotFoundException:
            return None
    
    def get_saddle_position(self) -> List[Tuple[int,int]]:
        return self.get_element_position('saddle')
    
    def get_carrot_position(self) -> List[Tuple[int,int]]:
        return self.get_element_position('carrot')
    
    def get_rewards(self) -> [int]:
        return self.rewards

    def get_map_as_nparray(self) -> np.ndarray:
        return self.state['chars']
    
    def is_episode_over(self) -> bool:
        return self.done
    
    # just an utility to check position during test
    def print_every_position(self):
        for i in range(len(self.state['screen_descriptions'])):
            for j in range(len(self.state['screen_descriptions'][0])):
                description = decode(self.state['screen_descriptions'][i][j])
                if(description != '' and description != 'floor of a room' and description != 'wall' and description != 'dark part of a room'):
                    print(f'{description} in <{i},{j}>')

    def print_inventory(self):
        for letter, stringa in \
            zip(decode(self.state["inv_letters"]), self.state["inv_strs"]):
            print(letter, " - ", decode(stringa))

    def get_message(self):
        return decode(self.state["message"])
