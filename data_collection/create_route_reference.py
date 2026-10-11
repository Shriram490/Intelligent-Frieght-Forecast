from pathlib import Path
import polars as pl
# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_FILE = PROCESSED_DIR / "route_reference.parquet"

# ---------------------------------------------------------
# ROUTE REFERENCE DATA
# ---------------------------------------------------------
# These are reference routes for the forecasting system.
# They are NOT historical voyage records.
#
# Exact nautical distances will be added after verification
# from a reliable route/distance source.
# ---------------------------------------------------------

routes = [
    {
        "Origin": "South Kalimantan",
        "Origin_Country": "Indonesia",
        "Destination": "Paradip",
        "Destination_Country": "India",
        "Region": "East Coast India",
        "Typical_Distance_NM": None,
        "Primary_Vessel_Types": "Supramax,Panamax",
        "Data_Status": "Reference",
    },
    {
        "Origin": "Newcastle",
        "Origin_Country": "Australia",
        "Destination": "Paradip",
        "Destination_Country": "India",
        "Region": "East Coast India",
        "Typical_Distance_NM": None,
        "Primary_Vessel_Types": "Panamax,Capesize",
        "Data_Status": "Reference",
    },
    {
        "Origin": "Hay Point",
        "Origin_Country": "Australia",
        "Destination": "Paradip",
        "Destination_Country": "India",
        "Region": "East Coast India",
        "Typical_Distance_NM": None,
        "Primary_Vessel_Types": "Panamax,Capesize",
        "Data_Status": "Reference",
    },
    {
        "Origin": "South Africa",
        "Origin_Country": "South Africa",
        "Destination": "Paradip",
        "Destination_Country": "India",
        "Region": "East Coast India",
        "Typical_Distance_NM": None,
        "Primary_Vessel_Types": "Panamax,Capesize",
        "Data_Status": "Reference",
    },
    {
        "Origin": "South Kalimantan",
        "Origin_Country": "Indonesia",
        "Destination": "Dhamra",
        "Destination_Country": "India",
        "Region": "East Coast India",
        "Typical_Distance_NM": None,
        "Primary_Vessel_Types": "Supramax,Panamax",
        "Data_Status": "Reference",
    },
    {
        "Origin": "Newcastle",
        "Origin_Country": "Australia",
        "Destination": "Dhamra",
        "Destination_Country": "India",
        "Region": "East Coast India",
        "Typical_Distance_NM": None,
        "Primary_Vessel_Types": "Panamax,Capesize",
        "Data_Status": "Reference",
    },
    {
        "Origin": "South Kalimantan",
        "Origin_Country": "Indonesia",
        "Destination": "Visakhapatnam",
        "Destination_Country": "India",
        "Region": "East Coast India",
        "Typical_Distance_NM": None,
        "Primary_Vessel_Types": "Supramax,Panamax",
        "Data_Status": "Reference",
    },
    {
        "Origin": "Newcastle",
        "Origin_Country": "Australia",
        "Destination": "Visakhapatnam",
        "Destination_Country": "India",
        "Region": "East Coast India",
        "Typical_Distance_NM": None,
        "Primary_Vessel_Types": "Panamax,Capesize",
        "Data_Status": "Reference",
    },
    {
        "Origin": "South Kalimantan",
        "Origin_Country": "Indonesia",
        "Destination": "Krishnapatnam",
        "Destination_Country": "India",
        "Region": "East Coast India",
        "Typical_Distance_NM": None,
        "Primary_Vessel_Types": "Supramax,Panamax",
        "Data_Status": "Reference",
    },
    {
        "Origin": "Newcastle",
        "Origin_Country": "Australia",
        "Destination": "Krishnapatnam",
        "Destination_Country": "India",
        "Region": "East Coast India",
        "Typical_Distance_NM": None,
        "Primary_Vessel_Types": "Panamax,Capesize",
        "Data_Status": "Reference",
    },
]


# ---------------------------------------------------------
# CREATE DATAFRAME
# ---------------------------------------------------------

print("Creating route reference dataset...")
print("=" * 80)

df = pl.DataFrame(routes)


# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------

print("\nRoute reference:")
print(df)

print("\nShape:")
print(df.shape)

print("\nOrigin countries:")
print(df["Origin_Country"].unique())

print("\nDestination ports:")
print(df["Destination"].unique())

print("\nMissing values:")
print(df.null_count())


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

df.write_parquet(OUTPUT_FILE)


# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("ROUTE REFERENCE DATASET CREATED")
print("=" * 80)

print(f"\nRows: {df.height}")
print(f"Columns: {df.width}")

print("\nOutput:")
print(OUTPUT_FILE)