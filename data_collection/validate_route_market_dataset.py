import polars as pl
from pathlib import Path

print("Validating route market dataset...")
print("=" * 80)

# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "route_market_dataset.parquet"

# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading route market dataset...")

df = pl.read_parquet(DATA_PATH)

print(f"Rows: {df.height}")
print(f"Columns: {df.width}")

print("\nColumns:")
print(df.columns)

# ============================================================
# DATE VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("DATE VALIDATION")
print("=" * 80)

print(f"\nDate range:")
print(f"From: {df['Date'].min()}")
print(f"To:   {df['Date'].max()}")

print(f"\nUnique dates: {df['Date'].n_unique()}")

# ============================================================
# ROUTE VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("ROUTE VALIDATION")
print("=" * 80)

print(f"\nUnique origins: {df['Origin'].n_unique()}")
print(df.select("Origin").unique().sort("Origin"))

print(f"\nUnique destinations: {df['Destination'].n_unique()}")
print(df.select("Destination").unique().sort("Destination"))

print("\nRoute combinations:")

routes = (
    df
    .select(["Origin", "Destination"])
    .unique()
    .sort(["Origin", "Destination"])
)

print(routes)
print(f"\nNumber of unique routes: {routes.height}")

# ============================================================
# VESSEL VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("VESSEL VALIDATION")
print("=" * 80)

print(f"\nVessel types: {df['Vessel_Type'].n_unique()}")

print(
    df
    .select("Vessel_Type")
    .unique()
    .sort("Vessel_Type")
)

print("\nRows per vessel type:")

print(
    df
    .group_by("Vessel_Type")
    .len()
    .sort("Vessel_Type")
)

# ============================================================
# ROUTE × VESSEL COMBINATIONS
# ============================================================

print("\n" + "=" * 80)
print("ROUTE × VESSEL VALIDATION")
print("=" * 80)

route_vessel = (
    df
    .select(["Origin", "Destination", "Vessel_Type"])
    .unique()
    .sort(["Origin", "Destination", "Vessel_Type"])
)

print(route_vessel)

print(f"\nUnique route-vessel combinations: {route_vessel.height}")

# ============================================================
# DUPLICATE VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("DUPLICATE VALIDATION")
print("=" * 80)

duplicate_count = (
    df.height
    - df.select(
        ["Date", "Origin", "Destination", "Vessel_Type"]
    ).unique().height
)

print(
    f"\nDuplicate Date + Origin + Destination + Vessel_Type rows: "
    f"{duplicate_count}"
)

# ============================================================
# MISSING VALUES
# ============================================================

print("\n" + "=" * 80)
print("MISSING VALUES")
print("=" * 80)

missing = df.null_count()

print(missing)

# ============================================================
# ZERO VALUES
# ============================================================

print("\n" + "=" * 80)
print("ZERO VALUE CHECK")
print("=" * 80)

numeric_columns = [
    "Typical_DWT_Min",
    "Typical_DWT_Max",
    "Average_Speed_Knots",
    "Fuel_Consumption_MT_Day",
    "Typical_Cargo_MT",
    "Typical_Distance_NM",
    "Freight_Rate",
    "Crude_Oil_Brent",
    "Crude_Oil_Dubai",
    "Crude_Oil_Average",
    "Crude_Oil_WTI",
    "Coal_Australian_Price",
    "Coal_South_African_Price",
    "Iron_Ore_Price",
]

for column in numeric_columns:
    if column in df.columns:
        zero_count = df.filter(
            pl.col(column) == 0
        ).height

        print(f"{column}: {zero_count}")

# ============================================================
# INVALID VESSEL CHARACTERISTICS
# ============================================================

print("\n" + "=" * 80)
print("VESSEL CHARACTERISTIC VALIDATION")
print("=" * 80)

print("\nDWT range:")
print(
    df.select(
        [
            pl.col("Typical_DWT_Min").min().alias("Min_DWT"),
            pl.col("Typical_DWT_Max").max().alias("Max_DWT"),
        ]
    )
)

print("\nSpeed range:")
print(
    df.select(
        [
            pl.col("Average_Speed_Knots").min().alias("Min_Speed"),
            pl.col("Average_Speed_Knots").max().alias("Max_Speed"),
        ]
    )
)

print("\nFuel consumption range:")
print(
    df.select(
        [
            pl.col("Fuel_Consumption_MT_Day").min().alias("Min_Fuel"),
            pl.col("Fuel_Consumption_MT_Day").max().alias("Max_Fuel"),
        ]
    )
)

# ============================================================
# FREIGHT RATE VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("FREIGHT RATE VALIDATION")
print("=" * 80)

print(
    df.select(
        [
            pl.col("Freight_Rate").min().alias("Minimum"),
            pl.col("Freight_Rate").max().alias("Maximum"),
            pl.col("Freight_Rate").mean().alias("Average"),
        ]
    )
)

negative_freight = df.filter(
    pl.col("Freight_Rate") < 0
).height

zero_freight = df.filter(
    pl.col("Freight_Rate") == 0
).height

print(f"\nNegative freight rates: {negative_freight}")
print(f"Zero freight rates: {zero_freight}")

# ============================================================
# DISTANCE VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("DISTANCE VALIDATION")
print("=" * 80)

distance_nulls = df.filter(
    pl.col("Typical_Distance_NM").is_null()
).height

print(f"\nMissing distance values: {distance_nulls}")

print(
    "\nDistance statistics:"
)

print(
    df.select(
        [
            pl.col("Typical_Distance_NM").min().alias("Minimum"),
            pl.col("Typical_Distance_NM").max().alias("Maximum"),
            pl.col("Typical_Distance_NM").mean().alias("Average"),
        ]
    )
)

# ============================================================
# EXPECTED DATASET SIZE
# ============================================================

print("\n" + "=" * 80)
print("COMBINATION CHECK")
print("=" * 80)

unique_dates = df["Date"].n_unique()
unique_route_vessels = route_vessel.height

expected_rows = unique_dates * unique_route_vessels

print(f"\nUnique dates: {unique_dates}")
print(f"Route-vessel combinations: {unique_route_vessels}")
print(f"Expected rows: {expected_rows}")
print(f"Actual rows:   {df.height}")

if expected_rows == df.height:
    print("\n✓ Complete Date × Route × Vessel combinations")
else:
    print("\n⚠ Missing or extra Date × Route × Vessel combinations")

# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 80)
print("ROUTE MARKET DATASET VALIDATION COMPLETE")
print("=" * 80)