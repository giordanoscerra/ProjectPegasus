from utils.general import decode
import numpy as np
# import os
# import sys
# import string
from nle import nethack
from pyswip import Prolog
from utils import exceptions


class KBwrapper():
    # It is hee on purpose: it is a class variable ("knowledge" shared
    # among all instances of the class). I think it is more proper.
    # changes to this reflect to all KBwrapper objects 
    # (most probabily we'll have only one, so who cares...)
    _categories = {
        'enemy': ['kobold', 'giant mummy', 'goblin'],
        'comestible': ['apple', 'carrot', 'food ration'],
        'weapon': ['sword', 'lance', 'shield', 'dagger'],
    }

    def __init__(self):
        self._kb = Prolog()
        # for now, I consult the KB from the hands_on2
        # 
        # Moreover, I don't really like this, but I don't have a 
        # good way to get the path of kb_handson2.pl relative to the
        # path of the script in current execution
        # current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        # kb_path = os.path.join(current_dir, 'KBS/kb_handson2.pl')
        # self._kb.consult(kb_path)

        self._kb.consult('KBS/kb_handson2.pl')

    # this is very experimental
    def query_for_action(self):
        try:
            action = list(self._kb.query("action(X)"))[0]
            action = action['X']
        except Exception as e:
            print(e)
            action = None
        return action
    
    #def assert_performed_action(self):
        # Q: quindi devo dire alla KB l'azione che ho fatto?
        # problema: se ogni azione richiede un formato specifico, in questa funzione
        # c'è un'esplosione di if (ovvero di cose da dire). Non è più chiaro ed 
        # elegante dire la cosa giusta al momento giusto?

    # the idea is that the position of an element should be returned by 
    # the KB
    # TODO: deal with multiple items in the map (e.g. two carrots).See also 
    # comment on the _element_position() function
    def get_element_position(self, element:str):
        try:
            pos_query = list(self._kb.query(f'position({element},_,Row,Col)'))[0]
            return (pos_query['Row'], pos_query['Col'])
        except IndexError:
            raise exceptions.ElemNotFoundException\
                (f'query for the position of {element} unsuccessful. '
                'Maybe is not in the environment?')
        
    def _get_key(self,value, dictionary):
        for key, values in dictionary.items():
            if value in values:
                return key
        return None   
    
    # TODO: deal with the second argument in the assertion.
    # The problem is that we might want to distinguish
    # certain elements among themselves by changing their "names"
    # (2nd argument in the position(_,_,_,_) assertion), in order to store 
    # their position independently (e.g carrot1 is in a certain position,
    # carrot2 is somewhere else). But we also want to use their names for 
    # inference!
    # Maybe this is not a real problem, as we'll have different predicates of 
    # the form position(*), and what makes them different is the coordinates 
    # (arguments 3 and 4). 
    # I think that we should consider adding a further parameter to the 
    # position statement, to keep track of the indexing of the different 
    # elements.     
    def retract_element_position(self, element:str, x:str='_', y:str='_'):
        category = self._get_key(element, self._categories)
        if category is None:
            # IDEA: if the element has no category, maybe it is a 
            # category on its own (or at least dealt as such by the KB)
            self._kb.retractall(f'position({element},_,{x},{y})')
        else:
            self._kb.retractall(f'position({category},{element},{x},{y})')

    def assert_element_position(self,element:str, x:int, y:int):
        category = self._get_key(element, self._categories)
        if category is None:
            self._kb.asserta(f'position({element},_,{x},{y})')
        else:
            # problem: keep the distinction between (e.g.) the carrot 
            # and the specific carrot. This has to be dealt with.
            self._kb.asserta(f'position({category},{element},{x},{y})')