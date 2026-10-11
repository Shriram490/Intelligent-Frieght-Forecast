from pathlib import Path
import polars as pl


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

OUTPUT_FILE = PROCESSED_DIR / "port_cost_reference.parquet"


# ---------------------------------------------------------
# DATASETS
# ---------------------------------------------------------

port_files = {
    "wharfage": "wharfage_rates.parquet",
    "handling": "handling_charges.parquet",
    "demurrage": "demurrage_charges.parquet",
    "pilotage_towage": "pilotage_towage_rates.parquet",
    "pilotage_additional": "pilotage_additional_charges.parquet",
    "vessel_port": "vessel_port_charges.parquet",
    "water_supply": "water_supply_charges.parquet",
    "weighment": "weighment_charges.parquet",
    "railway_siding": "railway_siding_charges.parquet",
    "environmental_berth": "environmental_berth_charges.parquet",
    "iohp_mchp": "iohp_mchp_connectivity_charges.parquet",
    "ecl_ccl": "ecl_ccl_handling_charges.parquet",
    "stevedoring_royalty": "stevedoring_royalty_charges.parquet",
    "transloading": "transloading_charges.parquet",
    "barge_facilitation": "barge_facilitation_charges.parquet",
    "sts_operation": "sts_operation_charges.parquet",
    "inland_waterway": "inland_waterway_charges.parquet",
    "sbm": "sbm_charges.parquet",
}


# ---------------------------------------------------------
# LOAD AND PROFILE PORT DATA
# ---------------------------------------------------------

print("Creating port cost reference layer...")
print("=" * 80)

records = []

for category, filename in port_files.items():

    filepath = PROCESSED_DIR / filename

    print(f"\nLoading: {filename}")

    if not filepath.exists():
        print("WARNING: File not found - skipping")
        continue

    df = pl.read_parquet(filepath)

    print(f"Rows: {df.height}")
    print(f"Columns: {df.width}")

    # -----------------------------------------------------
    # Create one reference record per source dataset
    # -----------------------------------------------------

    records.append({
        "Port": "Paradip",
        "Cost_Category": category,
        "Source_Dataset": filename,
        "Record_Count": df.height,
        "Column_Count": df.width,
        "Columns": ", ".join(df.columns),
    })


# ---------------------------------------------------------
# CREATE REFERENCE DATAFRAME
# ---------------------------------------------------------

reference = pl.DataFrame(records)


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

reference.write_parquet(OUTPUT_FILE)


# ---------------------------------------------------------
# REPORT
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("PORT COST REFERENCE CREATED")
print("=" * 80)

print(f"\nRows: {reference.height}")
print(f"Columns: {reference.width}")

print("\nReference categories:")
print(
    reference.select([
        "Cost_Category",
        "Source_Dataset",
        "Record_Count"
    ])
)

print("\nOutput:")
print(OUTPUT_FILE)