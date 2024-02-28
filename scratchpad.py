import pandas as pd

df = pd.read_csv("all_metadata.csv")
df = df.drop_duplicates()
df.to_csv("all_metadata.csv", index = False)