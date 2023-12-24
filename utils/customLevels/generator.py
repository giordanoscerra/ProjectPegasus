import gym
from minihack import LevelGenerator
from nle import nethack

from utils.customLevels.rewards import define_reward

def _level_0(pony:bool = True):
    lvl = LevelGenerator(w=20,h=20)
    lvl.add_object(name='carrot', symbol="%", place=None)
    lvl.add_object(name='carrot', symbol="%", place=None)
    if(pony):
            lvl.add_monster(name='pony', symbol="u", place=None)
    lvl.wallify()
    return lvl.get_des()

def _level_1():
    #get content from level1.des
    desDescriton = open('utils/customLevels/level1.des', 'r').read()
    lvl = LevelGenerator(map=desDescriton)
    lvl.add_monster(name='pony', symbol="u", place=None)
    lvl.add_object(name='carrot', symbol="%", place=None)
    lvl.add_object(name='carrot', symbol="%", place=None)
    return lvl.get_des()

def _level_2():
    #get content from level1.des
    desDescriton = open('utils/customLevels/level2.des', 'r').read()
    lvl = LevelGenerator(map=desDescriton)
    lvl.add_monster(name='pony', symbol="u", place=None)
    lvl.add_object(name='carrot', symbol="%", place=None)
    lvl.add_object(name='carrot', symbol="%", place=None)
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
    else:
        lvl = _level_1()

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
            'pixel'),
        des_file = lvl,
        reward_manager = reward_manager_defined,
    )
    print(lvl)
    return env