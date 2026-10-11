from pathlib import Path
import polars as pl


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

OUTPUT_FILE = PROCESSED_DIR / "vessel_reference.parquet"


# ---------------------------------------------------------
# VESSEL REFERENCE DATA
# ---------------------------------------------------------
# These are reference/assumption ranges used for modelling.
# They are NOT historical vessel observations.

vessels = [
    {
        "Vessel_Type": "Handysize",
        "Typical_DWT_Min": 10000,
        "Typical_DWT_Max": 40000,
        "Average_Speed_Knots": 12.0,
        "Fuel_Consumption_MT_Day": 20.0,
        "Typical_Cargo_MT": 30000,
    },
    {
        "Vessel_Type": "Supramax",
        "Typical_DWT_Min": 40000,
        "Typical_DWT_Max": 60000,
        "Average_Speed_Knots": 12.5,
        "Fuel_Consumption_MT_Day": 25.0,
        "Typical_Cargo_MT": 50000,
    },
    {
        "Vessel_Type": "Ultramax",
        "Typical_DWT_Min": 60000,
        "Typical_DWT_Max": 65000,
        "Average_Speed_Knots": 12.5,
        "Fuel_Consumption_MT_Day": 27.0,
        "Typical_Cargo_MT": 60000,
    },
    {
        "Vessel_Type": "Panamax",
        "Typical_DWT_Min": 65000,
        "Typical_DWT_Max": 85000,
        "Average_Speed_Knots": 13.0,
        "Fuel_Consumption_MT_Day": 30.0,
        "Typical_Cargo_MT": 75000,
    },
    {
        "Vessel_Type": "Capesize",
        "Typical_DWT_Min": 100000,
        "Typical_DWT_Max": 200000,
        "Average_Speed_Knots": 13.5,
        "Fuel_Consumption_MT_Day": 45.0,
        "Typical_Cargo_MT": 150000,
    },
]


# ---------------------------------------------------------
# CREATE DATAFRAME
# ---------------------------------------------------------

print("Creating vessel reference dataset...")
print("=" * 80)

df = pl.DataFrame(vessels)

print("\nVessel reference:")
print(df)

print("\nShape:")
print(df.shape)

print("\nVessel types:")
print(df["Vessel_Type"].to_list())


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

df.write_parquet(OUTPUT_FILE)

print("\n" + "=" * 80)
print("VESSEL REFERENCE DATASET CREATED")
print("=" * 80)

print(f"\nRows: {df.height}")
print(f"Columns: {df.width}")

print("\nOutput:")
print(OUTPUT_FILE)