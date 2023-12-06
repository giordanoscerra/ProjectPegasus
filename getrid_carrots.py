# very simple program to make the knight get rid of its carrots
from utils.map import Map

level = Map(pony = False, lava = True)
level.render()

# goes towards the lava pool
level.go_to_element(element='lava', show_steps=True, maxDistance=1, minDistance=1)

##kicks the object repeatedly (until it breaks open)
#box_direction = level.get_target_direction(target='box')
#message = ""
#while("open" not in message):
#    level.apply_action(actionName='KICK', where=box_direction)
#    level.render()
#    message = level.get_message()
#
## picks the large box up (necessary to put stuff in)
#level.apply_action(actionName=box_direction)
#level.apply_action(actionName='PICKUP')
#level.render()
#level.print_inventory()
#
## put stuff in box
#level.apply_action(actionName='APPLY', what='box')
#level.render()
#print(level.get_message())
