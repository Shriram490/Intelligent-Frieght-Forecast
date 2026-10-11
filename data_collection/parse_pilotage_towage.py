from pathlib import Path
import pandas as pd

output_file = Path("../data/processed/pilotage_towage_rates.parquet")

print("Creating Paradip Pilotage & Towage dataset...")

records = [
    {
        "Port": "Paradip",
        "Slab": "Up to 30,000 GRT",
        "Min_GRT": 0,
        "Max_GRT": 30000,
        "Traffic_Type": "Foreign",
        "Fixed_Rate": 0.0,
        "Incremental_Rate": 0.7148,
        "Unit": "USD/GRT"
    },
    {
        "Port": "Paradip",
        "Slab": "Up to 30,000 GRT",
        "Min_GRT": 0,
        "Max_GRT": 30000,
        "Traffic_Type": "Coastal",
        "Fixed_Rate": 0.0,
        "Incremental_Rate": 17.59,
        "Unit": "Rs/GRT"
    },
    {
        "Port": "Paradip",
        "Slab": "30,001 to 60,000 GRT",
        "Min_GRT": 30001,
        "Max_GRT": 60000,
        "Traffic_Type": "Foreign",
        "Fixed_Rate": 21444.00,
        "Incremental_Rate": 0.5716,
        "Unit": "USD"
    },
    {
        "Port": "Paradip",
        "Slab": "30,001 to 60,000 GRT",
        "Min_GRT": 30001,
        "Max_GRT": 60000,
        "Traffic_Type": "Coastal",
        "Fixed_Rate": 527700.00,
        "Incremental_Rate": 14.06,
        "Unit": "Rs"
    },
    {
        "Port": "Paradip",
        "Slab": "60,001 to 75,000 GRT",
        "Min_GRT": 60001,
        "Max_GRT": 75000,
        "Traffic_Type": "Foreign",
        "Fixed_Rate": 38592.00,
        "Incremental_Rate": 0.4289,
        "Unit": "USD"
    },
    {
        "Port": "Paradip",
        "Slab": "60,001 to 75,000 GRT",
        "Min_GRT": 60001,
        "Max_GRT": 75000,
        "Traffic_Type": "Coastal",
        "Fixed_Rate": 949500.00,
        "Incremental_Rate": 10.56,
        "Unit": "Rs"
    },
    {
        "Port": "Paradip",
        "Slab": "Above 75,000 GRT",
        "Min_GRT": 75001,
        "Max_GRT": None,
        "Traffic_Type": "Foreign",
        "Fixed_Rate": 45025.50,
        "Incremental_Rate": 0.3575,
        "Unit": "USD"
    },
    {
        "Port": "Paradip",
        "Slab": "Above 75,000 GRT",
        "Min_GRT": 75001,
        "Max_GRT": None,
        "Traffic_Type": "Coastal",
        "Fixed_Rate": 1107900.00,
        "Incremental_Rate": 8.80,
        "Unit": "Rs"
    }
]

pilotage_data = pd.DataFrame(records)

print("\nPilotage & Towage rates:")
print(pilotage_data.to_string(index=False))

print("\nShape:")
print(pilotage_data.shape)

print("\nTraffic types:")
print(pilotage_data["Traffic_Type"].unique())

pilotage_data.to_parquet(output_file, index=False)

print("\nPilotage & Towage dataset saved successfully!")
print("Output:", output_file)