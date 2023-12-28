import time
import numpy as np

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

        self.state,reward,_,_ = self._env.step(self._get_action_id(action=actionName)) # action            
        if(what is not None): self.state,reward,_,_ = self._env.step(self._env.actions.index(ord(what)))# object
        if(where is not None): self.state,reward,_,_ = self._env.step(self._get_action_id(action=where)) # direction
        #TODO: if a KB is used it should be updated here since we have a new state

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
        #TODO: check if is stepping on before raising exception
        #self.print_every_position()
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
        return int(current_health/max_health*100)

    def get_pony_position(self) -> (int,int):
        return list(self.get_element_position('pony'))[0]
    
    def get_saddle_position(self) -> List[Tuple[int,int]]:
        return self.get_element_position('saddle')
    
    def get_carrot_position(self) -> List[Tuple[int,int]]:
        return self.get_element_position('carrot')
    
    def get_rewards(self) -> [int]:
        return self.rewards

    def get_map_as_nparray(self) -> np.ndarray:
        return self.state['chars']
    
    # just an utility to check position during test
    def print_every_position(self):
        for i in range(len(self.state['screen_descriptions'])):
            for j in range(len(self.state['screen_descriptions'][0])):
                description = decode(self.state['screen_descriptions'][i][j])
                if(description != '' and description != 'floor of a room'):
                    print(f'{description} in <{i},{j}>')
        
    # supposed that the distance between [pony] target and agent is <= 3
    #TODO: reimplement considering get_element_position() returns a list
    def align_with_target(self, target:str) -> str:
        target_pos = self.get_element_position(element=target)
        agent_pos = self.get_agent_position()
        agent_pos = (agent_pos[0] - target_pos[0], agent_pos[1] - target_pos[1])
        if agent_pos[0] == agent_pos[1] or -agent_pos[0] == agent_pos[1]:
            return
        if agent_pos[0] == 0 or agent_pos[1] == 0:
            return
        move = ''
        if agent_pos[0] == 1:
            move = 'N'
        elif agent_pos[0] == -1:
            move = 'S'
        elif agent_pos[1] == 1:
            move = 'W'
        elif agent_pos[1] == -1:
            move = 'E'
        if move != '':
            self.apply_action(move)

    def align_with_pony(self):
        return self.align_with_target(target='pony')
    
    def get_target_direction(self, target:str) -> str:
        entity_pos = self.get_element_position(target)
        agent_pos = self.get_element_position('Agent')
        agent_pos = (agent_pos[0] - entity_pos[0], agent_pos[1] - entity_pos[1])
        throw_direction = ''
        if agent_pos[0] < 0:
            throw_direction += 'S'
        elif agent_pos[0] > 0:
            throw_direction += 'N'
        if agent_pos[1] < 0:
            throw_direction += 'E'
        elif agent_pos[1] > 0:
            throw_direction += 'W'
        return throw_direction
    
    def get_pony_direction(self):
        return self.get_target_direction('pony')

    def print_inventory(self):
        for letter, stringa in \
            zip(decode(self.state["inv_letters"]), self.state["inv_strs"]):
            print(letter, " - ", decode(stringa))

    def get_message(self):
        return decode(self.state["message"])
    
    # It was used to throw away all the carrots. Now is useless
    def throw_all(self, item:str, direction:str, show_inventory:bool = False):
        gen = (decode(s) for s in self.state["inv_strs"])
        number = 0
        for stringa in gen:
            if item in stringa:
                number = int(stringa.split(" ")[0])
                break
        if(number == 0):
            raise Exception(f'Item {item} not in inventory')
        for _ in range(number):
            self.apply_action(actionName='THROW', what=item, where=direction)
            if show_inventory:
                self.render()
                self.print_inventory()
