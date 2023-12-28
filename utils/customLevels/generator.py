import random
import gym
from minihack import LevelGenerator
from nle import nethack
import os
#import sys
#sys.path.insert(1, os.path.join(sys.path[0], '..'))
from utils.rewards import define_reward

def _level_0(pony:bool = True):
    lvl = LevelGenerator(w=20,h=20)
    for _ in range(10):
        lvl.add_object(name='carrot', symbol="%", place=None)
    if(pony):
            lvl.add_monster(name='pony', symbol="u", place=None)
    lvl.add_object(name='saddle', symbol="(", place=None)
    lvl.wallify()
    return lvl.get_des()

def _level_1(pony:bool = True):
    #get content from level1.des
    desDescriton = open('utils/customLevels/level1.des', 'r').read()
    lvl = LevelGenerator(map=desDescriton)
    #pony and carrots randomly placed in the second room
    if(pony):
        lvl.add_monster(name='pony', symbol="u", place=(random.randint(13, 16), random.randint(5, 9)))
    for _ in range(9):
        lvl.add_object(name='carrot', symbol="%", place=(random.randint(8, 16), random.randint(1, 9)))
    #carrot randomly placed near the agent
    lvl.add_object(name='carrot', symbol="%", place=(random.randint(1, 3), random.randint(4, 6)))
    lvl.add_object(name='saddle', symbol="(", place=None)
    lvl.set_start_pos((2,5))
    return lvl.get_des()

def _level_2(pony:bool = True):
    #get content from level1.des
    desDescriton = open('utils/customLevels/level2.des', 'r').read()
    lvl = LevelGenerator(map=desDescriton)
    if(pony):
        lvl.add_monster(name='pony', symbol="u", place=(21,4))
    for _ in range(12):
        lvl.add_object(name='carrot', symbol="%", place=None)
    lvl.add_object(name='saddle', symbol="(", place=None)
    lvl.set_start_pos((2,9))
    return lvl.get_des()

def _level_test_saddle_ride(pony:bool = True):
    lvl = LevelGenerator(w=20,h=20)
    lvl.set_start_pos((2,9))
    if(pony):
            lvl.add_monster(name='pony', symbol="u", place=(2,5), args=("peaceful", "awake"))
    lvl.add_object(name='saddle', symbol="(", place=(2,9))
    lvl.wallify()
    return lvl.get_des()

def _actions():
    actions = tuple(nethack.CompassDirection) + (
        nethack.Command.THROW,
        nethack.Command.RIDE,
        nethack.Command.EAT,
        nethack.Command.DROP,
        nethack.Command.APPLY,
        nethack.Command.PICKUP,
        nethack.Command.WHATIS,
        nethack.Command.INVENTORY,# included to allow use of saddle (i)
        nethack.Command.RUSH,# included to allow use of apple (g)
    )
    return actions

def createLevel(level:int = 0, pony:bool = True):
    if(level == 0):
        lvl = _level_0(pony)
    elif(level == 1):
        lvl = _level_1(pony)
    elif(level == 2):
        lvl = _level_2(pony)
    elif(level == 3):
        lvl = _level_test_saddle_ride(pony)
    else:
        lvl = _level_0(True)
    

    reward_manager_defined = define_reward()
    env = gym.make(
        'MiniHack-Skill-Custom-v0',
        actions = _actions(),
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
    return env, (minX,maxX)