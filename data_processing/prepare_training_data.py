import polars as pl
from pathlib import Path

# =============================================================================
# FREIGHT TRAINING DATA PREPARATION
# =============================================================================

print("=" * 80)
print("FREIGHT TRAINING DATA PREPARATION")
print("=" * 80)


# =============================================================================
# 1. PATHS
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "freight_features.parquet"

OUTPUT_DIR = BASE_DIR / "data" / "processed" / "training"

TRAIN_FILE = OUTPUT_DIR / "train.parquet"
VALIDATION_FILE = OUTPUT_DIR / "validation.parquet"
TEST_FILE = OUTPUT_DIR / "test.parquet"


# Create output directory if it does not exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# 2. READ FEATURE DATASET
# =============================================================================

print("\nReading freight feature dataset...")

df = pl.read_parquet(INPUT_FILE)

print(f"Input shape: {df.shape}")


# =============================================================================
# 3. SORT CHRONOLOGICALLY
# =============================================================================

print("\nSorting data chronologically...")

df = df.sort("Date")

print("Date sorting completed.")


# =============================================================================
# 4. CREATE NEXT-DAY TARGET
# =============================================================================

print("\nCreating forecasting target...")

# The model will predict the freight Price
# of the next available trading day.

df = df.with_columns(
    pl.col("Price")
    .shift(-1)
    .alias("Target_Price")
)

print("Created:")
print("- Target_Price")


# =============================================================================
# 5. SELECT FEATURES
# =============================================================================

print("\nSelecting model features...")

feature_columns = [
    "Price",
    "Open",
    "High",
    "Low",
    "Change %",
    "Year",
    "Month",
    "Quarter",
    "Day_of_Week",
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
    "Price_Range",
    "Price_Range_Pct",
    "Target_Price"
]

df = df.select(
    ["Date"] + feature_columns
)

print(f"Selected features: {len(feature_columns) - 1}")
print("Target: Target_Price")


# =============================================================================
# 6. REMOVE ROWS WITH MISSING VALUES
# =============================================================================

print("\nChecking missing values...")

missing_before = df.null_count().sum_horizontal()[0]

print(f"Rows affected by missing values: {missing_before}")

# Lag and rolling features naturally create missing values
# at the beginning of the dataset.
#
# The final row also has no Target_Price because there is
# no next-day price available.

df = df.drop_nulls()

print(f"Rows after removing missing values: {df.height}")


# =============================================================================
# 7. CHECK DATASET SIZE
# =============================================================================

print("\nDataset after preparation:")

print(f"Records: {df.height}")
print(f"Columns: {df.width}")

print("\nDate range:")
print(f"First date: {df['Date'].min()}")
print(f"Last date:  {df['Date'].max()}")


# =============================================================================
# 8. CHRONOLOGICAL TRAIN / VALIDATION / TEST SPLIT
# =============================================================================

print("\nCreating chronological train/validation/test split...")

total_rows = df.height

# 70% Training
# 15% Validation
# 15% Testing

train_end = int(total_rows * 0.70)
validation_end = int(total_rows * 0.85)

train_df = df.slice(0, train_end)

validation_df = df.slice(
    train_end,
    validation_end - train_end
)

test_df = df.slice(
    validation_end,
    total_rows - validation_end
)


# =============================================================================
# 9. DISPLAY SPLIT INFORMATION
# =============================================================================

print("\n" + "=" * 80)
print("DATASET SPLIT")
print("=" * 80)

print("\nTRAINING DATA")
print(f"Records: {train_df.height}")
print(f"From:    {train_df['Date'].min()}")
print(f"To:      {train_df['Date'].max()}")

print("\nVALIDATION DATA")
print(f"Records: {validation_df.height}")
print(f"From:    {validation_df['Date'].min()}")
print(f"To:      {validation_df['Date'].max()}")

print("\nTEST DATA")
print(f"Records: {test_df.height}")
print(f"From:    {test_df['Date'].min()}")
print(f"To:      {test_df['Date'].max()}")


# =============================================================================
# 10. SAVE DATASETS
# =============================================================================

print("\nSaving datasets...")

train_df.write_parquet(TRAIN_FILE)
validation_df.write_parquet(VALIDATION_FILE)
test_df.write_parquet(TEST_FILE)

print("\nSaved:")
print(f"- {TRAIN_FILE}")
print(f"- {VALIDATION_FILE}")
print(f"- {TEST_FILE}")


# =============================================================================
# 11. VERIFY SAVED DATA
# =============================================================================

print("\n" + "=" * 80)
print("SAVED DATA VERIFICATION")
print("=" * 80)

train_check = pl.read_parquet(TRAIN_FILE)
validation_check = pl.read_parquet(VALIDATION_FILE)
test_check = pl.read_parquet(TEST_FILE)

print(f"\nTrain shape:      {train_check.shape}")
print(f"Validation shape: {validation_check.shape}")
print(f"Test shape:       {test_check.shape}")


# =============================================================================
# 12. SHOW SAMPLE
# =============================================================================

print("\nTraining data sample:")

print(
    train_df.select(
        [
            "Date",
            "Price",
            "Price_Lag_1",
            "Price_MA_7",
            "Price_MA_30",
            "Target_Price"
        ]
    ).head(5)
)


print("\nTest data sample:")

print(
    test_df.select(
        [
            "Date",
            "Price",
            "Price_Lag_1",
            "Price_MA_7",
            "Price_MA_30",
            "Target_Price"
        ]
    ).head(5)
)


# =============================================================================
# COMPLETE
# =============================================================================

print("\n" + "=" * 80)
print("TRAINING DATA PREPARATION COMPLETE")
print("=" * 80)

print(f"\nTotal usable records: {df.height}")

print(f"\nTraining records:   {train_df.height}")
print(f"Validation records: {validation_df.height}")
print(f"Testing records:    {test_df.height}")

print("\nTarget:")
print("Target_Price = Price of the next available trading day")

print("\nSplit:")
print("70% Training")
print("15% Validation")
print("15% Testing")

print("\nOutput directory:")
print(OUTPUT_DIR)

print("=" * 80)
