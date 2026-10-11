import pandas as pd


file_path = "../data/processed/freight_data.parquet"

print("Reading freight dataset...")

df = pd.read_parquet(file_path)


print("\nShape:")
print(df.shape)


print("\nColumns:")
print(list(df.columns))


print("\nDate range:")
print("From:", df["Date"].min())
print("To:", df["Date"].max())


print("\nFirst 10 records:")
print(df.head(10))


print("\nLast 10 records:")
print(df.tail(10))


print("\nMissing values:")
print(df.isna().sum())


print("\nBasic statistics:")
print(df[["Price", "Open", "High", "Low"]].describe())