#!/usr/bin/env python
# coding: utf-8

# In[2]:


import matplotlib.pyplot as plt
import numpy as np
x = np.arange(1, 6)
y = np.array([5, 7, 3, 8, 6])
y2 = np.array([2, 6, 4, 7, 5])


# In[30]:


plt.figure(figsize=(10,4))
plt.plot(x, y, marker="o", label="Line 1")
plt.plot(x, y2, marker="s", label="Line 2")
plt.title("Line Plot")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.legend()
plt.show()


# In[31]:


plt.figure(figsize=(8,5))
plt.bar(x, y, color="skyblue")
plt.title("Bar Chart")
plt.xlabel("X-axis")
plt.ylabel("Values")
plt.show()


# In[27]:


plt.figure(figsize=(7,3))
plt.barh(x, y, color="orange")
plt.title("Horizontal Bar Chart")
plt.xlabel("Values")
plt.ylabel("X-axis")
plt.show()


# In[25]:


plt.figure(figsize=(5,5))
plt.pie(y, labels=["A", "B", "C", "D", "E"], autopct="%1.1f%%", startangle=90)
plt.title("Pie Chart")
plt.show()


# In[18]:


data = np.random.randn(1000)
plt.figure(figsize=(12,6))
plt.hist(data, bins=20, color="purple", alpha=0.7)
plt.title("Histogram")
plt.show()


# In[8]:


plt.figure(figsize=(6,4))
plt.scatter(x, y, color="red", label="Points")
plt.title("Scatter Plot")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.legend()
plt.show()


# In[17]:


plt.figure(figsize=(15,5))
plt.stackplot(x, y, y2, labels=["y", "y2"], colors=["blue", "lightgreen"])
plt.title("Stacked Area Plot")
plt.legend()
plt.show()


# In[15]:


plt.figure(figsize=(10,4))
plt.boxplot([y, y2], tick_labels=["y", "y2"])
plt.title("Box Plot")
plt.show()


# In[12]:


plt.figure(figsize=(9,5))
plt.plot(x, y, label="y")
plt.fill_between(x, y, y2, color="lightblue", alpha=0.5)
plt.title("Fill Between Plot")
plt.legend()
plt.show()

