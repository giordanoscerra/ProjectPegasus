import time
import gym
import numpy as np
from minihack import LevelGenerator
from nle import nethack

from typing import Optional
from utils.general import decode, are_close, are_aligned


DIRECTIONS = ['N','S','E','W','NE','NW','SE','SW']

# Most of the code is copied from Andrea's exercise
# if something does not works it is probably its fault
# if something does work it is probably thanks to him
class Map:
    def __init__(self, pony:bool = True, lava:bool = False):
        lvl = LevelGenerator(w=20,h=20)
        if(pony):
            lvl.add_monster(name='pony', symbol="u", place=None)
        if(lava):
            lvl.set_start_rect((0,0),(2,2)) # creates an area in which the agent can spawn
            lvl.add_terrain(flag="L", coord=(5,6))
        lvl.add_object(name='saddle', symbol="(", place=None, cursestate="blessed")
        env = gym.make(
            'MiniHack-Skill-Custom-v0',
            actions = tuple(nethack.CompassDirection) + (
                nethack.Command.THROW,
                nethack.Command.RIDE,
                nethack.Command.EAT,
                nethack.Command.DROP,
                nethack.Command.APPLY,
                nethack.Command.PICKUP,
                nethack.Command.INVENTORY,# included to allow use of saddle (i)
                nethack.Command.RUSH,# included to allow use of apple (g)
                nethack.Command.KICK,
            ),
            character = "kn-hum-neu-mal",
            observation_keys = (
                'glyphs',
                'chars',
                'screen_descriptions',  # descrizioni testuali di ogni cella della mappa 
                'message',
                'inv_strs',
                'inv_letters',
                'pixel'),
            des_file = lvl.get_des(),
        )
        self.state = env.reset()
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
        #TODO: if a KB is used it should be updated here since we have a new state


    def render(self, delay:float = 0.5):
        time.sleep(delay)
        self._env.render()

    
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
    
    #TODO: discuss with the team on wich algorithm to use
    #   things to consider:
    #       A* may be too much
    #       it is easy now but may be harder with monster and secondary task
    #       the environment will not always be a rectangle
    #this will take agent in distance that is <= maxDistance and >= minDistance from the object
    def go_to_element(self, element:str, show_steps:bool=False, delay:float = 0.5, maxDistance:int = 3, minDistance:int = 1) -> None:
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
                self.align_with_pony()
            try:
                element_pos = self.get_element_position(element=element)
            except:
                if(minDistance != 0):
                    raise Exception(f'No {element} is found in this state')
            agent_pos = self.get_agent_position()
            if(show_steps):
                time.sleep(delay)
                self.render()
        
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

# ottiene la posizione dell'entità che nella mappa appare con symbol
# Ovviamente, se ce n'è più di una vanno cambiate delle cose...
def get_location(game_map: np.ndarray, symbol: str):
    x, y = np.where(game_map == ord(symbol))
    return x[0], y[0]