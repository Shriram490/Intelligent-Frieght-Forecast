from pathlib import Path
import pandas as pd

output_file = Path(
    "../data/processed/environmental_berth_charges.parquet"
)

print("Creating Paradip environmental and berth maintenance charges dataset...")

records = [
    {
        "Port": "Paradip",
        "Charge_Category": "Environmental/Berth Maintenance",
        "Activities": "Water sprinkling, spillage cleaning, berth face dredging",
        "Basis": "Per MT",
        "Unit": "Rs/MT",
        "Rate": 2.87
    }
]

charge_data = pd.DataFrame(records)

print("\nEnvironmental and berth maintenance charges:")
print(charge_data.to_string(index=False))

print("\nShape:")
print(charge_data.shape)

charge_data.to_parquet(output_file, index=False)

print("\nDataset saved successfully!")
print("Output:", output_file)