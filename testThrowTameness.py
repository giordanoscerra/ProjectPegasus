from utils.map import Map
from utils.agent import Agent
from typing import Dict

saddle_present = False
level = Map(level = 42, pony=True, saddle=saddle_present, 
            peaceful_steeds=True)
knight = Agent()

to_perceive = ['carrot', 'saddle', 'pony', 'horse', 'warhorse','Agent', 'wall']

def update_tameness_dict(diz:Dict[str,int]):
    for q in knight.kbQuery('tameness(S,T)'):
        diz[q['S']+'_tameness'] = q['T']

def update_tameness_dictMk2(diz:Dict[str,int]):
    for steed in ['pony','horse','warhorse']:
        diz[steed+'_tameness'] = knight.kb.get_steed_tameness(steed)

level.render()
knight.percept(level, interesting_item_list=to_perceive)

tameness_dict={}
update_tameness_dictMk2(tameness_dict)
print('Starting tameness: ')
print(tameness_dict)

for thr in ['N','W','E']:
    knight.throw_element(level,throwDir=thr)
    #knight.percept(level, interesting_item_list=to_perceive)
    update_tameness_dictMk2(tameness_dict)
    level.render()
    print(f'After throwing carrot in direction {thr}, tameness are: ')
    print(tameness_dict)

    

