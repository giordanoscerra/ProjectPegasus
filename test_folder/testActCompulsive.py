import sys
import os
import subprocess
import numpy as np
sys.path.append(os.path.join(sys.path[0], '..'))
from utils.heuristics import manhattan_distance, infinity_distance, euclidean_distance
from utils.map import Map
from utils.agent import Agent
from utils import exceptions

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


if __name__ == "__main__":
    script_name = 'test_folder/testAct.py'  # The script to be run multiple times
    number_of_times = 20              # How many times you want to run the script
    exit_codes = []

    for i in range(number_of_times):
        printProgressBar(i, number_of_times, prefix = 'Progress:', suffix = 'Complete', length = 50)
        exit_codes.append(subprocess.run(['python', script_name]).returncode)

    printProgressBar(number_of_times, number_of_times, prefix = 'Progress:', suffix = 'Complete', length = 50)

    print('The agent averaged', np.mean(exit_codes), 'actions to perform the task over',number_of_times,'iterations')

"""
import subprocess
import multiprocessing

def run_script(script_name):
    return subprocess.run(['python', script_name], capture_output=True).returncode

def main():
    script_name = 'test_folder/testAct.py'  # The script to be run multiple times
    number_of_times = 20                    # How many times you want to run the script

    # Create a pool of workers and run the script in parallel
    with multiprocessing.Pool() as pool:
        exit_codes = pool.map(run_script, [script_name] * number_of_times)

    print("Exit codes:", exit_codes)

if __name__ == "__main__":
    main()
"""
