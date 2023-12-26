from minihack import RewardManager
from minihack.reward_manager import Event
from nle import nethack
from ..general import decode
import re

# These are the events needed by the reward manager to reward the agent for the actions we want them to do.
# To create one, it is needed to inherit from the Event class, implement the check method and eventually the reset method.
# The check method is called at each step of the game and it is used to check if the event has happened.
# GitHub copilot thinks: The reset method is called at the end of each episode and it is used to reset the event's internal state. I personally do not know - Yuri
# previous_state and state are tuples: they are subdivided by the observation keys we defined in the map.py, apparently.

# The PickCarrotEvent is used to reward the agent for picking up a carrot.
# when we have a single carrot in the inventory it is shown as "an uncursed carrot"
class GetCarrotsEvent(Event):
    def __init__(self, reward = 1, repeatable = True, terminal_required = False, terminal_sufficient = False):
        super().__init__(reward, repeatable, terminal_sufficient, terminal_required)
    
    def check(self, env, previous_observation, action, observation):
        carrots = 0
        prev_carrots = 0
        for letter, stringa in \
            zip(decode(previous_observation[env._original_observation_keys.index('inv_letters')]), previous_observation[env._original_observation_keys.index('inv_strs')]):
            if "carrot" in decode(stringa): 
                try:
                    prev_carrots = [int(s) for s in  re.findall(r'\d+',decode(stringa))][0]
                except:
                    #should fix the case in which the number of carrots is incremented but
                    #because for example we picked 2 and we had one in the inventory
                    #because the reward would be 2-1 = 1 instead of 2
                    prev_carrots = 1
        carrots = 0
        for letter, stringa in zip(decode(observation[env._original_observation_keys.index('inv_letters')]), observation[env._original_observation_keys.index('inv_strs')]):
            if "carrot" in decode(stringa):
                try: 
                    carrots = [int(s) for s in  re.findall(r'\d+',decode(stringa))][0]
                except:
                    carrots = 1
        return (prev_carrots < carrots and action == env.actions.index(nethack.Command.PICKUP))*(carrots-prev_carrots)
    
    def reset(self):    
        pass

class MountEvent(Event):
    def __init__(self, reward = 100, repeatable = False, terminal_required = True, terminal_sufficient = True):
        super().__init__(reward, repeatable, terminal_required, terminal_sufficient)

    def check(self, env, previous_observation, action, observation):
        del previous_observation
        curr_msg = (
            observation[env._original_observation_keys.index("message")]
            .tobytes()
            .decode("utf-8")
        )
        return self.reward if "You mount the" in curr_msg else 0
    
    def reset(self):
        pass

# This defines the reward manager, passed to the environment as a variable during initialization
def define_reward():
    reward_manager = RewardManager()
    reward_manager.add_event(MountEvent())
    reward_manager.add_event(GetCarrotsEvent())
    return reward_manager