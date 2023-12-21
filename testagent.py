from utils.general import decode
from utils.agent import Agent
from utils.map import Map
import numpy as np

level = Map(pony=False)
knight = Agent()

knight.percept(level)
