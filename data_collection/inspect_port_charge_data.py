import polars as pl
from pathlib import Path

BASE = Path(r"C:\intelligentfrieghtforecast\data\processed")

files = [
    "wharfage_rates.parquet",
    "handling_charges.parquet",
    "demurrage_charges.parquet",
    "pilotage_towage_rates.parquet",
    "pilotage_additional_charges.parquet",
    "vessel_port_charges.parquet",
    "water_supply_charges.parquet",
    "weighment_charges.parquet",
    "railway_siding_charges.parquet",
    "environmental_berth_charges.parquet",
    "iohp_mchp_connectivity_charges.parquet",
    "ecl_ccl_handling_charges.parquet",
    "stevedoring_royalty_charges.parquet",
    "transloading_charges.parquet",
    "barge_facilitation_charges.parquet",
    "sts_operation_charges.parquet",
    "inland_waterway_charges.parquet",
    "sbm_charges.parquet",
]

for filename in files:
    path = BASE / filename

    print("\n" + "=" * 80)
    print(filename)
    print("=" * 80)

    df = pl.read_parquet(path)

    print("Shape:", df.shape)
    print("Columns:", df.columns)
    print("\nData:")
    print(df)