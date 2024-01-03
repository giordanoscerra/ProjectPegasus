from pyswip import Prolog
from utils import exceptions
from heuristics import infinity_distance

class KBwrapper():
    # It is here on purpose: it is a class variable ("knowledge" shared
    # among all instances of the class). I think it is more proper.
    # changes to this reflect to all KBwrapper objects 
    # (most probabily we'll have only one, so who cares...)
    _categories = {
        'enemy': ['kobold', 'giant mummy', 'goblin', 'lichen'],
        'comestible': ['apple', 'carrot', 'food ration'],
        'weapon': ['sword', 'lance', 'shield', 'dagger'],
        'applicable' : ['saddle'],
        'steed' : ['pony', 'horse', 'warhorse'],
    }
    encumbrance_messages = {
        "unencumbered" : [None,"Your movements are now unencumbered."],
        "burdened" : ["Your movements are slowed slightly because of your load.", "Your movements are only slowed slightly because of your load"],
        "stressed" : ["You rebalance your load. Movement is difficult.", "You rebalance your load. Movement is still difficult."],
        "strained" : ["You stagger under your load. Movement is very hard.", "You stagger under your load. Movement is still very hard."],
        "overtaxed" : ["You can barely move a handspan with this load!", None],
        "overloaded" : ["You collapse under your load.", None]
    }
    riding_skill = {
        "unskilled" : -20,
        "basic" : 0,
        "skilled" : 15,
        "expert" : 30
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

    # ---------------- element position related methods START ----------------     
    def get_element_position_query(self, element:str):
        element = element.lower()   # pointless. Just to be sure
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
                 'Maybe they are not in the environment? Query sentence: '+query_sentence)
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
            self._kb.retractall(f'position({element.lower()},{element.lower()},{x},{y})')
        else:
            self._kb.retractall(f'position({category},{element.lower()},{x},{y})')

    def assert_element_position(self,element:str, x:int, y:int):
        category = self._get_key(element, self._categories)
        if category is None:
            self._kb.asserta(f'position({element.lower()},{element.lower()},{x},{y})')
        else:
            self._kb.asserta(f'position({category},{element.lower()},{x},{y})')

    # ---------------- element position related methods END ----------------
            


    # ---------------- explore subtask related methods START ----------------
            
    def assert_full_visited(self):
        tot = list(self._kb.query("fullyExplored(X)"))[0]['X'] + 1
        self._kb.retractall("fullyExplored(_)")
        self._kb.asserta(f"fullyExplored({tot})")

    # ---------------- explore subtask related methods END ----------------
        


    # ---------------- stepping_on related methods START ----------------
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
        return bool(list(self._kb.query(stepping_on_sentence)))
    
    # ---------------- stepping_on related methods END ----------------



    # ---------------- hostility-related methods START ----------------

    # assert that a certain creature (or its category) is hostile in the kb.
    # It's ok like this for now: when we'll want to implement multiple steeds or good and bad monsters we'll modify this.
    # It's not ok anymore, we have to modify it now.
    def assert_hostile(self, creature: str):
        category = self._get_key(creature, self._categories)
        if category == 'steed':
            # Hopefully we'll only have one pony 
            if not bool(list(self._kb.query(f'hostile({creature})'))):
                self._kb.asserta(f'hostile({creature})')
        else: 
            print("For now, only hostility of steeds is supported")
            #if not bool(list(self._kb.query(f'hostile({creature})'))):
            #    self._kb.asserta(f'hostile({creature})')

    def retract_hostile(self, creature:str):
        category = self._get_key(creature, self._categories)
        if category == 'steed': 
            # Hopefully we'll only have one pony 
            if bool(list(self._kb.query(f'hostile({creature})'))):
                self._kb.retractall(f'hostile({creature})')
        else: 
            print("For now, only hostility of steeds is supported")

    # Q: get_steed_tameness could be used for the same purpose,
    #   but maybe the KB messes up. Who knows.
    def query_hostile(self,creature:str='pony'):
        category = self._get_key(creature, self._categories)
        if category == 'steed':
            return bool(list(self._kb.query(f'hostile({creature})')))
        else:
            print("For now, only hostility of steeds is supported")
            #return bool(list(self._kb.query(f'hostile({creature})')))
    
    # ---------------- hostility-related methods END ----------------



    # ---------------- tameness-related methods START ----------------
    def update_tameness(self, inc:int, steed:str='pony'):
        category = self._get_key(steed, self._categories)
        if category == 'steed':
            try:
                old_t = self.get_steed_tameness(steed)
                # mamma mia che ciofeca sta roba...
                #word = category if category == 'steed' else steed
                self._kb.retractall(f'tameness({steed},_)')
                self._kb.asserta(f'tameness({steed},{old_t+inc})')            
            except IndexError:
                print("update_tameness: the predicate hasn't been found")
        else:
            print('Error: only tameness of steeds can be updated')
    
    def get_steed_tameness(self, steed:str='pony'):
        category = self._get_key(steed, self._categories)
        if category == 'steed': 
            try:
                return list(self._kb.query(f"tameness({steed}, X)"))[0]['X']
            except IndexError:
                print("get_steed_tameness: the predicate hasn't been found")
        else:
            print('Error: only tameness of steeds can be gotten')
    
    # ---------------- tameness-related methods END ----------------
    


    # ---------------- riding and saddled steed-related methods START ----------------
    def get_rideable_steeds(self):
        return self._kb.query("rideable(X)")
    
    def query_riding(self, steed:str):
        category = self._get_key(steed, self._categories)
        if category == "steed": 
          return bool(list(self._kb.query('riding(agent,steed')))
        else: 
          return bool(list(self._kb.query(f'riding(agent,{steed})'))) # when the steed is not a *steed* but, for example, a monster.

    def assert_saddled_steed(self, steed:str):
        category = self._get_key(steed, self._categories)
        if category == 'steed': 
            if not bool(list(self._kb.query(f'saddled({steed})'))):
                self._kb.asserta(f'saddled({steed})')
        else: 
            print("Sorry, only steeds can be saddled!")
          
    def retract_saddled_steed(self, steed:str):
        category = self._get_key(steed, self._categories)
        if category == 'steed': 
            if bool(list(self._kb.query(f'saddled({steed})'))):
                self._kb.retractall(f'saddled({steed})')
        else: 
            print("Sorry, only steeds can be saddled!")
    
    # ---------------- riding and saddled steed-related methods END ----------------

    
    def is_slippery(self):
        return self._kb.query("slippery")[0]
    
    def is_agent_confused(self):
        return self._kb.query("confused(agent)")[0]
    
    def is_agent_fumbling(self):
        return self._kb.query("fumbling(agent)")[0]
    
    def update_encumbrance(self, encumbrance:str):
        for keys in self.encumbrance_messages.keys():
            self._kb.retractall(f'{keys}(agent)')
        self._kb.asserta(f'{encumbrance}(agent)')

    def update_health(self, health:int):
        self._kb.retractall('health(_)')
        self._kb.asserta(f'health({health})')

    def update_quantity(self, item:str, quantity:int):
        if item in ['carrot', 'apple', 'saddle']: 
            item += 's'
        self._kb.retractall(f'{item}(_)')
        self._kb.asserta(f'{item}({quantity})')

    def query_quantity(self, item:str):
        if item in ['carrot', 'apple', 'saddle']: item += 's'
        return list(self._kb.query(f'{item}(X)'))[0]['X']

    # ---------------- has predicate related methods START ----------------
    def assert_has(self, owner:str, item:str):
        ownerCategory = self._get_key(owner, self._categories) if self._get_key(owner ,self._categories) is not None else owner
        itemCategory = self._get_key(item, self._categories) if self._get_key(item ,self._categories) is not None else item
        self._kb.asserta(f'has({ownerCategory},{owner},{itemCategory},{item})')

    # This function is VERY brittle. Basically, it doesn't work in general,
    # but it does the job when (e.g.) not multiple elements of a category exist
    # or just a single possible owner exists
    def retract_has(self, owner:str, item:str):
        ownerCategory = self._get_key(owner, self._categories) if self._get_key(owner ,self._categories) is not None else owner
        itemCategory = self._get_key(item, self._categories) if self._get_key(item ,self._categories) is not None else item
        # Here comes the problem!
        self._kb.retractall(f'has({ownerCategory},{owner},{itemCategory},{item})')

    # ---------------- has predicate related methods END ----------------



    # ---------------- enemies-related methods START ----------------
    def isEnemy(self, element:str):
        category = self._get_key(element, self._categories)
        return category == 'enemy'
    
    
    # I still have to test this
    def query_enemy_to_attack(self):
        enemies_list = list(self._kb.query('attack(X)'))['X']
        print(enemies_list)
        enemy_and_coordinates = []
        coordinates = []
        for enemy in enemies_list:
            enemy_coord = self.get_element_position_query(enemy)
            coordinates.append(enemy_coord)
            enemy_and_coordinates.append([enemy, enemy_coord])
        print(enemy_and_coordinates)
        print(coordinates)
        closest_coord,distance = infinity_distance(self.get_element_position_query('agent'), coordinates)
        print(closest_coord)
        closest_enemy = enemy_and_coordinates[coordinates.index(closest_coord)]
        print(closest_enemy)
        return closest_enemy, distance

    # ---------------- enemies-related methods END ----------------