import pandas as pd


file_path = "../data/processed/commodity_prices.parquet"

print("Reading commodity price dataset...")

df = pd.read_parquet(file_path)


print("\nNumber of records:", len(df))
print("Number of commodities:", df["Commodity"].nunique())


print("\nCommodity list:")
print("-" * 60)

for commodity in sorted(df["Commodity"].unique()):
    print(commodity)


print("\n" + "-" * 60)

print("Date range:")
print("From:", df["Date"].min())
print("To:", df["Date"].max())