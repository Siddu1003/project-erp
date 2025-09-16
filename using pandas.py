import pandas as pd
import matplotlib.pyplot as plt

# Read CSV file
df = pd.read_csv("data.csv")

# Print the data
print("Marks Data:\n", df)

# Plot bar chart
plt.bar(df["Name"], df["Marks"], color="skyblue")

# Add labels and title
plt.title("Students Marks")
plt.xlabel("Name")
plt.ylabel("Marks")

# Show the chart
plt.show()
