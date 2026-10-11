from pathlib import Path
import pandas as pd

output_file = Path(
    "../data/processed/railway_siding_charges.parquet"
)

print("Creating Paradip railway siding charges dataset...")

records = [
    {
        "Port": "Paradip",
        "Siding_Type": "Warehousing Zone",
        "Charge_Category": "Railway Siding",
        "Basis": "Per MT",
        "Unit": "Rs/MT",
        "Rate": 4.88,
        "Additional_Placement_Charge": None
    },
    {
        "Port": "Paradip",
        "Siding_Type": "Other Sidings",
        "Charge_Category": "Railway Siding",
        "Basis": "Per MT",
        "Unit": "Rs/MT",
        "Rate": 4.59,
        "Additional_Placement_Charge": 2296.25
    }
]

railway_data = pd.DataFrame(records)

print("\nRailway siding charges:")
print(railway_data.to_string(index=False))

print("\nShape:")
print(railway_data.shape)

railway_data.to_parquet(output_file, index=False)

print("\nRailway siding dataset saved successfully!")
print("Output:", output_file)