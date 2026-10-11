from pathlib import Path
import pandas as pd

output_file = Path("../data/processed/transloading_charges.parquet")

print("Creating Paradip transloading charges dataset...")

records = [
    {
        "Port": "Paradip",
        "Charge_Category": "Cargo Transloading",
        "Operation": "Cargo transloaded from/to mother vessel",
        "Basis": "Per Tonne",
        "Unit": "Rs/ton",
        "Rate": 4.33,
        "Applicable_From": "2024-10-07",
        "Notes": "Section 4.8 states the fee was enhanced by Rs.2.29 per ton from 07.10.2024 from the earlier Rs.2.04 per ton."
    }
]

transloading_data = pd.DataFrame(records)

print("\nTransloading charges:")
print(transloading_data.to_string(index=False))

print("\nShape:")
print(transloading_data.shape)

transloading_data.to_parquet(output_file, index=False)

print("\nTransloading dataset saved successfully!")
print("Output:", output_file)