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

carrot_query = knight.kbQuery('position(comestible,carrot,X,Y)')

saddle_query = knight.kbQuery('position(saddle,_,X,Y)')
xsaddle, ysaddle = level.get_element_position('saddle')

agent_query = knight.kbQuery('position(agent,_,X,Y)')
xagent, yagent = level.get_element_position('Agent')
# it seems to be working. Of course, this way of querying is very
# "crude", and looks a real mess right now. Things will be fixed, 
# and cleaned. Fear not.