import math


def euclidean_distance(positions:list(tuple), toCompare: int) -> tuple:
    return min(positions, key=lambda x: math.sqrt(sum((x[i]-toCompare[i])**2 for i in range(len(x)))))