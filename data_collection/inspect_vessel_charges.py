import pandas as pd

file_path = "../data/processed/vessel_port_charges.parquet"

print("Reading vessel port charges...")

data = pd.read_parquet(file_path)

print("\nFull dataset:")
print(data.to_string(index=False))

print("\nColumns:")
print(data.columns.tolist())

print("\nShape:")
print(data.shape)

print("\nData types:")
print(data.dtypes)