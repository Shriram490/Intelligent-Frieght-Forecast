from pathlib import Path
import pandas as pd

output_file = Path(
    "../data/processed/stevedoring_royalty_charges.parquet"
)

print("Creating Paradip stevedoring royalty charges dataset...")

records = [
    {
        "Port": "Paradip",
        "Charge_Category": "Stevedoring/Shore Handling Royalty",
        "Basis": "Per MT",
        "Unit": "Rs/MT",
        "Rate": 5.81,
        "Effective_From": "2026-04-01",
        "Applicable_To": "Stevedoring and shore handling agents"
    }
]

royalty_data = pd.DataFrame(records)

print("\nRoyalty charges:")
print(royalty_data.to_string(index=False))

print("\nShape:")
print(royalty_data.shape)

royalty_data.to_parquet(output_file, index=False)

print("\nRoyalty dataset saved successfully!")
print("Output:", output_file)