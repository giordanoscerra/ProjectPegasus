import pandas as pd
import re
import os
import matplotlib.pyplot as plt

# Specify the path to your text file
#file_list = ['stats/L2YANE', 'stats/L2NANE', 'stats/L3YANE', 'stats/L3NANE']
# Specify the path to your folder
folder_path = 'stats/assessments'

# Get a list of all files in the folder
file_list = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]

result_df = pd.DataFrame()

for file_path in file_list:
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
result_df = result_df.round(2)
# Save the final DataFrame to an Excel file
excel_file_path = 'stats/results.xlsx'
result_df = result_df.T
# Sort the DataFrame based on the inverse alphabetic order of the index
df_sorted = result_df.sort_index(ascending=False)
df_sorted.to_excel(excel_file_path, index=True)


'''
PLOTTING IS MOMENTANEALLY IN STAND BY

# Convert columns to numeric (remove non-numeric values like '0')
result_df = result_df.apply(pd.to_numeric, errors='coerce')

# Create histograms for each column
result_df.plot(kind='hist', bins=10, edgecolor='black', alpha=0.7)

# Customize the plot (optional)
plt.title('Histograms of Steps On Failure and Steps On Success')
plt.xlabel('Values')
plt.ylabel('Frequency')
plt.legend(['Steps On Failure', 'Steps On Success'])

# Show the plot
plt.show()
'''