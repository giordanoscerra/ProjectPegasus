import pandas as pd
import re

# Specify the path to your text file
file_path = 'stats/L3YANE.txt'

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

# Save the DataFrame to a CSV file
csv_file_path = 'stats/L3YANE.csv'
df.to_csv(csv_file_path, index=False)
