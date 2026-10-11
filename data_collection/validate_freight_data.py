import polars as pl
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FREIGHT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "freight_data.parquet"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 80)
print("FREIGHT DATA VALIDATION")
print("=" * 80)

print("\nReading freight dataset...")

df = pl.read_parquet(FREIGHT_FILE)

print(f"Shape: {df.shape}")


# ============================================================
# 1. CHECK COLUMN NAMES
# ============================================================

print("\n" + "=" * 80)
print("1. COLUMNS")
print("=" * 80)

print(df.columns)


# ============================================================
# 2. CHECK DATA TYPES
# ============================================================

print("\n" + "=" * 80)
print("2. DATA TYPES")
print("=" * 80)

print(df.schema)


# ============================================================
# 3. CHECK DUPLICATE DATES
# ============================================================

print("\n" + "=" * 80)
print("3. DUPLICATE DATES")
print("=" * 80)

duplicate_dates = (
    df.group_by("Date")
    .agg(pl.len().alias("Count"))
    .filter(pl.col("Count") > 1)
)

print(f"Duplicate date records: {duplicate_dates.height}")

if duplicate_dates.height > 0:
    print(duplicate_dates)


# ============================================================
# 4. CHECK MISSING VALUES
# ============================================================

print("\n" + "=" * 80)
print("4. MISSING VALUES")
print("=" * 80)

missing_values = df.null_count()

print(missing_values)


# ============================================================
# 5. CHECK ZERO VALUES
# ============================================================

print("\n" + "=" * 80)
print("5. ZERO VALUES")
print("=" * 80)

numeric_columns = ["Price", "Open", "High", "Low", "Change %"]

for column in numeric_columns:
    zero_count = df.filter(pl.col(column) == 0).height
    print(f"{column}: {zero_count} zero values")


# ============================================================
# 6. CHECK NEGATIVE VALUES
# ============================================================

print("\n" + "=" * 80)
print("6. NEGATIVE VALUES")
print("=" * 80)

for column in numeric_columns:
    negative_count = df.filter(pl.col(column) < 0).height
    print(f"{column}: {negative_count} negative values")


# ============================================================
# 7. CHECK DATE ORDER
# ============================================================

print("\n" + "=" * 80)
print("7. DATE ORDER")
print("=" * 80)

is_sorted = df["Date"].is_sorted()

print(f"Dates sorted chronologically: {is_sorted}")


# ============================================================
# 8. CHECK PRICE CONSISTENCY
# ============================================================

print("\n" + "=" * 80)
print("8. PRICE CONSISTENCY")
print("=" * 80)

price_mismatch = df.filter(
    (pl.col("Price") != pl.col("Open"))
    | (pl.col("Price") != pl.col("High"))
    | (pl.col("Price") != pl.col("Low"))
)

print(f"Records where Price differs from Open/High/Low: {price_mismatch.height}")

if price_mismatch.height > 0:
    print("\nSample mismatches:")
    print(price_mismatch.head(10))


# ============================================================
# 9. CHECK CHANGE %
# ============================================================

print("\n" + "=" * 80)
print("9. CHANGE % VALIDATION")
print("=" * 80)

change_stats = df.select(
    [
        pl.col("Change %").min().alias("Minimum"),
        pl.col("Change %").max().alias("Maximum"),
        pl.col("Change %").mean().alias("Average"),
    ]
)

print(change_stats)


# ============================================================
# 10. CHECK EXTREME PRICE MOVEMENTS
# ============================================================

print("\n" + "=" * 80)
print("10. EXTREME PRICE MOVEMENTS")
print("=" * 80)

extreme_changes = df.filter(
    pl.col("Change %").abs() > 10
)

print(f"Records with price change greater than ±10%: {extreme_changes.height}")

if extreme_changes.height > 0:
    print("\nSample extreme movements:")
    print(extreme_changes.head(20))


# ============================================================
# 11. BASIC PRICE STATISTICS
# ============================================================

print("\n" + "=" * 80)
print("11. PRICE STATISTICS")
print("=" * 80)

price_statistics = df.select(
    [
        pl.col("Price").count().alias("Count"),
        pl.col("Price").mean().alias("Mean"),
        pl.col("Price").median().alias("Median"),
        pl.col("Price").std().alias("Std Dev"),
        pl.col("Price").min().alias("Minimum"),
        pl.col("Price").max().alias("Maximum"),
    ]
)

print(price_statistics)


# ============================================================
# 12. DATE RANGE
# ============================================================

print("\n" + "=" * 80)
print("12. DATE RANGE")
print("=" * 80)

print(f"First date: {df['Date'].min()}")
print(f"Last date:  {df['Date'].max()}")


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)

print(f"""
Total records: {df.height}

Duplicate dates: {duplicate_dates.height}

Missing values checked: YES

Zero values checked: YES

Negative values checked: YES

Date ordering checked: YES

Price consistency checked: YES

Extreme movements checked: YES
""")