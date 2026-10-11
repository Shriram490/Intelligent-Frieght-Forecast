import pandas as pd
from pathlib import Path

# Path to route_market_dataset.parquet relative to data_collection folder or absolute
BASE_DIR = Path(__file__).resolve().parent.parent
file_path = BASE_DIR / "data" / "processed" / "route_market_dataset.parquet"

if not file_path.exists():
    print(f"Error: File not found at {file_path}")
    exit(1)

df = pd.read_parquet(file_path)

print("=" * 80)
print("ROUTE MARKET DATASET INSPECTION")
print("=" * 80)

print("\n1. DATASET SHAPE")
print(df.shape)

print("\n2. COLUMNS")
for column in df.columns:
    print("-", column)

print("\n3. DATA TYPES")
print(df.dtypes)

print("\n4. FIRST 10 ROWS")
print(df.head(10).to_string())

print("\n5. MISSING VALUES")
print(df.isnull().sum())

print("\n6. UNIQUE VALUES FOR IMPORTANT COLUMNS")

for column in ["Origin", "Destination", "Vessel_Type"]:
    if column in df.columns:
        print(f"\n{column}:")
        print(df[column].dropna().unique())

print("\n7. UNIQUE ORIGIN -> DESTINATION ROUTES")

if "Origin" in df.columns and "Destination" in df.columns:
    routes = df[["Origin", "Destination"]].drop_duplicates()
    print(routes.to_string(index=False))

print("\n8. BASIC STATISTICS")

numeric_columns = df.select_dtypes(include="number").columns
print(df[numeric_columns].describe().to_string())

print("\n" + "=" * 80)
print("INSPECTION COMPLETE")
print("=" * 80)
