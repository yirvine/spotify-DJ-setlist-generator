import os
import pandas as pd

# Directory containing the CSV files
csv_dir = 'csvs'

# List to hold dataframes
dfs = []

# Iterate over all CSV files in the directory
for filename in os.listdir(csv_dir):
    if filename.endswith('.csv'):
        file_path = os.path.join(csv_dir, filename)
        dfs.append(pd.read_csv(file_path))

# Concatenate all dataframes
combined_df = pd.concat(dfs, ignore_index=True)

# Save the combined dataframe to a new CSV file
combined_df.to_csv('combined.csv', index=False)

print("CSV files have been combined successfully!")
