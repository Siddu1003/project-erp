import pandas as pd

emp = pd.read_csv("employees.csv")

print("First 5 employees:\n", emp.head())

print("\nEmployee Age and Gender:\n", emp[["Name", "Age", "Gender"]])


print("\nGender Count:\n", emp["Gender"].value_counts())
