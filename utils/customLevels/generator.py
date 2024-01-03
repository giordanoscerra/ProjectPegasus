import random
import gym
from minihack import LevelGenerator
from nle import nethack
import os
#import sys
#sys.path.insert(1, os.path.join(sys.path[0], '..'))
from utils.rewards import define_reward


def generate_new_empty_spot(used_places:dict, dimX:int, dimY:int):
    x = random.randint(0,dimX-1)
    y = random.randint(0,dimY-1)
    while((x,y) in used_places):
        x = random.randint(0,dimX-1)
        y = random.randint(0,dimY-1)
    return (x,y)

def _level_0(pony:bool = True, enemies:bool=False):
    lvl = LevelGenerator(w=20,h=15)
    used_places = {}
    for _ in range(15):
        rndPlace = generate_new_empty_spot(used_places, 20, 15)
        lvl.add_object(name='carrot', symbol="%", place=rndPlace)
        used_places[rndPlace] = True
    if(pony):
        rndPlace = generate_new_empty_spot(used_places, 20, 15)
        lvl.add_monster(name='pony', symbol="u", place=rndPlace, args=("hostile", "awake"))
        used_places[rndPlace] = True
    rndPlace = generate_new_empty_spot(used_places, 20, 15)
    lvl.add_object(name='saddle', symbol="(", place=rndPlace)
    if(enemies):
        lvl.add_monster(name='lichen', place=None)
        lvl.add_monster(name='newt', place=None)
        lvl.add_monster(name='jackal', place=None)
    used_places[rndPlace] = True
    rndPlace = generate_new_empty_spot(used_places, 20, 15)
    lvl.set_start_pos(rndPlace)
    lvl.wallify()
    return lvl.get_des()

def _level_1(pony:bool = True, enemies:bool=False):
    #get content from level1.des
    desDescription = open('utils/customLevels/level1.des', 'r').read()
    lvl = LevelGenerator(map=desDescription)
    #pony and carrots randomly placed in the second room
    if(pony):
        lvl.add_monster(name='pony', symbol="u", place=(random.randint(13, 16), random.randint(5, 9)), args=("hostile", "awake"))
    for _ in range(9):
        lvl.add_object(name='carrot', symbol="%", place=(random.randint(8, 16), random.randint(1, 9)))
    #carrot randomly placed near the agent
    if(enemies):
        lvl.add_monster(name='jackal', place=None)
        lvl.add_monster(name='lichen', place=None)
        lvl.add_monster(name='newt', place=None)
    lvl.add_object(name='carrot', symbol="%", place=(random.randint(1, 3), random.randint(4, 6)))
    lvl.add_object(name='saddle', symbol="(", place=None)
    lvl.set_start_pos((2,5))
    return lvl.get_des()

def _level_2(pony:bool = True, enemies:bool=False):
    #get content from level1.des
    desDescription = open('utils/customLevels/level2.des', 'r').read()
    lvl = LevelGenerator(map=desDescription)
    if(pony):
        lvl.add_monster(name='pony', symbol="u", place=(21,4), args=("hostile", "awake"))
    for _ in range(12):
        lvl.add_object(name='carrot', symbol="%", place=None)
    if(enemies):
        lvl.add_monster(name='lichen', place=None)
        lvl.add_monster(name='newt', place=None)
        lvl.add_monster(name='jackal', place=None)
    lvl.add_object(name='saddle', symbol="(", place=None)
    lvl.set_start_pos((2,9))
    return lvl.get_des()

def _level_test_saddle_ride(pony:bool = True):
    lvl = LevelGenerator(w=20,h=20)
    lvl.set_start_pos((2,9))
    if(pony):
        lvl.add_monster(name='pony', symbol="u", place=(2,7), args=("peaceful", "awake"))
    lvl.add_object(name='saddle', symbol="(", place=(2,9))
    lvl.wallify()
    return lvl.get_des()

def _level_3(pony:bool = True, enemies:bool=False):
    desDescriton = open('utils/customLevels/level3.des', 'r').read()
    lvl = LevelGenerator(map=desDescriton)
    if(pony):
        lvl.add_monster(name='pony', symbol="u", place=(31, 14), args=("hostile", "awake"))
    for _ in range(5):
        lvl.add_object(name='carrot', symbol="%", place=None)
    if(enemies):
        lvl.add_monster(name='jackal', place=None)
        lvl.add_monster(name='lichen', place=None)
        lvl.add_monster(name='newt', place=None)
    lvl.add_object(name='saddle', symbol="(", place=None)
    lvl.set_start_pos((2,2))
    return lvl.get_des()

def _level_pony_paradise(pony:bool = True):
    lvl = LevelGenerator(w=17,h=15)
    lvl.set_start_pos((2,9))
    if(pony):
        lvl.add_monster(name='pony', symbol="u", place=(2,7), args=("hostile", "awake"))
    for i in range(17):
        for j in range(15):
            if (i != 2 or j != 10):
                lvl.add_object(name='carrot', symbol="%", place=(i,j))
    lvl.add_object(name='saddle', symbol="(", place=(2,10))
    lvl.wallify()
    return lvl.get_des()

def _level_desolation():
    lvl = LevelGenerator(w=10,h=10)
    lvl.set_start_pos((0,0))
    lvl.add_object(name='saddle', symbol="(", place=(9,7))
    lvl.wallify()
    return lvl.get_des()

def _level_74(pony:bool = True, peaceful:bool = True, enemy:bool = False):
    desDescription = open('utils/customLevels/level74.des', 'r').read()
    lvl = LevelGenerator(desDescription)
    for _ in range(5):
        lvl.add_object(name='carrot', symbol="%", place=None)
    if(pony):
        if(peaceful):
            lvl.add_monster(name='pony', symbol="u", place=(14,11), args=('peaceful',))
        else:
            lvl.add_monster(name='pony', symbol="u", place=(14,11))
    if(enemy):
        lvl.add_monster(name='lichen', place=None)
        lvl.add_monster(name='newt', place=None)
    lvl.add_object(name='saddle', symbol="(", place=None)
    lvl.set_start_pos((random.randint(1,14),random.randint(1,9)))
    lvl.wallify()
    return lvl.get_des() 

def _level_tameness_message(pony:bool=True, 
                            saddle:bool=False, 
                            peaceful_steeds:bool=True):
    lvl = LevelGenerator(w=15, h=15)
    steed_args = ('peaceful',) if peaceful_steeds else None
    if(pony):
        lvl.add_monster(name='pony', symbol='u', place=(3,7), args=steed_args)
    lvl.add_monster(name='horse', symbol='u', place=(11,7), args=steed_args)
    lvl.add_monster(name='warhorse', symbol='u', place=(7,3), args=steed_args)
    if(saddle):
        lvl.add_object(name='saddle', symbol='(', place = None)
    lvl.set_start_pos((7,7))
    lvl.wallify()
    return lvl.get_des()

def _level_test_saddle_ride(pony:bool = True):
    lvl = LevelGenerator(w=20,h=20)
    lvl.set_start_pos((2,9))
    if(pony):
            lvl.add_monster(name='pony', symbol="u", place=(2,7), args=("peaceful", "awake"))
    lvl.add_object(name='saddle', symbol="(", place=(2,9))
    lvl.wallify()
    return lvl.get_des()

# https://rosettacode.org/wiki/Maze_generation
def _make_maze(w:int=24, h:int=10):
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

def _level_random_maze(pony:bool = True):
    lvl = LevelGenerator(_make_maze(w=12, h=10))
    #lvl.set_start_pos((2,9))
    if(pony):
        lvl.add_monster(name='pony', symbol="u", args=("hostile", "awake"))
    for _ in range(20):
        lvl.add_object(name='carrot', symbol="%", place=None)
    lvl.add_object(name='saddle', symbol="(")
    return lvl.get_des()

#def _actions():
#    actions = tuple(nethack.CompassDirection) + (
#        nethack.Command.THROW,
#        nethack.Command.RIDE,
#        nethack.Command.EAT,
#        nethack.Command.DROP,
#        nethack.Command.APPLY,
#        nethack.Command.PICKUP,
#        nethack.Command.WHATIS,
#        nethack.Command.INVENTORY,# included to allow use of saddle (i)
#        nethack.Command.RUSH,# included to allow use of apple (g)
#    )
#    return actions

def createLevel(level:int = 0, pony:bool = True,**kwargs):
    if(level == -1):
        lvl = _level_random_maze(pony)
    elif(level == 0):
        lvl = _level_0(pony, **kwargs)
    elif(level == 1):
        lvl = _level_1(pony, **kwargs)
    elif(level == 2):
        lvl = _level_2(pony, **kwargs)
    elif(level == 3):
        lvl = _level_3(pony, **kwargs)
    elif(level == 74):
        lvl = _level_74(pony,**kwargs)
    elif(level == 4):
        lvl = _level_test_saddle_ride(pony)
    elif(level == 5):
        lvl = _level_pony_paradise(pony)
    elif(level == 6):
        lvl = _level_desolation()
    elif(level == 42):
        lvl = _level_tameness_message(pony,**kwargs)
    else:
        lvl = _level_0(True)
    

    reward_manager_defined = define_reward()
    env = gym.make(
        'MiniHack-Skill-Custom-v0',
        #actions = _actions(),
        character = "kn-hum-neu-mal",
        observation_keys = (
            'glyphs',
            'chars',
            'colors', # Some characters have special colors that represent different things.
            'screen_descriptions',  # descrizioni testuali di ogni cella della mappa 
            'message',
            'inv_strs',
            'inv_letters',
            'blstats',
            'pixel'),
        des_file = lvl,
        reward_manager = reward_manager_defined,
        max_episode_steps = 100000,
    )
    #20 * 20 -> [15:, 480:800]
    #19 * 11 -> [y:, x1:x2]
    #28 * 18 -> [y:, 420:840]
    # 20 -> 480:800 -> 320
    # 19 -> 480:770 -> 290
    # 28 -> 420:840 -> 420
    # circa 16 pixel per cella
    # it would be better to compute the correct dimension
    # but if we don't intend to create more level is enough
    minX = 464
    maxX = 816
    if level==1:
        minX = 480
        maxX = 770
    elif level==2:
        minX = 420
        maxX = 840
    elif level==3:
        minX = 350
        maxX = 890
    return env, (minX,maxX)