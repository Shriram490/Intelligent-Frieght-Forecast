from pathlib import Path
import pandas as pd

output_file = Path("../data/processed/weighment_charges.parquet")

print("Creating Paradip weighment charges dataset...")

records = [
    {
        "Port": "Paradip",
        "Commodity_Category": "Iron Ore/Chrome Ore/Other Ores",
        "Basis": "Per Ton",
        "Unit": "Rs/ton",
        "Rate": 2.81,
        "Minimum_Charge": 28.51,
        "Minimum_Basis": "Per Consignment"
    },
    {
        "Port": "Paradip",
        "Commodity_Category": "Other Commodities",
        "Basis": "Per Ton",
        "Unit": "Rs/ton",
        "Rate": 4.20,
        "Minimum_Charge": 42.16,
        "Minimum_Basis": "Per Consignment"
    }
]

weighment_data = pd.DataFrame(records)

print("\nWeighment charges:")
print(weighment_data.to_string(index=False))

print("\nShape:")
print(weighment_data.shape)

weighment_data.to_parquet(output_file, index=False)

print("\nWeighment dataset saved successfully!")
print("Output:", output_file)