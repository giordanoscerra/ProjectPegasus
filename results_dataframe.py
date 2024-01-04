import pandas as pd
import re
import os

# Specify the path to your text file
file_list = ['stats/L2YANE', 'stats/L2NANE', 'stats/L3YANE', 'stats/L3NANE']

result_df = pd.DataFrame()

for file in file_list:
    # Specify the path to your text file
    file_path = file+'.txt'

    # Read the data from the text file
    with open(file_path, 'r') as file:
        content = file.read()

    # Extracting data using regular expressions
    pattern = re.compile(r'rewards:<([\d.]+)> steps:<(\d+)>')
    matches = pattern.findall(content)

    # Creating a DataFrame
    df = pd.DataFrame(matches, columns=['Rewards', 'Steps'])

    # Converting data types
    df['Rewards'] = df['Rewards'].astype(float)
    df['Steps'] = df['Steps'].astype(int)

    # Display the DataFrame
    print(df)
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