import numpy as np

# Array original de tamanho x
array_x = np.array([1, 2, 3, 4, 5])

# Novo tamanho do array
y = 10

# Cria os índices para o array original
indices_originais = np.arange(len(array_x))

# Cria índices para o novo array
indices_novos = np.linspace(0, len(array_x) - 1, y)

# Interpola os valores
array_y = np.interp(indices_novos, indices_originais, array_x)

print("Array original:", array_x)
print("Array alongado:", array_y)