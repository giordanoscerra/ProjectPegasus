import numpy as np
from queue import PriorityQueue
from typing import Tuple, List
from .general import are_close, build_path, get_valid_moves, is_within
from .heuristics import manhattan_distance, euclidean_distance

def a_star(game_map: np.ndarray, start: Tuple[int, int], target: Tuple[int, int],
            heuristic:callable = lambda t,s: manhattan_distance([t],s)[1],
            maxDistance:int=0, minDistance:int=0) -> List[Tuple[int, int]]:
    # initialize open and close list
    open_list = PriorityQueue()
    close_list = []
    # additional dict which maintains the nodes in the open list for an easier access and check
    support_list = {}

    # points that are within minDistance from target are as "expensive" as 
    # those that are at maxDistance. This is to make sure that the agent 
    # moves away from them, if it starts closer than minDistance 
    def h(p,target): 
        if are_close(p,target,minDistance):
            return maxDistance 
        else:
            return heuristic(p,target)
        #return heuristic(p,target)

    starting_state_g = 0
    starting_state_h = h(start,target)
    starting_state_f = starting_state_g + starting_state_h

    open_list.put((starting_state_f, (start, starting_state_g)))
    support_list[start] = starting_state_g
    parent = {start: None}

    while not open_list.empty():
        # get the node with lowest f
        (_, (current, current_g)) = open_list.get()
        # add the node to the close list
        close_list.append(current)

        if is_within(current,target,extRadius=maxDistance,intRadius=minDistance):
        #if current == target:
            #print("Target found!")
            path = build_path(parent, current)
            return path

        for neighbor in get_valid_moves(game_map, current):
            # check if neighbor in close list, if so continue
            if neighbor in close_list: 
                continue

            # compute neighbor g, h and f values
            neighbor_g = current_g + 1
            neighbor_h = h(neighbor,target)
            neighbor_f = neighbor_g + neighbor_h
            neighbor_entry = (neighbor_f, (neighbor, neighbor_g))
            # if neighbor in open_list
            if neighbor in support_list.keys():
                # if neighbor_g is greater or equal to the one in the open list, continue
                if neighbor_g >= support_list[neighbor]: 
                    continue

            # add neighbor to open list and update support_list
            parent[neighbor] = current
            open_list.put(neighbor_entry)
            support_list[neighbor] = neighbor_g

    #TODO: raise an exception if the target is not found? 
    #print("Target node not found!")
    return None