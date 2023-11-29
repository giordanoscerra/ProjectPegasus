from minihack.reward_manager import Event


# These are the events needed by the reward manager to reward the agent for the actions we want them to do.
# To create one, it is needed to inherit from the Event class, implement the check method and eventually the reset method.
# The check method is called at each step of the game and it is used to check if the event has happened.
# GitHub copilot thinks: The reset method is called at the end of each episode and it is used to reset the event's internal state. I personally do not know - Yuri
# previous_state and state are tuples: they are subdivided by the observation keys we defined in the map.py, apparently.

# The PickCarrotEvent is used to reward the agent for picking up a carrot.
class PickCarrotEvent(Event):
    def __init__(self, reward = 1, repeatable = True, terminal_required = False, terminal_sufficient = False):
        super().__init__(reward, repeatable, terminal_sufficient, terminal_required)
    
    
    def check(self, previous_state, action, state):
        return previous_state['inv_strs'].count(b'carrot') < state['inv_strs'].count(b'carrot') and action == 44
    
    def reset(self):    
        pass

class RidePonyEvent(Event):
    def __init__(self, reward = 100, repeatable = False, terminal_required = True, terminal_sufficient = True):
        super().__init__(reward, repeatable, terminal_required, terminal_sufficient)

    def check(self, previous_state, action, state):
        return "You mount the" in state['message'] and action == 210
    
    def reset(self):
        pass