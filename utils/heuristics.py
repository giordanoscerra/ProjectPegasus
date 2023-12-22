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
    return min(positions, key=lambda x: np.linalg.norm([np.array(x)-np.array(toCompare)]))
