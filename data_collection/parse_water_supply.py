from pathlib import Path
import pandas as pd

output_file = Path("../data/processed/water_supply_charges.parquet")

print("Creating Paradip water supply charges dataset...")

records = [
    {
        "Port": "Paradip",
        "Supply_Mode": "Direct at Berth",
        "Traffic_Type": "Foreign",
        "Basis": "Per MT",
        "Unit": "USD/MT",
        "Rate": 5.61,
        "Minimum_Charge": 84.30
    },
    {
        "Port": "Paradip",
        "Supply_Mode": "Direct at Berth",
        "Traffic_Type": "Coastal",
        "Basis": "Per MT",
        "Unit": "Rs/MT",
        "Rate": 138.19,
        "Minimum_Charge": 2072.63
    },
    {
        "Port": "Paradip",
        "Supply_Mode": "Barge at Mooring Wharf/Jetty",
        "Traffic_Type": "Foreign",
        "Basis": "Per MT",
        "Unit": "USD/MT",
        "Rate": 11.24,
        "Minimum_Charge": 449.65
    },
    {
        "Port": "Paradip",
        "Supply_Mode": "Barge at Mooring Wharf/Jetty",
        "Traffic_Type": "Coastal",
        "Basis": "Per MT",
        "Unit": "Rs/MT",
        "Rate": 276.41,
        "Minimum_Charge": 11055.91
    },
    {
        "Port": "Paradip",
        "Supply_Mode": "Barge at Anchorage/Roads",
        "Traffic_Type": "Foreign",
        "Basis": "Per MT",
        "Unit": "USD/MT",
        "Rate": 26.54,
        "Minimum_Charge": 2213.16
    },
    {
        "Port": "Paradip",
        "Supply_Mode": "Barge at Anchorage/Roads",
        "Traffic_Type": "Coastal",
        "Basis": "Per MT",
        "Unit": "Rs/MT",
        "Rate": 653.00,
        "Minimum_Charge": 54416.76
    }
]

water_data = pd.DataFrame(records)

print("\nWater supply charges:")
print(water_data.to_string(index=False))

print("\nShape:")
print(water_data.shape)

print("\nSupply modes:")
print(water_data["Supply_Mode"].unique())

water_data.to_parquet(output_file, index=False)

print("\nWater supply dataset saved successfully!")
print("Output:", output_file)