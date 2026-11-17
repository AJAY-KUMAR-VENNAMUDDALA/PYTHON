import pandas as pd
import numpy as np

print("Sample Data:")

df = pd.read_excel("C:/Users/ajayk/OneDrive/Desktop/AK/Python/Pandas/sample_-_superstore.xls")
print(df.shape)

print(df.head())


print(df.shape)
print(df)

print(df.columns)
print(df.tail())
print(pd.DataFrame(np.random.randint(0,10,(3,3)),columns=['A','B','C'], index=['Row1','Row2','Row3']))