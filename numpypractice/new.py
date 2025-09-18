import numpy as np

# 1D array
a = np.array([1, 2, 3, 4, 5])

# 2D array (matrix)
b = np.array([[1, 2, 3],
              [4, 5, 6]])

print("1D Array:", a)
print("2D Array:\n", b)


# Random integers between 10–50
rand_ints = np.random.randint(10, 50, size=5)

# Random floats between 0–1
rand_floats = np.random.rand(5)

print("Random Integers:", rand_ints)
print("Random Floats:", rand_floats)
