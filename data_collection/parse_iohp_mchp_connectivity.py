from pathlib import Path
import pandas as pd

output_file = Path(
    "../data/processed/iohp_mchp_connectivity_charges.parquet"
)

print("Creating Paradip IOHP-MCHP connectivity charges dataset...")

records = [
    {
        "Port": "Paradip",
        "Operation": (
            "Unloading dry bulk cargo from wagon at wagon tippler "
            "of Iron Ore Handling Plant and stacking at stockyard "
            "of Mechanized Coal Handling Plant using IOHP-MCHP connectivity"
        ),
        "Cargo_Type": "Dry Bulk Cargo",
        "Traffic_Type": "Foreign",
        "Basis": "Per MT",
        "Unit": "Rs/MT",
        "Rate": 72.64
    },
    {
        "Port": "Paradip",
        "Operation": (
            "Unloading dry bulk cargo from wagon at wagon tippler "
            "of Iron Ore Handling Plant and stacking at stockyard "
            "of Mechanized Coal Handling Plant using IOHP-MCHP connectivity"
        ),
        "Cargo_Type": "Dry Bulk Cargo",
        "Traffic_Type": "Coastal",
        "Basis": "Per MT",
        "Unit": "Rs/MT",
        "Rate": 72.64
    }
]

connectivity_data = pd.DataFrame(records)

print("\nIOHP-MCHP connectivity charges:")
print(connectivity_data.to_string(index=False))

print("\nShape:")
print(connectivity_data.shape)

print("\nTraffic types:")
print(connectivity_data["Traffic_Type"].unique())

connectivity_data.to_parquet(output_file, index=False)

print("\nIOHP-MCHP connectivity dataset saved successfully!")
print("Output:", output_file)