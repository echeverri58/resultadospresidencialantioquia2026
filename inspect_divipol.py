import pandas as pd
df = pd.read_excel('Divipole Antioquia.xlsx')
print("Columns:")
print(df.columns.tolist())
print("\nFirst 3 rows:")
print(df.head(3).to_dict(orient='records'))
