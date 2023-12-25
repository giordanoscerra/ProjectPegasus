import time
import numpy as np

from utils.customLevels.generator import createLevel

import matplotlib.pyplot as plt
import IPython.display as display

from typing import Optional
from .general import decode, are_close, are_aligned


DIRECTIONS = ['N','S','E','W','NE','NW','SE','SW']

# Most of the code is copied from Andrea's exercise
# if something does not work it's probably his fault
# if something does work it's probably thanks to him
class Map:
    def __init__(self, pony:bool = True, level:int = 0):
        env, (self.minXCG, self.maxXCG) = createLevel(level=level, pony=pony)
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
    
    #TODO: optimize possibly using a KB to store position
    def get_element_position(self, element:str) -> (int,int):
        for i in range(len(self.state['screen_descriptions'])):
            for j in range(len(self.state['screen_descriptions'][0])):
                description = decode(self.state['screen_descriptions'][i][j])
                if(element in description):
                    return (i,j)
        #TODO: check if is stepping on before raising exception
        #self.print_every_position()
        raise Exception(f'no {element} is found in this state')

    def get_agent_position(self) -> (int,int):
        return self.get_element_position('Agent')
    # Now unused within the class
    def get_pony_position(self) -> (int,int):
        return self.get_element_position('pony')
    def get_saddle_position(self) -> (int,int):
        return self.get_element_position('saddle')
    
    # just an utility to check position during test
    def print_every_position(self):
        for i in range(len(self.state['screen_descriptions'])):
            for j in range(len(self.state['screen_descriptions'][0])):
                description = decode(self.state['screen_descriptions'][i][j])
                if(description != '' and description != 'floor of a room'):
                    print(f'{description} in <{i},{j}>')
    
    #TODO: discuss with the team on which algorithm to use
    #   things to consider:
    #       A* may be too much
    #       it is easy now but may be harder with monster and secondary task
    #       the environment will not always be a rectangle
    #this will take agent in distance that is <= maxDistance and >= minDistance from the object
    def go_to_element(self, element:str, show_steps:bool=False, graphic:bool=False, delay:float = 0.5, maxDistance:int = 3, minDistance:int = 1) -> None:
        #until we are not close to the pony
        element_pos = self.get_element_position(element=element)
        agent_pos = self.get_agent_position()
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
                self.apply_action(move)
            else:
                self.align_with_target(target=element)
            try:
                element_pos = self.get_element_position(element=element)
            except:
                if(minDistance != 0):
                    raise Exception(f'No {element} is found in this state')
            agent_pos = self.get_agent_position()
            if(show_steps):
                time.sleep(delay)
                self.render(graphic=graphic)
        
    # supposed that the distance between [pony] target and agent is <= 3
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
