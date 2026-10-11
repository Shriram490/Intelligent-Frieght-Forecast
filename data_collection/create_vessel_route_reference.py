from pathlib import Path
import polars as pl


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

OUTPUT_FILE = PROCESSED_DIR / "vessel_route_reference.parquet"


# ---------------------------------------------------------
# ROUTE + VESSEL REFERENCE DATA
# ---------------------------------------------------------
#
# These are scenario/reference combinations.
# Values that are not yet sourced are kept as NULL.
#
# DO NOT treat this as historical vessel movement data.
# ---------------------------------------------------------

records = [
    # Indonesia -> Paradip
    {
        "Origin": "Indonesia",
        "Destination": "Paradip",
        "Vessel_Type": "Supramax",
        "Capacity_Min_MT": 50000,
        "Capacity_Max_MT": 60000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },
    {
        "Origin": "Indonesia",
        "Destination": "Paradip",
        "Vessel_Type": "Ultramax",
        "Capacity_Min_MT": 60000,
        "Capacity_Max_MT": 70000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },
    {
        "Origin": "Indonesia",
        "Destination": "Paradip",
        "Vessel_Type": "Panamax",
        "Capacity_Min_MT": 70000,
        "Capacity_Max_MT": 85000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },

    # Australia -> Paradip
    {
        "Origin": "Australia",
        "Destination": "Paradip",
        "Vessel_Type": "Supramax",
        "Capacity_Min_MT": 50000,
        "Capacity_Max_MT": 60000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },
    {
        "Origin": "Australia",
        "Destination": "Paradip",
        "Vessel_Type": "Ultramax",
        "Capacity_Min_MT": 60000,
        "Capacity_Max_MT": 70000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },
    {
        "Origin": "Australia",
        "Destination": "Paradip",
        "Vessel_Type": "Panamax",
        "Capacity_Min_MT": 70000,
        "Capacity_Max_MT": 85000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },

    # Indonesia -> Dhamra
    {
        "Origin": "Indonesia",
        "Destination": "Dhamra",
        "Vessel_Type": "Supramax",
        "Capacity_Min_MT": 50000,
        "Capacity_Max_MT": 60000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },
    {
        "Origin": "Indonesia",
        "Destination": "Dhamra",
        "Vessel_Type": "Ultramax",
        "Capacity_Min_MT": 60000,
        "Capacity_Max_MT": 70000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },
    {
        "Origin": "Indonesia",
        "Destination": "Dhamra",
        "Vessel_Type": "Panamax",
        "Capacity_Min_MT": 70000,
        "Capacity_Max_MT": 85000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },

    # Australia -> Dhamra
    {
        "Origin": "Australia",
        "Destination": "Dhamra",
        "Vessel_Type": "Supramax",
        "Capacity_Min_MT": 50000,
        "Capacity_Max_MT": 60000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },
    {
        "Origin": "Australia",
        "Destination": "Dhamra",
        "Vessel_Type": "Ultramax",
        "Capacity_Min_MT": 60000,
        "Capacity_Max_MT": 70000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },
    {
        "Origin": "Australia",
        "Destination": "Dhamra",
        "Vessel_Type": "Panamax",
        "Capacity_Min_MT": 70000,
        "Capacity_Max_MT": 85000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },

    # Indonesia -> Visakhapatnam
    {
        "Origin": "Indonesia",
        "Destination": "Visakhapatnam",
        "Vessel_Type": "Supramax",
        "Capacity_Min_MT": 50000,
        "Capacity_Max_MT": 60000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },
    {
        "Origin": "Indonesia",
        "Destination": "Visakhapatnam",
        "Vessel_Type": "Ultramax",
        "Capacity_Min_MT": 60000,
        "Capacity_Max_MT": 70000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },
    {
        "Origin": "Indonesia",
        "Destination": "Visakhapatnam",
        "Vessel_Type": "Panamax",
        "Capacity_Min_MT": 70000,
        "Capacity_Max_MT": 85000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },

    # Australia -> Visakhapatnam
    {
        "Origin": "Australia",
        "Destination": "Visakhapatnam",
        "Vessel_Type": "Supramax",
        "Capacity_Min_MT": 50000,
        "Capacity_Max_MT": 60000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },
    {
        "Origin": "Australia",
        "Destination": "Visakhapatnam",
        "Vessel_Type": "Ultramax",
        "Capacity_Min_MT": 60000,
        "Capacity_Max_MT": 70000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },
    {
        "Origin": "Australia",
        "Destination": "Visakhapatnam",
        "Vessel_Type": "Panamax",
        "Capacity_Min_MT": 70000,
        "Capacity_Max_MT": 85000,
        "Speed_Knots": None,
        "Fuel_Consumption_MT_Day": None,
        "Distance_NM": None,
        "Data_Status": "Reference",
    },
]


# ---------------------------------------------------------
# CREATE DATAFRAME
# ---------------------------------------------------------

print("Creating vessel and route reference dataset...")
print("=" * 80)

df = pl.DataFrame(records)


# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns)

print("\nRoutes:")
print(df.select(["Origin", "Destination"]).unique())

print("\nVessel types:")
print(df["Vessel_Type"].unique())

print("\nMissing values:")
print(df.null_count())


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

df.write_parquet(OUTPUT_FILE)

print("\n" + "=" * 80)
print("VESSEL + ROUTE REFERENCE CREATED")
print("=" * 80)

print(f"\nRows: {df.height}")
print(f"Columns: {df.width}")

print(f"\nOutput:")
print(OUTPUT_FILE)