from pathlib import Path
import pandas as pd


processed_folder = Path("../data/processed")

print("Profiling processed datasets...\n")

parquet_files = sorted(processed_folder.glob("*.parquet"))

for file in parquet_files:
    df = pd.read_parquet(file)

    print("=" * 70)
    print("FILE:", file.name)
    print("ROWS:", len(df))
    print("COLUMNS:", len(df.columns))
    print("COLUMN NAMES:", list(df.columns))

print("\n" + "=" * 70)
print("Total datasets:", len(parquet_files))