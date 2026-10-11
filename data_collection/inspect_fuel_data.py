import pandas as pd


file_path = "../data/processed/fuel_prices.parquet"

print("Reading fuel price dataset...")

df = pd.read_parquet(file_path)


print("\nShape:")
print(df.shape)


print("\nColumns:")
print(list(df.columns))


print("\nDate range:")
print("From:", df["Date"].min())
print("To:", df["Date"].max())


print("\nCrude oil series:")
print(df["Commodity"].unique())


print("\nRecords per crude oil series:")
print(df["Commodity"].value_counts())


print("\nMissing values:")
print(df.isna().sum())


print("\nFirst 10 records:")
print(df.head(10))