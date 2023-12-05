from minihack import RewardManager
from utils.classes import PickCarrotEvent

# decodifica le stringhe (ad esempio in state['message'])
def decode(X):
    return bytes(X).decode('utf-8').rstrip('\x00')

def define_reward():
    reward_manager = RewardManager()
    reward_manager.add_message_event(["You mount the saddled pony."],
                                        reward=100,
                                        terminal_sufficient=True,
                                        terminal_required=True)
    reward_manager.add_event(PickCarrotEvent)
    return reward_manager