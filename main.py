from utils.map import Map

level = Map()


for i in range(3):
    level.go_near_pony(show_steps=True)
    throw_direction = level.throw_to_pony_direction()
    level.apply_action('THROW', what='carrot', where=throw_direction)
    level.render(delay=3)

level.go_near_pony(show_steps=True, maxDistance=1)
throw_direction = level.throw_to_pony_direction()
#ride pony
level.apply_action('RIDE', where=throw_direction)
level.render()
#print(level.get_agent_position())
#print(level.get_pony_position())
#level.print_every_position()