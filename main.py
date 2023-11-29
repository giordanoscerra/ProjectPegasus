from utils.map import Map

level = Map()

level.apply_action('S')
level.apply_action('THROW','carrot', 'S')
level.render()