from utils.map import Map

for iter in range(100):

    level = Map()

    #go to pony and throw carrots
    for i in range(9):
        level.go_to_element(element='pony',show_steps=False)
        throw_direction = level.get_pony_direction()
        level.apply_action('THROW', what='carrot', where=throw_direction)
        #level.render(delay=0)

    #go to saddle
    level.go_to_element(element='saddle',show_steps=False, maxDistance=0, minDistance=0)
    #level.render(delay=0)

    #pick up saddle
    level.apply_action('PICKUP')
    #level.render(delay=0)

    #saddle pony
    level.go_to_element(element='pony',show_steps=False, maxDistance=1)
    saddle_direction = level.get_pony_direction()
    level.apply_action('APPLY', what='saddle', where=saddle_direction)
    #level.render(delay=0)

    #ride pony
    level.go_to_element(element='pony',show_steps=False, maxDistance=1)
    ride_direction = level.get_pony_direction()
    level.apply_action('RIDE', where=ride_direction)


    print('iteration ', iter, ' completed')
    #level.render(delay=0)
    #print(level.get_agent_position())
    #print(level.get_pony_position())
    #level.print_every_position()