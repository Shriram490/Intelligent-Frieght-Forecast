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
    / "freight_data_clean.parquet"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "freight_features.parquet"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 80)
print("FREIGHT FEATURE ENGINEERING")
print("=" * 80)

print("\nReading cleaned freight dataset...")

df = pl.read_parquet(INPUT_FILE)

print(f"Input shape: {df.shape}")


# ============================================================
# 1. MAKE SURE DATA IS SORTED
# ============================================================

df = df.sort("Date")

print("\nData sorted chronologically.")


# ============================================================
# 2. TIME FEATURES
# ============================================================

print("\nCreating time features...")

df = df.with_columns(
    [
        pl.col("Date").dt.year().alias("Year"),

        pl.col("Date").dt.month().alias("Month"),

        pl.col("Date").dt.quarter().alias("Quarter"),

        pl.col("Date").dt.weekday().alias("Day_of_Week"),
    ]
)

print("Created:")
print("- Year")
print("- Month")
print("- Quarter")
print("- Day_of_Week")


# ============================================================
# 3. LAG FEATURES
# ============================================================

print("\nCreating lag features...")

df = df.with_columns(
    [
        pl.col("Price").shift(1).alias("Price_Lag_1"),

        pl.col("Price").shift(7).alias("Price_Lag_7"),

        pl.col("Price").shift(30).alias("Price_Lag_30"),
    ]
)

print("Created:")
print("- Price_Lag_1")
print("- Price_Lag_7")
print("- Price_Lag_30")


# ============================================================
# 4. ROLLING AVERAGES
# ============================================================

print("\nCreating rolling averages...")

df = df.with_columns(
    [
        pl.col("Price")
        .shift(1)
        .rolling_mean(window_size=7)
        .alias("Price_MA_7"),

        pl.col("Price")
        .shift(1)
        .rolling_mean(window_size=30)
        .alias("Price_MA_30"),

        pl.col("Price")
        .shift(1)
        .rolling_mean(window_size=90)
        .alias("Price_MA_90"),
    ]
)

print("Created:")
print("- Price_MA_7")
print("- Price_MA_30")
print("- Price_MA_90")


# ============================================================
# 5. ROLLING VOLATILITY
# ============================================================

print("\nCreating volatility features...")

df = df.with_columns(
    [
        pl.col("Price")
        .shift(1)
        .rolling_std(window_size=7)
        .alias("Volatility_7"),

        pl.col("Price")
        .shift(1)
        .rolling_std(window_size=30)
        .alias("Volatility_30"),
    ]
)

print("Created:")
print("- Volatility_7")
print("- Volatility_30")


# ============================================================
# 6. MOMENTUM / PRICE CHANGE
# ============================================================

print("\nCreating momentum features...")

df = df.with_columns(
    [
        (
            (
                pl.col("Price_Lag_1")
                - pl.col("Price_Lag_7")
            )
            / pl.col("Price_Lag_7")
        * 100
        ).alias("Price_Change_7"),

        (
            (
                pl.col("Price_Lag_1")
                - pl.col("Price_Lag_30")
            )
            / pl.col("Price_Lag_30")
        * 100
        ).alias("Price_Change_30"),
    ]
)

print("Created:")
print("- Price_Change_7")
print("- Price_Change_30")


# ============================================================
# 7. PRICE RANGE
# ============================================================

print("\nCreating price range feature...")

df = df.with_columns(
    (
        pl.col("High") - pl.col("Low")
    ).alias("Price_Range")
)

print("Created:")
print("- Price_Range")


# ============================================================
# 8. PRICE RANGE PERCENTAGE
# ============================================================

print("\nCreating price range percentage...")

df = df.with_columns(
    (
        (
            (pl.col("High") - pl.col("Low"))
            / pl.col("Price")
        ) * 100
    ).alias("Price_Range_Pct")
)

print("Created:")
print("- Price_Range_Pct")


# ============================================================
# 9. SAVE FEATURE DATASET
# ============================================================

print("\nSaving feature dataset...")

df.write_parquet(OUTPUT_FILE)

print(f"Saved to:")
print(OUTPUT_FILE)


# ============================================================
# 10. SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("FEATURE ENGINEERING COMPLETE")
print("=" * 80)

print(f"""
Original columns: 6
Final columns:    {len(df.columns)}

Original records: 2789
Final records:    {df.height}

Output:
freight_features.parquet
""")


# ============================================================
# 11. DISPLAY COLUMN NAMES
# ============================================================

print("\nFinal columns:")

for column in df.columns:
    print(f"- {column}")


# ============================================================
# 12. DISPLAY SAMPLE
# ============================================================

print("\nLast 10 records:")

print(
    df.select(
        [
            "Date",
            "Price",
            "Price_Lag_1",
            "Price_Lag_7",
            "Price_Lag_30",
            "Price_MA_7",
            "Price_MA_30",
            "Price_MA_90",
            "Volatility_7",
            "Volatility_30",
            "Price_Change_7",
            "Price_Change_30",
        ]
    ).tail(10)
)