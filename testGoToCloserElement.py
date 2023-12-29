from utils.map import Map
from utils.agent import Agent
from utils.general import decode

lvl = Map(pony=False, level=6)
#the name of the knight is Yoritomo
yoritomo = Agent()

yoritomo.go_to_closer_element(lvl,element='saddle',show_steps=False,delay=0.2)

message=decode(lvl.state['message'])
if 'You see here a saddle' in message:
    print('test go to closer element passed')
else:
    print('test go to closer element failed')