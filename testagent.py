from utils.general import decode
from utils.agent import Agent
from utils.map import Map
from utils import exceptions
import numpy as np

level = Map(pony=True)
knight = Agent()

knight.percept(level)

knight.look_for_element(level, element='pony')
try:
    x,y = knight.kb.get_element_position('pony')
    print(f'The KB says that there is a pony in position ({x},{y})')
except exceptions.ElemNotFoundException as exc:
    print(f'ElemNotFoundException catturata con successo. '
        f'Restituisce il messaggio: {exc}')

#let's see in the knowledge base

carrot_query = knight.kbQuery('position(comestible,carrot,X,Y)')
for positions in carrot_query:
    print(f'KB says there is a carrot in position ({positions["X"]},{positions["Y"]})')

saddle_query = knight.kbQuery('position(saddle,_,X,Y)')
for positions in saddle_query:
    print(f'KB says there is a saddle in position ({positions["X"]},{positions["Y"]})')
xsaddle, ysaddle = level.get_element_position('saddle')[0]
print(f'Agent percepts saddle is in position ({xsaddle},{ysaddle})')

agent_query = knight.kbQuery('position(agent,_,X,Y)')
for positions in agent_query:
    print(f'KB says agent is in position ({positions["X"]},{positions["Y"]})')
xagent, yagent = level.get_element_position('Agent')[0]
print(f'Agent is in position ({xagent},{yagent})')
# it seems to be working. Of course, this way of querying is very
# "crude", and looks a real mess right now. Things will be fixed, 
# and cleaned. Fear not.