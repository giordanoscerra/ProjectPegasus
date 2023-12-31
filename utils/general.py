from typing import List, Tuple
import numpy as np

# decodifica le stringhe (ad esempio in state['message'])
def decode(X):
    return bytes(X).decode('utf-8').rstrip('\x00')

# the region defined as close is a square with side = maxOffset*2
def are_close(A:(int,int), B:(int,int), maxOffset) -> bool:
    return abs(A[0] - B[0]) <= maxOffset and abs(A[1] - B[1]) <= maxOffset

def are_aligned(A:(int,int), B:(int,int)) -> bool:
    return A[0] == B[0] or A[1] == B[1] or abs(A[0] - B[0]) == abs(A[1] - B[1])

def is_within(A:(int,int), center:(int,int), extRadius, intRadius):
    isInside = are_close(A,B=center,maxOffset=extRadius)
    isOutside = not are_close(A,B=center,maxOffset=intRadius-1)
    return isInside and isOutside

# from first handson session, used by a* to get the list of moves to do
def build_path(parent: dict, target: Tuple[int, int]) -> List[Tuple[int, int]]:
    path = []
    while target is not None:
        path.insert(0,target)
        target = parent[target]
    return path

# from first handson session, used by a* to get the list of valid moves
def get_valid_moves(game_map: np.ndarray, current_position: Tuple[int, int],
                    around_pony:bool) -> List[Tuple[int, int]]:
    x_limit, y_limit = game_map.shape
    valid = []
    x, y = current_position    
    # North
    if y - 1 > 0 and not is_obstacle(game_map[x, y-1], around_pony):
        valid.append((x, y-1)) 
    # East
    if x + 1 < x_limit and not is_obstacle(game_map[x+1, y], around_pony):
        valid.append((x+1, y)) 
    # South
    if y + 1 < y_limit and not is_obstacle(game_map[x, y+1], around_pony):
        valid.append((x, y+1)) 
    # West
    if x - 1 > 0 and not is_obstacle(game_map[x-1, y], around_pony):
        valid.append((x-1, y))
    # North-East
    if y - 1 > 0 and x + 1 < x_limit and not is_obstacle(game_map[x+1, y-1], around_pony):
        valid.append((x+1, y-1))
    # South-East
    if y + 1 < y_limit and x + 1 < x_limit and not is_obstacle(game_map[x+1, y+1], around_pony):
        valid.append((x+1, y+1))
    # South-West
    if y + 1 < y_limit and x - 1 > 0 and not is_obstacle(game_map[x-1, y+1], around_pony):
        valid.append((x-1, y+1))
    # North-West
    if y - 1 > 0 and x - 1 > 0 and not is_obstacle(game_map[x-1, y-1], around_pony):
        valid.append((x-1, y-1))

    return valid

# from first handson session, used by get_valid_moves to check if a position is an obstacle
def is_obstacle(position_element: int, around_pony:bool) -> bool:
    obstacles = "|- "
    return chr(position_element) in around_pony*'u' + obstacles

# From first handson session, used to translate the path returned by a* 
# (which is a list of tuples (coordinates)) into a sequence of actions to perform
#
# OSS: it suffices to get a list of actions. level.perform_action() will take
# care of retrieving the correct id :)
def actions_from_path(start: Tuple[int, int], path: List[Tuple[int, int]]) -> List[str]:
    actions = []
    x_s, y_s = start
    for (x, y) in path:
        move = ''
        if x_s > x:
            move += 'N'
        elif x_s < x:
            move += 'S'
        if y_s > y:
            move += 'W'
        elif y_s < y:
            move += 'E'

        actions.append(move)
        x_s = x
        y_s = y
    
    return actions