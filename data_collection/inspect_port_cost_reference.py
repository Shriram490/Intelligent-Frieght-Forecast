import polars as pl

path = r"C:\intelligentfrieghtforecast\data\processed\port_cost_reference.parquet"

df = pl.read_parquet(path)

print("Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns)

print("\nData:")
print(df)

print("\nData types:")
print(df.schema)