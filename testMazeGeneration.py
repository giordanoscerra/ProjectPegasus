import random

def generate_ascii_map(width, height, wall_char='|', floor_char='.', outer_wall=True):

    map_str = ""

    for y in range(height):
        for x in range(width):
            if outer_wall and (x == 0 or x == width - 1 or y == 0 or y == height - 1):
                map_str += wall_char
            elif random.random() < 0.3:  # 30% chance to place a wall, can be adjusted
                map_str += wall_char
            else:
                map_str += floor_char
        map_str += "\n"

    return map_str


# https://rosettacode.org/wiki/Maze_generation
def make_maze(w=32, h=17):
    vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]
    ver = [["|.."] * w + ['|'] for _ in range(h)] + [[]]
    hor = [["|||"] * w + ['|'] for _ in range(h + 1)]

    def walk(x, y):
        vis[y][x] = 1

        d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
        random.shuffle(d)
        for (xx, yy) in d:
            if vis[yy][xx]: continue
            if xx == x: hor[max(y, yy)][x] = "|.."
            if yy == y: ver[y][max(x, xx)] = "..."
            walk(xx, yy)

    walk(random.randrange(w), random.randrange(h))

    s = ""
    for (a, b) in zip(hor, ver):
        s += ''.join(a + ['\n'] + b + ['\n'])
    return s


# Generate a maze with default dimensions
print(make_maze())

# Example usage
random_map = generate_ascii_map(32, 32)
#print(random_map)