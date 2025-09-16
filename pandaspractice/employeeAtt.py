#!/usr/bin/env python
# coding: utf-8

# In[40]:


import pandas as pd

emp = pd.read_excel("employee_data.xlsx")
display(emp.head())
display(emp.tail())


# In[41]:


print("Missing Values in Xl File:", emp.isnull().sum())


# In[42]:


emp["TasksCompleted"] = emp["TasksCompleted"].fillna(0)
emp["HoursWorked"] = emp["HoursWorked"].fillna(0)
emp["Status"] = emp["Status"].fillna("Absent")


# In[43]:


print("After handling the missing values:\n",emp.isnull().sum())


# In[44]:


emp["Date"] = pd.to_datetime(emp["Date"])
print(emp["Date"].head())
print("\n",emp["Date"].tail())


# In[22]:


attendance_summary = emp.groupby(["EmployeeID", "Name"])["Date"].nunique().reset_index()
attendance_summary.rename(columns={"Date": "TotalWorkingDays"}, inplace=True)

status_summary = emp.groupby(["EmployeeID", "Name", "Status"])["Date"].count().unstack(fill_value=0).reset_index()

attendance_report = pd.merge(attendance_summary, status_summary, on=["EmployeeID", "Name"])

display(attendance_report.head())


# In[29]:


dept_hours = emp.groupby("Department")["HoursWorked"].mean().reset_index()

top_employees = emp.groupby(["EmployeeID", "Name"])["TasksCompleted"].sum().reset_index()
top_employees = top_employees.sort_values(by="TasksCompleted", ascending=False).head(5)

dept_tasks = emp.groupby("Department")["TasksCompleted"].mean().reset_index()

display("Finding the average hours worked per department:",dept_hours)
display("Identify the top 5 employees with the highest total tasks completed:",top_employees)
display("For each department the average tasks completed per day:",dept_tasks)


# In[31]:


emp["Month"] = emp["Date"].dt.to_period("M")


monthly_tasks = emp.groupby("Month")["TasksCompleted"].sum().reset_index()
monthly_hours = emp.groupby("Month")["HoursWorked"].mean().reset_index()


monthly_summary = pd.merge(monthly_tasks, monthly_hours, on="Month")
monthly_summary.rename(columns={
    "TasksCompleted": "TotalTasksCompleted",
    "HoursWorked": "AvgHoursWorked"
}, inplace=True)

display(monthly_summary)


# In[39]:


with pd.ExcelWriter("employee_report.xlsx", engine="openpyxl") as writer:
    emp.to_excel(writer, sheet_name="Manipulated Data", index=False)
    attendance_report.to_excel(writer, sheet_name="Attendance Summary", index=False)
    dept_hours.to_excel(writer, sheet_name="Avg Dept Hours", index=False)
    top_employees.to_excel(writer, sheet_name="Top 5 Employees", index=False)
    dept_tasks.to_excel(writer, sheet_name="Avg Dept Tasks", index=False)
    monthly_summary.to_excel(writer, sheet_name="Monthly Summary", index=False)

