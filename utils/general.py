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

# the region defined as close is a square with side = maxOffset*2
def are_close(A:(int,int), B:(int,int), maxOffset) -> bool:
    return abs(A[0] - B[0]) <= maxOffset and abs(A[1] - B[1]) <= maxOffset

def are_aligned(A:(int,int), B:(int,int)) -> bool:
    return A[0] == B[0] or A[1] == B[1] or abs(A[0] - B[0]) == abs(A[1] - B[1])
