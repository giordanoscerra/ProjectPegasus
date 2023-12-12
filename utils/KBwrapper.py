from uu import decode
import numpy as np
import os
import sys
import string
from nle import nethack
from pyswip import Prolog


class KBwrapper():
    def __init__(self):
        self._kb = Prolog()
        # for now, I consult the KB from the hands_on2
        # 
        # Moreover, I don't really like this, but I don't have a 
        # good way to get the path of kb_handson2.pl relative to the
        # path of the script in current execution
        current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        kb_path = os.path.join(current_dir, 'KBS/kb_handson2.pl')
        self._kb.consult(kb_path)

        #self._kb.consult('../KBS/kb_handson2.pl')

    # this is very experimental
    def query_for_action(self):
        try:
            action = list(self.kb.query("action(X)"))[0]
            action = action['X']
        except Exception as e:
            action = None
        return action
    
    #def assert_performed_action(self):
        # Q: quindi devo dire alla KB l'azione che ho fatto?
        # problema: se ogni azione richiede un formato specifico, in questa funzione
        # c'è un'esplosione di if (ovvero di cose da dire). Non è più chiaro ed 
        # elegante dire la cosa giusta al momento giusto?

    def assert_position_of_elements(self, scr_desc:np.ndarray):
        # DavideB will kill me for this...
        #
        # IDEA: this function is called after each env.step().
        # it scans the whole map, by the same approach we used in the Map class
        # and asserts the position of each notable element. 
        # When we need the position of an element we query the KB, instead of scanning 
        # the whole map each time.
        # We need to assert the position of the various notable elements because
        # they might change after each env.step() (e.g. enemies move, carrots get stolen...)
        self._kb.retractall("position(_,_,_,_)")
        interesting_item_list = ['carrot', 'saddle', 'pony', 'Agent']
        for i in range(len(scr_desc)):
            for j in range(len(scr_desc[0])):
                description = decode(scr_desc[i][j])
                if(description != '' and description != 'floor of a room'):
                    for interesting_item in interesting_item_list:
                        if interesting_item in description:
                            self._kb.asserta(f'position({interesting_item},_,{i},{j})')

    # the idea is that the position of an element should be returned by 
    # the KB
    # Q1: deal with multiple items in the map (e.g. two carrots)
    def get_element_position(self, element:str):
        pos_query = list(self._kb.query(f'position({element},_,Row,Col)'))[0]
        return (pos_query['Row'], pos_query['Col'])