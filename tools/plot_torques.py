#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python39Packages.pandas python39Packages.matplotlib

import matplotlib.pyplot as plt
import pandas as pd

# Constants
lever_arm = 0.231775  # in meters

# Load data from CSV
file_path = 'torque_measurements.csv'  # Update this to the path of your CSV file
df = pd.read_csv(file_path)

# Calculate Force (N) and Torque (Nm)
df['Force (N)'] = df['Mass(g)'] * 9.81 / 1000  # Converting g to kg and multiplying by gravity
df['Torque (Nm)'] = df['Force (N)'] * lever_arm

# Calculate Torque Constant (Nm/A)
df['Torque Constant (Nm/A)'] = df['Torque (Nm)'] / df['Current(A)']

# Display Torque Constant values
print("Torque Constant (Nm/A) for each data point:")
print(df[['Num', 'Torque Constant (Nm/A)']])

# Plotting on a single graph
plt.figure(figsize=(10, 6))

# Plot Current, Force, and Torque on the same plot
plt.plot(df['Num'], df['Current(A)'], label='Current (A)', color='blue')
plt.plot(df['Num'], df['Force (N)'], label='Force (N)', color='orange')
plt.plot(df['Num'], df['Torque (Nm)'], label='Torque (Nm)', color='green')

# Labels and title
plt.xlabel('Num')
plt.ylabel('Values')
plt.legend()
plt.title('Current, Force, and Torque vs Num')

plt.tight_layout()
plt.show()

