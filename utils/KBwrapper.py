from utils.general import decode
import numpy as np
# import os
# import sys
# import string
from nle import nethack
from pyswip import Prolog
from utils import exceptions


class KBwrapper():
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

    # Before you start killing me (I'm Andrea) here is why this function is
    # comment and shouldn't be used: it is the agent through its percepts
    # that must add informations to the kb (it does so with the intermediation
    # of this class methods). My idea is that in the main.py we declare 
    # the agent, and the agent possesses the (or more...) kb as attribute(s),
    # which are instances of this class.
    # 
    #def assert_position_of_elements(self, scr_desc:np.ndarray):
    #    # DavideB will kill me for this...
    #    #
    #    # IDEA: this function is called after each env.step().
    #    # it scans the whole map, by the same approach we used in the Map class
    #    # and asserts the position of each notable element. 
    #    # When we need the position of an element we query the KB, instead of scanning 
    #    # the whole map each time.
    #    # We need to assert the position of the various notable elements because
    #    # they might change after each env.step() (e.g. enemies move, carrots get stolen...)
    #    self._kb.retractall("position(_,_,_,_)")
    #    interesting_item_list = ['carrot', 'saddle', 'pony', 'Agent']
    #    for i in range(len(scr_desc)):
    #        for j in range(len(scr_desc[0])):
    #            description = decode(scr_desc[i][j])
    #            if(description != '' and description != 'floor of a room'):
    #                for interesting_item in interesting_item_list:
    #                    if interesting_item in description:
    #                        self._kb.asserta(f'position({interesting_item},_,{i},{j})')

    # the idea is that the position of an element should be returned by 
    # the KB
    # Q1: deal with multiple items in the map (e.g. two carrots)
    # Q2: what if the element is not found? I'd raise an exception
    def get_element_position(self, element:str):
        try:
            pos_query = list(self._kb.query(f'position({element},_,Row,Col)'))[0]
            return (pos_query['Row'], pos_query['Col'])
        except IndexError:
            raise exceptions.ElemNotFoundException\
                (f'query for the position of {element} unsuccessful. '
                'Maybe is not in the environment?')
    
    # TODO: deal with the _ argument in the assertion, maybe by passing
    # an optional further optional parameter, gathered in *args or **kwargs.
    # it is important, as often we don't want to retract the position of 
    # all (e.g.) enemies, but only specific ones.
    # This is very much tied to the semantic of the handson2 kb, though
    def retract_element_position(self, element:str):
        self._kb.retractall(f'position({element},_,_,_)')

    def assert_element_position(self,element:str, x:int, y:int):
        self._kb.asserta(f'position({element},_,{x},{y})')
    
    def get_rideable_steeds(self):
        return self._kb.query("rideable(X)")
    
    def get_steed_tameness(self, steed):
        return self._kb.query(f"steed_tameness({steed}, X)")[0]['X']
