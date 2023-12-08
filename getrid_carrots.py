# very simple program to make the knight get rid of its carrots
from utils.map import Map

level = Map(pony = True, lava = True)
level.render()

# goes towards the lava pool
level.go_to_element(element='lava', show_steps=True, maxDistance=4, minDistance=1)

# aligns with lava

# throws the carrots in the lava pool
lava_direction = level.get_target_direction(target='lava')
level.throw_all(item = 'carrot', direction=lava_direction, show_inventory=True)

# print what's remaining
level.render()
level.print_every_position()    # no carrots in the environment!

# It works, the only problem is that while the agent is emptying 
# his pocket, the pony arrives to kick him.
# This of course can change with level design or other choices.