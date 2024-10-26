#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python39Packages.pandas python39Packages.matplotlib python39Packages.numpy

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Constants
lever_arm = 0.231775  # in meters

# Load data from CSV
file_path = 'torque_measurements.csv'  # Update this to the path of your CSV file
df = pd.read_csv(file_path)

# Calculate Force (N) and Torque (Nm)
df['Force (N)'] = df['Mass(g)'] * 9.81 / 1000  # Converting g to kg and multiplying by gravity
df['Torque (Nm)'] = df['Force (N)'] * lever_arm

# Use numpy to calculate the slope and intercept of the best-fit line
x = df['Torque (Nm)'].values
y = df['Num'].values

# Calculate the slope (m) and intercept (b) manually
m = np.sum((x - x.mean()) * (y - y.mean())) / np.sum((x - x.mean()) ** 2)
b = y.mean() - m * x.mean()

print(f"Function to convert Torque to Num: Num = {m:.4f} * Torque + {b:.4f}")

# Plot original data and fitted line
plt.figure(figsize=(10, 6))
plt.scatter(x, y, color='blue', label='Original Data')
plt.plot(x, m * x + b, color='red', label='Fitted Line')

plt.xlabel('Torque (Nm)')
plt.ylabel('Num')
plt.legend()
plt.title('Torque to Num Conversion')

plt.show()

