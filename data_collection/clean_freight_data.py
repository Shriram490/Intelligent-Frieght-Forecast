import polars as pl
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "freight_data.parquet"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "freight_data_clean.parquet"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 80)
print("FREIGHT DATA CLEANING")
print("=" * 80)

print("\nReading freight dataset...")

df = pl.read_parquet(INPUT_FILE)

print(f"Original shape: {df.shape}")


# ============================================================
# 1. SORT BY DATE
# ============================================================

print("\nSorting data chronologically...")

df = df.sort("Date")

print("Date sorting completed.")


# ============================================================
# 2. REPLACE INVALID ZERO OHLC VALUES
# ============================================================

print("\nChecking OHLC columns for zero values...")

ohlc_columns = ["Open", "High", "Low"]

for column in ohlc_columns:

    zero_count = df.filter(
        pl.col(column) == 0
    ).height

    print(f"{column}: {zero_count} zero values")

    if zero_count > 0:
        df = df.with_columns(
            pl.when(pl.col(column) == 0)
            .then(None)
            .otherwise(pl.col(column))
            .alias(column)
        )


# ============================================================
# 3. DO NOT MODIFY PRICE
# ============================================================

print("\nPrice column:")
print("Zero prices: ", df.filter(pl.col("Price") == 0).height)
print("Negative prices:", df.filter(pl.col("Price") < 0).height)

print("Price values will not be modified.")


# ============================================================
# 4. DO NOT REMOVE EXTREME MOVEMENTS
# ============================================================

print("\nChecking extreme Change % values...")

extreme_count = df.filter(
    pl.col("Change %").abs() > 10
).height

print(f"Extreme movements (> ±10%): {extreme_count}")

print("Extreme movements will be retained because they may represent")
print("real freight-market movements rather than data errors.")


# ============================================================
# 5. CHECK MISSING VALUES AFTER CLEANING
# ============================================================

print("\nMissing values after cleaning:")

print(df.null_count())


# ============================================================
# 6. CHECK ROW COUNT
# ============================================================

print("\nRow count check:")

print(f"Original rows: {2789}")
print(f"Cleaned rows:  {df.height}")

if df.height == 2789:
    print("Row count preserved: YES")
else:
    print("WARNING: Row count changed!")


# ============================================================
# 7. SAVE CLEAN DATASET
# ============================================================

print("\nSaving cleaned dataset...")

df.write_parquet(OUTPUT_FILE)

print(f"Saved to:")
print(OUTPUT_FILE)


# ============================================================
# 8. DISPLAY CLEANED DATA
# ============================================================

print("\nFirst 5 records:")

print(df.head(5))

print("\nLast 5 records:")

print(df.tail(5))


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("CLEANING COMPLETE")
print("=" * 80)

print(f"""
Input records:  {2789}
Output records: {df.height}

Cleaning performed:
- Sorted dates chronologically
- Replaced zero Open values with null
- Replaced zero High values with null
- Replaced zero Low values with null
- Preserved Price values
- Preserved Change % values
- Preserved extreme market movements
- Preserved all records

Output:
freight_data_clean.parquet
""")