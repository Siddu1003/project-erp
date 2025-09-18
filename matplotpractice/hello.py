import matplotlib.pyplot as plt

# Data points
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

# Plotting the graph
plt.plot(x, y)

# Adding title and labels
plt.title("Basic Line Graph")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")

# Show the graph
plt.show()

x = [5, 7, 8, 7, 6, 9, 5, 8, 7, 6]
y = [99, 86, 87, 88, 100, 86, 103, 87, 94, 78]

plt.scatter(x, y, color="red")
plt.title("Scatter Plot Example")
plt.xlabel("X values")
plt.ylabel("Y values")
plt.show()