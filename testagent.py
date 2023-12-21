from utils.general import decode
from utils.agent import Agent
from utils.map import Map
from utils import exceptions
import numpy as np

level = Map(pony=False)
knight = Agent()

knight.look_for_element(level, element='pony')
try:
    x,y = knight.kb.get_element_position('pony')
    print(f'The KB says that there is a pony in position ({x},{y})')
except exceptions.ElemNotFoundException as exc:
    print(f'L\' eccezione ElemNotFoundException è stata catturata '
        f'con successo, e restituisce il messaggio: {exc}')
    
knight.percept(level)

#let's see in the knowledge base
knb = knight.kb

carrot_query = list(knb._kb.query('position(comestible,F,X,Y)'))
# one can check that it didn't work

saddle_query = list(knb._kb.query('position(saddle,_,X,Y)'))
xsaddle, ysaddle = level.get_element_position('saddle')

agent_query = list(knb._kb.query('position(Agent,_,X,Y)'))
xagent, yagent = level.get_element_position('Agent')
# OK, non funziona nulla. Le asserzioni vengono fatte molto male
# a quanto pare, per qualche motivo.