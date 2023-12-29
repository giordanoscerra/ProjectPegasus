from utils.agent import Agent
from utils.map import Map
from utils.general import decode

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def bruteForceCheckMount(level:Map) -> bool:
    for i in range(len(level.state['screen_descriptions'])):
        for j in range(len(level.state['screen_descriptions'][0])):
            description = decode(level.state['screen_descriptions'][i][j])
            if('Agent, mounted on your pony' in description):
                return True
    return False

def get_direction(start:tuple, end:tuple) -> str:
    distance = (start[0] - end[0], start[1] - end[1])
    nestStep = ''
    if distance[0] > 0:
        nestStep += 'N'
    elif distance[0] < 0:
        nestStep += 'S'
    if distance[1] > 0:
        nestStep += 'W'
    elif distance[1] < 0:
        nestStep += 'E'
    return nestStep

def go_to_pony(carrotFarm:Map):
    #go to pony
    tokugawaPos = carrotFarm.get_agent_position()
    ponyPos = carrotFarm.get_pony_position()
    distance = (tokugawaPos[0] - ponyPos[0], tokugawaPos[1] - ponyPos[1])
    while abs(distance[0]) > 1 or abs(distance[1]) > 1:
        carrotFarm.apply_action(actionName=get_direction(tokugawaPos, ponyPos))
        tokugawaPos = carrotFarm.get_agent_position()
        ponyPos = carrotFarm.get_pony_position()
        distance = (tokugawaPos[0] - ponyPos[0], tokugawaPos[1] - ponyPos[1])

successfulRides = 0
notSaddled = 0
failure = 0
totTries = 1000
for i in range(totTries):
    printProgressBar(i, totTries, prefix = 'Progress:', suffix = 'Complete', length = 50)
    carrotFarm = Map(pony=True, level=5)
    # another knight (he was born in Japan)
    #tokugawa = Agent()

    #throw a carrot to the pony
    carrotFarm.apply_action(actionName='THROW', what='carrot', where='N')

    #pick up the saddle
    carrotFarm.apply_action(actionName='S')
    carrotFarm.apply_action(actionName='PICKUP')

    eatenCarrots = 0
    for _ in range(3):
        carrotFarm.apply_action(actionName='S')
        message=decode(carrotFarm.state['message'])
        if 'pony eats a carrot' in message:
            eatenCarrots += 1

    #wait for the pony to eat 20 carrots
    while eatenCarrots < 13:
        carrotFarm.apply_action(actionName='N')
        carrotFarm.apply_action(actionName='S')
        message=decode(carrotFarm.state['message'])
        if 'pony eats a carrot' in message:
            eatenCarrots += 1

    # go to pony and apply a saddle
    go_to_pony(carrotFarm=carrotFarm)
    tokugawaPos = carrotFarm.get_agent_position()
    ponyPos = carrotFarm.get_pony_position()
    carrotFarm.apply_action(actionName='APPLY', what='saddle', where=get_direction(tokugawaPos, ponyPos))

    #try to ride the pony
    go_to_pony(carrotFarm=carrotFarm)
    tokugawaPos = carrotFarm.get_agent_position()
    ponyPos = carrotFarm.get_pony_position()
    carrotFarm.apply_action(actionName='RIDE', where=get_direction(tokugawaPos, ponyPos))
    message=decode(carrotFarm.state['message'])
    if 'mount the saddled pony' in message:
        successfulRides += 1
    elif 'not saddled' in message:
        notSaddled += 1
    elif 'pony eats a carrot' in message:
        #to know check all position in the map
        if bruteForceCheckMount(carrotFarm):
            successfulRides += 1
        else:
            failure += 1

printProgressBar(totTries, totTries, prefix = 'Progress:', suffix = 'Complete', length = 50)
print()
print(f'Percentage: {successfulRides/totTries*100}%')
print(f'You mounted {successfulRides} out of {totTries} tries')
print(f'You tried to mount a not saddled pony {notSaddled} times')
print(f'You failed {failure} times')