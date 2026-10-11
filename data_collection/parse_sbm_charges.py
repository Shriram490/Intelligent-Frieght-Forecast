from pathlib import Path
import pandas as pd

output_file = Path("../data/processed/sbm_charges.parquet")

print("Creating Paradip Single Buoy Mooring (SBM) charges dataset...")

records = [
    {
        "Port": "Paradip",
        "Charge_Category": "Berth Hire",
        "Traffic_Type": "Foreign",
        "Basis": "GRT per hour",
        "Unit": "USD/GRT/hour",
        "Rate": 0.00084,
        "Minimum_Charge": None
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Berth Hire",
        "Traffic_Type": "Coastal",
        "Basis": "GRT per hour",
        "Unit": "Rs/GRT/hour",
        "Rate": 0.28,
        "Minimum_Charge": None
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Pilotage",
        "Traffic_Type": "Foreign",
        "Basis": "GRT per entry",
        "Unit": "USD/GRT/entry",
        "Rate": 0.3654,
        "Minimum_Charge": 7325.86
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Pilotage",
        "Traffic_Type": "Coastal",
        "Basis": "GRT per entry",
        "Unit": "Rs/GRT/entry",
        "Rate": 11.24,
        "Minimum_Charge": 317137.67
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Tug Hire",
        "Traffic_Type": "Foreign",
        "Basis": "Per hour",
        "Unit": "USD/hour",
        "Rate": 2107.77,
        "Minimum_Charge": None
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Tug Hire",
        "Traffic_Type": "Coastal",
        "Basis": "Per hour",
        "Unit": "Rs/hour",
        "Rate": 34251.09,
        "Minimum_Charge": None
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Port Dues",
        "Traffic_Type": "Foreign",
        "Basis": "GRT per entry",
        "Unit": "USD/GRT/entry",
        "Rate": 0.3402,
        "Minimum_Charge": None
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Port Dues",
        "Traffic_Type": "Coastal",
        "Basis": "GRT per entry",
        "Unit": "Rs/GRT/entry",
        "Rate": 11.03,
        "Minimum_Charge": None
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Pilot Attendance",
        "Traffic_Type": "Foreign",
        "Basis": "Per hour",
        "Unit": "USD/hour",
        "Rate": 56.16,
        "Minimum_Charge": None
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Pilot Attendance",
        "Traffic_Type": "Coastal",
        "Basis": "Per hour",
        "Unit": "Rs/hour",
        "Rate": 1896.98,
        "Minimum_Charge": None
    }
]

sbm_data = pd.DataFrame(records)

print("\nSBM charges:")
print(sbm_data.to_string(index=False))

print("\nShape:")
print(sbm_data.shape)

print("\nCharge categories:")
print(sbm_data["Charge_Category"].unique())

sbm_data.to_parquet(output_file, index=False)

print("\nSBM dataset saved successfully!")
print("Output:", output_file)