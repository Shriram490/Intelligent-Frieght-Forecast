from pathlib import Path


processed_folder = Path("../data/processed")

print("Checking processed datasets...\n")

parquet_files = sorted(processed_folder.glob("*.parquet"))

print("Parquet files found:")
print("-" * 50)

for file in parquet_files:
    print(file.name)

print("\n" + "-" * 50)
print("Total Parquet files:", len(parquet_files))