# import math


#def euclidean_distance(positions:list(tuple), toCompare: int) -> tuple:
#    return min(positions, key=lambda x: math.sqrt(sum((x[i]-toCompare[i])**2 for i in range(len(x)))))


# I am lazy and I use numpy :D 
# Jokes aside, doing all the involved computations by hand would just be 
# tedious. There are more flashy-pythonic ways of doing it, 
# but in this way is more elegant 
import numpy as np
from typing import List, Tuple


def euclidean_distance(positions:List[Tuple], toCompare:Tuple[int,int]) -> Tuple[int,int]:
    '''Compute the closest point to toCompare among those in the positions list, 
    according to the euclidean distance.
    INPUT: positions, a list of points. toCompare, the origin (a point aka a tuple)
    OUTPUT: a tuple (closest_p, closest_p_dist) where closest_p is the point 
    in positions closest to toCompare, and closest_p_dist is its distance
    '''
    
    argmin = min(positions, key=lambda x: np.linalg.norm([np.array(x)-np.array(toCompare)]))
    min_dist = np.linalg.norm(np.array(argmin) - np.array(toCompare))
    return argmin, min_dist

def manhattan_distance(positions:List[Tuple], toCompare:Tuple[int,int]) -> Tuple[int,int]:
    '''Compute the closest point to toCompare among those in the positions list, 
    according to the Manhattan distance (aka l1-norm-induced distance).
    INPUT: positions, a list of points. toCompare, the origin (a point aka a tuple)
    OUTPUT: a tuple (closest_p, closest_p_dist) where closest_p is the point 
    in positions closest to toCompare, and closest_p_dist is its distance
    '''
    
    argmin = min(positions, key=lambda x: np.linalg.norm([np.array(x)-np.array(toCompare)], ord=1))
    min_dist = np.linalg.norm(np.array(argmin) - np.array(toCompare), ord=1)
    return argmin, min_dist

def infinity_distance(positions:List[Tuple], toCompare:Tuple[int,int]) -> Tuple[int,int]:
    '''Compute the closest point to toCompare among those in the positions list, 
    according to the distance induced by the infinity norm.
    INPUT: positions, a list of points. toCompare, the origin (a point aka a tuple)
    OUTPUT: a tuple (closest_p, closest_p_dist) where closest_p is the point 
    in positions closest to toCompare, and closest_p_dist is its distance
    '''
    
    argmin = min(positions, key=lambda x: np.linalg.norm([np.array(x)-np.array(toCompare)], ord=np.inf))
    min_dist = np.linalg.norm(np.array(argmin) - np.array(toCompare), ord=np.inf)
    return argmin, min_dist