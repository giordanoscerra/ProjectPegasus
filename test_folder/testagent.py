from utils.general import decode
from utils.agent import Agent
from utils.map import Map
from utils import exceptions
import numpy as np

level = Map(pony=True)
knight = Agent()

knight.percept(level)

try:
    x,y = knight.closest_element_position('pony')
    print(f'The KB says that there is a pony in position ({x},{y})')
except exceptions.ElemNotFoundException as exc:
    print(f'ElemNotFoundException catturata con successo. '
        f'Restituisce il messaggio: {exc}')

#let's see in the knowledge base

#carrot_query = knight.kbQuery('position(comestible,carrot,X,Y)')
carrot_query = knight.kb.get_element_position_query('carrot')
for positions in carrot_query:
    #print(f'KB says there is a carrot in position ({positions["X"]},{positions["Y"]})')
    print(f'KB says there is a carrot in position {positions}')

#saddle_query = knight.kbQuery('position(saddle,_,X,Y)')
saddle_query = knight.kb.get_element_position_query('saddle')
for positions in saddle_query:
    #print(f'KB says there is a saddle in position ({positions["X"]},{positions["Y"]})')
    print(f'KB says there is a saddle in position {positions}')
xsaddle, ysaddle = level.get_element_position('saddle')[0]
print(f'According to the map, the saddle is in position ({xsaddle},{ysaddle})')

#agent_query = knight.kbQuery('position(agent,_,X,Y)')
agent_query = knight.kb.get_element_position_query('agent')[0]
print(f'KB says agent is in position {agent_query}')

xagent, yagent = level.get_element_position('Agent')[0]
print(f'Agent is in position ({xagent},{yagent})')

print('Agent interesting attributes: ')
for attribute in knight.attributes:
    print(attribute + " : " + str(knight.attributes[attribute]))

print('Agent encumbrances: ' + str(knight.attributes['encumbrance']))
# it seems to be working. Of course, this way of querying is very
# "crude", and looks a real mess right now. Things will be fixed, 
# and cleaned. Fear not.