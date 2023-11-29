from utils.map import Map

level = Map()


for i in range(7):
    level.go_near_pony(show_steps=True)
    throw_direction = level.throw_to_pony_direction()
    level.apply_action('THROW', what='carrot', where=throw_direction)
    level.render(delay=3)

#print(level.get_agent_position())
#print(level.get_pony_position())
#level.print_every_position()