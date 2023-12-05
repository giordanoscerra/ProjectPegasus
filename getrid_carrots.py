# very simple program to make the knight get rid of its carrots
from utils.map import Map

level = Map(pony = False, sink = True)
level.render()

# goes towards the sink
level.go_to_element(element='sink', show_steps=True, maxDistance=1, minDistance=1)

level.throw_all(item = 'carrot', direction='SE')
#print(f'index is: {x}, and the number is {n}')
level.print_inventory()