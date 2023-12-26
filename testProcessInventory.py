from utils.agent import Agent
from utils.heuristics import manhattan_distance
from utils.map import Map

level = Map(pony=False)
#sam is a classical knight name
sam = Agent()

sam.process_inventory(level)
initialCarrots = sam.kbQuery('carrots(X)')[0]['X']

def goAndPick(level:Map,agent:Agent,element:str):
    agent.percept(level)
    agent.go_to_closer_element(level,element=element,show_steps=False,
                            delay=0.2,heuristic=lambda x,y: manhattan_distance([x],y)[1])
    level.apply_action('PICKUP')

for _ in range(4):
    goAndPick(level,sam,'carrot')
goAndPick(level,sam,'saddle')

sam.process_inventory(level)
finalCarrots = sam.kbQuery('carrots(X)')[0]['X']
saddle = sam.kbQuery('saddles(X)')[0]['X']
assert initialCarrots < finalCarrots + 4
assert saddle == 1

print('test process inventory passed')