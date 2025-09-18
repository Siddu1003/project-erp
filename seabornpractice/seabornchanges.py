import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Generate random data
np.random.seed(42)
data = pd.DataFrame({
    "Maths": np.random.randint(30, 100, 50),
    "Science": np.random.randint(25, 95, 50),
    "Gender": np.random.choice(["Male", "Female"], 50)
})

# Plot scatterplot
plt.figure(figsize=(7,5))
sns.scatterplot(x="Maths", y="Science", hue="Gender", data=data, palette="Set2", s=80)
plt.title("Random Student Marks: Maths vs Science")
plt.show()
