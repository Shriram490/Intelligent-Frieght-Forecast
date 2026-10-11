from pathlib import Path
import polars as pl


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_FILE = PROCESSED_DIR / "data_dictionary.parquet"


# ---------------------------------------------------------
# DATASETS TO DOCUMENT
# ---------------------------------------------------------

datasets = sorted(PROCESSED_DIR.glob("*.parquet"))

# Don't include previously generated metadata files
datasets = [
    file for file in datasets
    if file.name not in [
        "data_inventory.parquet",
        "data_dictionary.parquet"
    ]
]


# ---------------------------------------------------------
# CREATE DATA DICTIONARY
# ---------------------------------------------------------

print("Creating data dictionary...")
print("=" * 80)

records = []

for file in datasets:

    print(f"\nProcessing: {file.name}")

    df = pl.read_parquet(file)

    for column in df.columns:

        series = df[column]

        record = {
            "Dataset": file.name,
            "Column": column,
            "Data_Type": str(series.dtype),
            "Rows": df.height,
            "Missing_Values": series.null_count(),
            "Unique_Values": series.n_unique(),
        }

        # -------------------------------------------------
        # Numerical information
        # -------------------------------------------------

        if series.dtype in [
            pl.Int8, pl.Int16, pl.Int32, pl.Int64,
            pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
            pl.Float32, pl.Float64
        ]:

            record["Minimum"] = series.min()
            record["Maximum"] = series.max()
            record["Mean"] = series.mean()

        else:

            record["Minimum"] = None
            record["Maximum"] = None
            record["Mean"] = None

        records.append(record)


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

dictionary = pl.DataFrame(records)

dictionary.write_parquet(OUTPUT_FILE)

print("\n" + "=" * 80)
print("DATA DICTIONARY CREATED")
print("=" * 80)

print(f"\nRows: {dictionary.height}")
print(f"Columns: {dictionary.width}")

print("\nDatasets documented:")
print(dictionary["Dataset"].unique().sort())

print(f"\nOutput:")
print(OUTPUT_FILE)