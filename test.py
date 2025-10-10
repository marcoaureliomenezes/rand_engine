import numpy as np


distinct_1 = ["value1", "value2", "value3"]

distinct_2 = ["col1;value4", "col2;value5", "col3;value6"]

print(np.random.choice(distinct_1, 10))

# Generate sample data
data = np.random.choice(distinct_2, 10)
print("\nOriginal:", data)

# Method 1: np.char.split (fastest for simple cases)
split_list = np.char.split(data, sep=';')
print("\nSplit list:", split_list)

# Method 2: Convert to 2D array (for DataFrame usage)
# This creates separate columns efficiently
split_array = np.array([x.split(';') for x in data])
col1 = split_array[:, 0]
col2 = split_array[:, 1]
print("\nColumn 1:", col1)
print("Column 2:", col2)

# Method 3: Vectorized with np.char (fastest for large arrays)
split_vectorized = np.stack(np.char.split(data, ';'))
print("\nVectorized split shape:", split_vectorized.shape)
print("Column 1 (vec):", split_vectorized[:, 0])
print("Column 2 (vec):", split_vectorized[:, 1])
