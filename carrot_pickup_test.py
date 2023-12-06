from utils.map import Map

level = Map(pony=False)

#go to carrot
level.go_to_element(element='carrot',show_steps=True, delay=0.2, maxDistance=0, minDistance=0)
level.render()
#pick up carrot
level.apply_action('PICKUP')
level.render()
level.apply_action('S')
level.render()
#print rewards
print(level.rewards)
#print inventory
level.print_inventory()