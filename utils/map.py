import time
import gym
import numpy as np
from minihack import LevelGenerator
from nle import nethack

from typing import Optional, List, Tuple
from .general import decode
from .rewards import define_reward
from . import exceptions 


DIRECTIONS = ['N','S','E','W','NE','NW','SE','SW']

# Most of the code is copied from Andrea's exercise
# if something does not work it's probably his fault
# if something does work it's probably thanks to him
class Map:
    def __init__(self, pony:bool = True):
        lvl = LevelGenerator(w=20,h=20)
        self.rewards = []
        reward_manager_defined = define_reward()
        if(pony):
            lvl.add_monster(name='pony', symbol="u", place=None)
        lvl.add_object(name='carrot', symbol="%", place=(0,0))
        lvl.add_object(name='carrot', symbol="%", place=(0,0))
        for _ in range(3):
            lvl.add_object(name='carrot', symbol="%", place=None)
        lvl.add_object(name='saddle', symbol="(", place=None)
        # mura tutt'attorno. Più carino. E più challenging per il pathfinding
        lvl.wallify()  
        env = gym.make(
            'MiniHack-Skill-Custom-v0',
            actions = tuple(nethack.CompassDirection) + (
                nethack.Command.THROW,
                nethack.Command.RIDE,
                nethack.Command.EAT,
                nethack.Command.DROP,
                nethack.Command.APPLY,
                nethack.Command.PICKUP,
                nethack.Command.WHATIS,
                nethack.Command.INVENTORY,# included to allow use of saddle (i)
                nethack.Command.RUSH,# included to allow use of apple (g)
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
                'pixel',
                'blstats'),
            des_file = lvl.get_des(),
            reward_manager = reward_manager_defined,
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
            raise Exception(f'Valid directions are {DIRECTIONS}')
        if(what is not None and self._get_item_char(what) is None):
            raise Exception(f'Object <{what}> is not in inventory')
        elif(what is not None):
            print(f'Object <{what}> is in inventory')
            #print inventory
            self.print_inventory()
            what = self._get_item_char(what)
            print(f'Object <{what}> is in inventory')

        self.state,reward,_,_ = self._env.step(self._get_action_id(action=actionName)) # action            
        if(what is not None): self.state,reward,_,_ = self._env.step(self._env.actions.index(ord(what)))# object
        if(where is not None): self.state,reward,_,_ = self._env.step(self._get_action_id(action=where)) # direction
        #TODO: if a KB is used it should be updated here since we have a new state

        self.rewards.append(reward)

    def render(self, delay:float = 0.5):
        time.sleep(delay)
        self._env.render()
    
    #TODO: optimize possibly using a KB to store position: DONE (in a certain sense)
    # This function is used by agent.look_for_closest()
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
    
    # just an utility to check position during test
    def print_every_position(self):
        for i in range(len(self.state['screen_descriptions'])):
            for j in range(len(self.state['screen_descriptions'][0])):
                description = decode(self.state['screen_descriptions'][i][j])
                if(description != '' and description != 'floor of a room'):
                    print(f'{description} in <{i},{j}>')
        
    # supposed that the distance between pony and agent is <= 3
    def align_with_pony(self) -> str:
        pony_pos = self.get_pony_position()
        agent_pos = self.get_agent_position()
        agent_pos = (agent_pos[0] - pony_pos[0], agent_pos[1] - pony_pos[1])
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
    
    def get_pony_direction(self) -> str:
        pony_pos = self.get_pony_position()
        agent_pos = self.get_agent_position()
        agent_pos = (agent_pos[0] - pony_pos[0], agent_pos[1] - pony_pos[1])
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

    def print_inventory(self):
        for letter, stringa in \
            zip(decode(self.state["inv_letters"]), self.state["inv_strs"]):
            print(letter, " - ", decode(stringa))

# ottiene la posizione dell'entità che nella mappa appare con symbol
# Ovviamente, se ce n'è più di una vanno cambiate delle cose...
def get_location(game_map: np.ndarray, symbol: str):
    x, y = np.where(game_map == ord(symbol))
    return x[0], y[0]