from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance
from utils.map import Map
from utils.agent import Agent
from utils import exceptions

level = Map(level = 74, pony=True, peaceful=False, enemy=True)
knight = Agent()

knight.percept(level)

for _ in range(knight.kbQuery('carrots(X)')[0]['X']):
    level.apply_action('EAT',what='carrot')
    level.render()
    knight.percept(level)

knight.percept(level)
level.render()