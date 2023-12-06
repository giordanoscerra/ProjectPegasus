# very simple program to make the knight get rid of its carrots
from utils.map import Map

level = Map(pony = False, sink = True)
level.render()

# goes towards the sink
level.go_to_element(element='sink', show_steps=True, maxDistance=1, minDistance=1)

throw_direction = level.get_target_direction('sink')

# throws all the carrots
level.throw_all(item = 'carrot', show_inventory=True, direction=throw_direction)
level.render()
level.print_inventory()