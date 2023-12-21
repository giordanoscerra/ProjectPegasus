from utils.general import decode
from utils.agent import Agent
from utils.map import Map
from utils import exceptions
import numpy as np

level = Map(pony=True)
knight = Agent()

knight.percept(level)
try:
    x,y = knight.kb.get_element_position('pony')
    print(f'The KB says that there is a pony in position ({x},{y})')
except exceptions.ElemNotFoundException as exc:
    print(f'L\' eccezione ElemNotFoundException è stata catturata '
        f'con successo, e restituisce il messaggio: {exc}')