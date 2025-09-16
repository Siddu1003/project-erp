#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

student = pd.read_excel("student_marks.xlsx")

student.head()


# In[2]:


print(student.columns)


# In[3]:


marks_columns = ["Maths", "Science", "English", "History", "Computer"]
marks_array = student[marks_columns].to_numpy()

marks_array[:5] 


# In[ ]:


avg_per_student = np.mean(marks_array, axis=1)


highest_per_subject = np.max(marks_array, axis=0)
highest = dict(zip(marks_columns, highest_per_subject.tolist()))
print("Highest Marks per Subject:", highest)

lowest_per_subject = np.min(marks_array, axis=0)
lowest = dict(zip(marks_columns, lowest_per_subject.tolist()))
print("Lowest Marks per Subject:", lowest)

class_avg_per_subject = np.mean(marks_array, axis=0)
class_avg =  dict(zip(marks_columns, np.round(class_avg_per_subject,2).tolist()))
print("Class Average per Subject:", class_avg)


plt.bar(marks_columns, class_avg_per_subject)
plt.title("Class Average per Subject")
plt.ylabel("Average Marks")
plt.xlabel("Subjects")
plt.show()


# In[6]:


totalmarks_per_student = np.sum(marks_array, axis=1)


ranks = totalmarks_per_student.argsort()[::-1] 


rank_array = np.empty_like(ranks)
rank_array[ranks] = np.arange(1, len(ranks)+1)



top3_indices = ranks[:3]
bottom3_indices = ranks[-3:]

print("Top 3 Students:")
print(student.loc[top3_indices, ["StudentID", "Name"]].assign(Total=totalmarks_per_student[top3_indices]))

print("\nBottom 3 Students:")
print(student.loc[bottom3_indices, ["StudentID", "Name"]].assign(Total=totalmarks_per_student[bottom3_indices]))


# In[8]:


pass_fail = np.where((marks_array >= 40).all(axis=1), "Pass", "Fail")


total_passed = np.sum(pass_fail == "Pass")

print("\nTotal Students Passed All Subjects:", total_passed)


# In[9]:


student["Result"] = pass_fail


passed_students = student[student["Result"] == "Pass"]


failed_students = student[student["Result"] == "Fail"]

print("\n Passed Students:")
print(passed_students)

print("\n Failed Students:")
print(failed_students)


# In[19]:


pass_fail_counts = student["Result"].value_counts()

plt.pie(pass_fail_counts, labels=pass_fail_counts.index, autopct="%1.1f%%", startangle=90)
plt.title("Pass vs Fail ")
plt.show()


# In[22]:


student["TotalMarks"] = totalmarks_per_student
student["AverageMarks"] = np.round(avg_per_student, 2)
student["Result"] = pass_fail
student["Rank"] = rank_array


# In[38]:


plt.figure(figsize=(15, 5)) 
plt.plot(student["Name"], student["TotalMarks"], marker="o",)
plt.title("Total Marks of Students")
plt.xticks(rotation=45)
plt.ylabel("Total Marks")
plt.show()


# In[49]:


with pd.ExcelWriter("student_report.xlsx", engine="openpyxl") as writer:
    student.to_excel(writer, sheet_name="All Students", index=False)
    passed_students.to_excel(writer, sheet_name="Passed Students", index=False)
    failed_students.to_excel(writer, sheet_name="Failed Students", index=False)

print("✅ Data successfully written to student_report.xlsx")


# In[ ]:



