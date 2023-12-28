from utils.general import decode
import numpy as np
# import os
# import sys
# import string
from nle import nethack
from pyswip import Prolog
from utils import exceptions


class KBwrapper():
    # It is here on purpose: it is a class variable ("knowledge" shared
    # among all instances of the class). I think it is more proper.
    # changes to this reflect to all KBwrapper objects 
    # (most probabily we'll have only one, so who cares...)
    _categories = {
        'enemy': ['kobold', 'giant mummy', 'goblin'],
        'comestible': ['apple', 'carrot', 'food ration'],
        'weapon': ['sword', 'lance', 'shield', 'dagger'],
        'applicable' : ['saddle'],
    }

    def __init__(self):
        self._kb = Prolog()
        self._kb.consult('KBS/kb.pl')

    def queryDirectly(self, sentence:str):
        '''For rapid-test purposes only.
        The function queries the kb for the sentence in input.
        The query method is applied directly to sentence.
        '''
        return list(self._kb.query(sentence))

    # This function is only used by agent._go to closer_element. 
    # For now is very very stupid. Just to get things going
    #def query_for_greenlight(self):
    #    return True

    # this is very experimental
    def query_for_action(self):
        try:
            action = list(self._kb.query("action(X)"))[0]
            action = action['X']
        except Exception as e:
            print(e)
            action = None
        return action
    
    def query_for_interrupt(self, current_subtask):
        try:
            interrupt = bool(list(self._kb.query(f"interrupt({current_subtask})")))
        except Exception as e:
            print(e)
            interrupt = False
        return interrupt
    
    #def assert_performed_action(self):
        # Q: quindi devo dire alla KB l'azione che ho fatto?
        # problema: se ogni azione richiede un formato specifico, in questa funzione
        # c'è un'esplosione di if (ovvero di cose da dire). Non è più chiaro ed 
        # elegante dire la cosa giusta al momento giusto?

    # the idea is that the position of an element should be returned by 
    # the KB        
    def get_element_position_query(self, element:str):
        if element in self._categories.keys():
            query_sentence = f'position({element},_,Row,Col)'
            err_sentence = f'any element in the {element} category '
        else:
            category = self._get_key(element,self._categories) if self._get_key(element,self._categories) else "_"
            query_sentence = f'position({category},{element},Row,Col)'
            err_sentence = f'{element} '
        pos_query = [(q['Row'], q['Col']) for q in self._kb.query(query_sentence)]
        if(pos_query == []):
            raise exceptions.ElemNotFoundException\
                ('query for the position of '+err_sentence+'unsuccessful. '
                 'Maybe they are not in the environment?')
        else:
            return pos_query
        
    def _get_key(self,value, dictionary):
        for key, values in dictionary.items():
            if value in values:
                return key
        return None   
    
    def retract_element_position(self, element:str, *args):
        if(len(args) == 0):
            x, y = '_','_'
        else:
            x, y = args

        category = self._get_key(element, self._categories)
        if category is None:
            self._kb.retractall(f'position({element},{element},{x},{y})')
        else:
            self._kb.retractall(f'position({category},{element},{x},{y})')

    def assert_element_position(self,element:str, x:int, y:int):
        category = self._get_key(element, self._categories)
        if category is None:
            self._kb.asserta(f'position({element},{element},{x},{y})')
        else:
            self._kb.asserta(f'position({category},{element},{x},{y})')

    def retractall_stepping_on(self):
        self._kb.retractall('stepping_on(agent,_,_)')

    def assert_stepping_on(self, spaced_elem:str):
        element = spaced_elem.replace(' ','')
        category = self._get_key(spaced_elem, self._categories)
        if category is None:
            self._kb.asserta(f'stepping_on(agent,{element},{element})')
        else:
            self._kb.asserta(f'stepping_on(agent,{category},{element})')

    def query_stepping_on(self, spaced_elem:str):
        element = spaced_elem.replace(' ','')
        category = self._get_key(spaced_elem, self._categories)
        stepping_on_sentence = f'stepping_on(agent,{category},{element})' if category is None else f'stepping_on(agent,_,{element})'
        return bool(self._kb.query(stepping_on_sentence))

    def update_tameness(self, inc:int, steed:str):
        try:
            old_t = list(self._kb.query(f'tameness({steed},X)'))[0]['X']
            self._kb.retractall(f'tameness({steed},_)')
            self._kb.asserta(f'tameness({steed},{old_t+inc})')            
        except IndexError:
            print('The predicate hasn\'t been found')

    def get_rideable_steeds(self):
        return self._kb.query("rideable(X)")
    
    def get_steed_tameness(self, steed):
        return list(self._kb.query(f"steed_tameness({steed}, X)"))[0]['X']
    
    def is_slippery(self):
        return self._kb.query("slippery")[0]

    def update_health(self, health:int):
        self._kb.retractall('health(_)')
        self._kb.asserta(f'health({health})')

    def update_quantity(self, item:str, quantity:int):
        if item == 'carrot':
            item += 's'
        if item == 'saddle':
            item += 's'
        if item == 'apple':
            item += 's'
        self._kb.retractall(f'{item}(_)')
        self._kb.asserta(f'{item}({quantity})')