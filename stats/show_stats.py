import pandas as pd
import re
import os
import matplotlib.pyplot as plt

# Specify the path to your text file
#file_list = ['stats/L2YANE', 'stats/L2NANE', 'stats/L3YANE', 'stats/L3NANE']
# Specify the path to your folder

def show_stats(level:int=-1, success_rate_flag:bool=False):

    # -1 for random maze
    # 0 for square
    # 1 for impossible one
    # 2 for nethack-like level
    # 3 for complex maze

    folder_path = 'stats/assessments'

    # Get a list of all files in the folder
    file_list = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]

    result_df = pd.DataFrame()

    desired_sequence= 'L'+str(level)

    for file_path in [s for s in file_list if desired_sequence in s and "Infinity" not in s]:
        # Specify the path to your text file
        pattern = r"\d+:\srewards:<([-\d.]+)>\ssteps:<([-\d.]+)>"
        rewards_list = []
        steps_list = []

        with open(file_path, 'r') as file:
            for line in file:
                # Stripping newline characters from each line
                line = line.strip()
                # Apply regex pattern to each line
                match = re.match(pattern, line)
                if match:
                    # Extracting the captured integers
                    rewards,steps = match.groups()
                    rewards_list.append(float(rewards))
                    steps_list.append(int(steps))
                else:
                    print(f"Invalid format: {line}")
            
        df = pd.DataFrame()

        # Converting data types
        df['Rewards'] = pd.Series(rewards_list)
        df['Steps'] = pd.Series(steps_list)
        # Count the number of rows where "Rewards" < 1000
        failures = (df[df['Rewards'] < 1000])['Steps'].mean()
        #print(failures)
        success = (df[df['Rewards'] >= 1000])['Steps'].mean()
        success_amount = len(df[df['Rewards'] >= 1000])
        tot = len(df)
        success_rate = success_amount/tot
        # Extract the file name without extension
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        med_df = pd.DataFrame([failures, success, success_rate])
        result_df[file_name] = med_df 


    result_df.index = ['Steps On Failure', 'Steps On Success', 'Success Rate']
    #result_df = result_df.fillna("0")
    result_df = result_df.round(3)
    # Save the final DataFrame to an Excel file
    excel_file_path = 'stats/results.xlsx'
    result_df = result_df.T

    if(success_rate_flag):
        # Create histograms for each column
        ax = result_df['Success Rate'].plot(kind='bar')
        # Set the y-axis limit to 1
        ax.set_ylim(0, 1)

        # Customize the plot (optional)
        plt.title('Success Rate')
        plt.xlabel('Level CODENAME')
        plt.ylabel('Success Rate')

        # Show the plot
        plt.show()
        plt.close()

    result_df = result_df.drop('Success Rate', axis=1)

    # Convert columns to numeric (remove non-numeric values like '0')
    result_df = result_df.apply(pd.to_numeric, errors='coerce')

    # Create histograms for each column
    result_df.plot(kind='bar')

    # Customize the plot (optional)
    plt.title('Steps On Failure and Steps On Success')
    plt.xlabel('Level CODENAME')
    plt.ylabel('Steps')
    plt.legend(['Steps On Failure', 'Steps On Success'])

    # Show the plot
    plt.show()
    plt.close()