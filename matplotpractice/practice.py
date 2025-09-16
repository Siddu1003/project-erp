#!/usr/bin/env python
# coding: utf-8

# In[35]:


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


# In[36]:


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


# In[37]:


import pandas as pd

# Read CSV file
ama = pd.read_csv("amazon_products.csv")

print("Product data:\n",ama)


# In[38]:


print(ama.head())
print("\n",ama.head(4))


# In[39]:


print(ama.tail())
print("\n",ama.tail(3))


# In[40]:


print(ama.isnull().sum())


# In[34]:


print(ama.info())


# In[42]:


print(ama.columns)


# In[43]:


print(ama.shape)


# In[ ]:


#we can remove null values by using ".dropna()".
#to remove rows where a specific column has nulls ".dropna(subset=["colum_name"])"
#remove columns with null values "dropna(axis=1)" drops entire column if they contain null values.


# In[3]:


import numpy as np

# Create numpy arrays
arr1 = np.array([1, 2, 3, 4, 5])
arr2 = np.array([10, 20, 30, 40, 50])

print("Addition:", arr1 + arr2)
print("Subtraction:", arr2 - arr1)
print("Multiplication:", arr1 * arr2)
print("Division:", arr2 / arr1)


print("Mean of arr1:", np.mean(arr1))
print("Max of arr2:", np.max(arr2))
print("Square root of arr1:", np.sqrt(arr1))
print("Reshape arr2 (1 row, 5 cols):", arr2.reshape(1, 5))


# In[29]:


import numpy as np
#import matplotlib.pyplot as plt
from matplotlib.image import imread

# Read image as NumPy array
img = imread("screenshot.png")
print("image:",img.shape)


# In[52]:


import numpy as np

x = np.array([75, 82, 90, 65, 88])

avg = np.mean(x)
max = np.max(x)
print("Average:", avg)
print("Max:",max)


# In[81]:


import pandas as pd

emp = pd.read_csv("employees.csv")

print("First 5 employees:\n", emp.head())

print("\nEmployee Age and Gender:\n", emp[["Name", "Age", "Gender"]])

print("\nGender Count:\n", emp["Gender"].value_counts())

max_age=emp["Age"].max()
print("\nmax Age is:",max_age)


# In[ ]:


emp_id = input("Enter EmployeeID to get details:")
employee = emp[emp["EmployeeID"] == emp_id]

print(employee)


# In[ ]:


import pandas as pd

marks = pd.read_csv("marks.csv")

print("First 5 rows:\n", marks.head())

print("\nAverage Marks:\n", marks[["Math","Science","English","History","Computer"]].mean())


# In[ ]:


stu_id = input("Enter StudendID to get details:")
student = marks[marks["StudentID"] == stu_id]

print(student)


# In[ ]:


grade = input("Enter Grade to find students: ")
find_grade = marks[marks["Grade"] == grade]
print(f"\n Students with Grade {grade}:\n",find_grade)


# In[ ]:


per = float(input("Enter a Value to find Percentage : "))

find_per = marks[marks["Percentage"] >= per]

print(f"Students with Percentage {per}% and above:\n", find_per)


# In[1]:


import pandas as pd

amazon = pd.read_csv("amazon_products.csv")
print(amazon)


# In[3]:


print(amazon.isnull().sum())


# In[4]:


null = amazon.dropna()
print("After removing null values:\n",null)


# In[ ]:


new_data = {"ProductID": "P101", "ProductName": "Laptop", "Brand": "asus","Category":"Electronics","Price":25000,"Rating":3.5,"Stock":335,"Discount(%)":8.0,}
amazon = pd.concat([amazon, pd.DataFrame([new_data])], ignore_index=True)
print(amazon)


# In[ ]:


#Task-sir will share in the gsroup

