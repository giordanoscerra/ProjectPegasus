import pandas as pd
import re
import os

# Specify the path to your text file
file_list = ['stats/L3YANE', 'stats/L2NANE', 'stats/L3YANE', 'stats/L3NANE']

result_df = pd.DataFrame()

for file in file_list:
    # Specify the path to your text file
    file_path = file+'.txt'
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
    print(df)
    # Count the number of rows where "Rewards" < 1000
    failures = (df[df['Rewards'] < 1000])['Steps'].mean()
    print(failures)
    success = (df[df['Rewards'] >= 1000])['Steps'].mean()
    print(success)
    exit()
    # Extract the file name without extension
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    # Compute the average of each column
    column_averages = df.mean()
    result_df[file_name] = column_averages


result_df.index = ['Rewards', 'Steps']
result_df = result_df.round(2)
# Save the final DataFrame to an Excel file
excel_file_path = 'stats/results.xlsx'
result_df.to_excel(excel_file_path, index=True)