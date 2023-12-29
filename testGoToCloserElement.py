from utils.map import Map
from utils.agent import Agent

lvl = Map(pony=False, level=6)
#the name of the knight is Yoritomo
yoritomo = Agent()

lvl.render()

yoritomo.go_to_closer_element(lvl,element='saddle',show_steps=True,delay=0.2)
lvl.render()