from pathlib import Path
import pandas as pd


processed_folder = Path("../data/processed")

datasets = []

for file in sorted(processed_folder.glob("*.parquet")):
    df = pd.read_parquet(file)

    datasets.append({
        "Dataset": file.name,
        "Rows": len(df),
        "Columns": len(df.columns),
        "Date_Column": "Date" if "Date" in df.columns else "None",
        "Description": ""
    })


inventory = pd.DataFrame(datasets)


descriptions = {
    "commodity_prices.parquet":
        "Historical monthly commodity prices from World Bank Pink Sheet",

    "freight_data.parquet":
        "Historical Baltic Dry Index market indicator",

    "fuel_prices.parquet":
        "Historical crude oil price series used as fuel-market indicators",

    "wharfage_rates.parquet":
        "Paradip wharfage rates by commodity, cargo type and volume",

    "handling_charges.parquet":
        "Paradip cargo handling charges",

    "demurrage_charges.parquet":
        "Paradip demurrage charges by storage period",

    "vessel_port_charges.parquet":
        "Paradip berth hire, roadstead and port dues",

    "pilotage_towage_rates.parquet":
        "Paradip pilotage and towage rates by vessel GRT",

    "pilotage_additional_charges.parquet":
        "Paradip additional pilotage-related charges",

    "sbm_charges.parquet":
        "Paradip Single Buoy Mooring charges",

    "water_supply_charges.parquet":
        "Paradip vessel water supply charges",

    "weighment_charges.parquet":
        "Paradip cargo weighment charges",

    "transloading_charges.parquet":
        "Paradip transloading charges",

    "environmental_berth_charges.parquet":
        "Paradip water sprinkling, spillage cleaning and berth-face dredging charges",

    "railway_siding_charges.parquet":
        "Paradip railway siding charges",

    "iohp_mchp_connectivity_charges.parquet":
        "Paradip IOHP-MCHP connectivity handling charges",

    "ecl_ccl_handling_charges.parquet":
        "Paradip ECL/CCL cargo handling charges",

    "stevedoring_royalty_charges.parquet":
        "Paradip stevedoring and shore-handling royalty",

    "barge_facilitation_charges.parquet":
        "Paradip barge loading facilitation charge",

    "sts_operation_charges.parquet":
        "Paradip STS operation charges",

    "inland_waterway_charges.parquet":
        "Paradip inland-waterway VRC and wharfage charges",
}


inventory["Description"] = inventory["Dataset"].map(descriptions)


print("\nDATA INVENTORY")
print("=" * 100)
print(inventory.to_string(index=False))


output_file = processed_folder / "data_inventory.parquet"

inventory.to_parquet(output_file, index=False)

print("\n" + "=" * 100)
print("Inventory saved successfully!")
print("Output:", output_file)