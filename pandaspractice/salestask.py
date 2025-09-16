#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_excel("sales_data.xlsx")

print("First 5 rows of data:")
display(df.head())


# In[2]:


df["TotalSales"] = df["Units"] * df["UnitPrice"]
print("After Adding Total Sales:")
display(df.head())


# In[3]:


sales = df.groupby("Region")["TotalSales"].sum()
print("Total Sales by Region:\n",sales)


# In[4]:


sales.plot(kind="bar", color="skyblue", figsize=(15,5))
plt.title("Total Sales by Region")
plt.ylabel("Total Sales")
plt.show()


# In[5]:


top_salespersons = df.groupby(["SalesPerson", "Region"])["TotalSales"].sum().sort_values(ascending=False)

display(top_salespersons)
print("\nTop 3 Salespersons:")
print(top_salespersons.head(3))



# In[6]:


top_salespersons.plot(kind="bar", color="orange", figsize=(15,7))
plt.title("Top Salespersons by Sales ")
plt.xlabel("Salespersons By Region")
plt.ylabel("Total sales")
plt.show()


# In[8]:


extract_highsales = df[df["TotalSales"] > 5000]
print("\nTransactions with TotalSales > 5000:")
display(extract_highsales)


# In[9]:


each_product = df.groupby("Product").agg(
    TotalUnits=("Units", "sum"),
    AvgPrice=("UnitPrice", "mean")
)
print("\nProduct Analysis:")
display(each_product)


# In[10]:


sort_data = df.sort_values(by="TotalSales", ascending=False)
print("\nSorted Transactions:")
display(sort_data.head())


# In[11]:


sort_data.to_excel("sales_report.xlsx", index=False)

