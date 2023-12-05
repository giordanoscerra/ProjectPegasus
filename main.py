from utils.map import Map

level = Map()

#go to saddle
level.go_to_element(element='saddle',show_steps=True, maxDistance=0, minDistance=0)
level.render()

#pick up saddle
level.apply_action('PICKUP')
level.render()

#go to pony and throw carrots
for i in range(9):
    level.go_to_element(element='pony',show_steps=True)
    throw_direction = level.get_pony_direction()
    level.apply_action('THROW', what='carrot', where=throw_direction)
    level.render(delay=1)

#saddle pony
level.go_to_element(element='pony',show_steps=True, maxDistance=1)
saddle_direction = level.get_pony_direction()
level.apply_action('APPLY', what='saddle', where=saddle_direction)
level.render()

#ride pony
level.go_to_element(element='pony',show_steps=True, maxDistance=1)
ride_direction = level.get_pony_direction()
level.apply_action('RIDE', where=ride_direction)
level.render()
#print(level.get_agent_position())
#print(level.get_pony_position())
#level.print_every_position()