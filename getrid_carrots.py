# very simple program to make the knight get rid of its carrots
from utils.map import Map

level = Map(pony = False, sink = True)
level.render()

# goes towards the sink
level.go_to_element(element='sink', show_steps=True, maxDistance=0, minDistance=0)

# throws all the carrots
level.apply_action(actionName='DROP', what='carrot')
level.render()
level.print_inventory()