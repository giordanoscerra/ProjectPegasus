from utils.general import decode
from utils.agent import Agent
from utils.map import Map
from utils import exceptions
import numpy as np

level = Map(pony=False)
knight = Agent()

print('Starting inventory: ')
level.print_inventory()

decoded_str_dict = {decode(str):str for str in level.state['inv_strs']}

# remove the letter relative to carrot entry in inventory
# (it is always the last one)
inv_l = level.state['inv_letters']
inv_l[np.nonzero(inv_l)[0][-1]] = 0

# set to zero the whole row saying that there are carrots
# (always the last one)
inv_s = level.state['inv_strs']
nonzero_rows = np.where(np.any(inv_s, axis=1))[0]
inv_s[nonzero_rows[-1],:] = 0


level.print_inventory()
print('Puf! Carrots are gone!... \n ...Or are they?')

level.apply_action('N')

level.print_inventory()
print('As you can see, unfortunately, the carrots reappeared.')

