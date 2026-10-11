from pathlib import Path
import pandas as pd


output_file = Path("../data/processed/vessel_port_charges.parquet")

print("Creating Paradip vessel port charge dataset...")


records = [

    # =========================
    # BERTH HIRE
    # =========================

    {
        "Port": "Paradip",
        "Charge_Category": "Berth Hire",
        "Traffic_Type": "Foreign",
        "Basis": "GT per hour",
        "Unit": "USD/GT/hour",
        "Rate": 0.003338,
        "Conditions": "Foreign-going vessels"
    },

    {
        "Port": "Paradip",
        "Charge_Category": "Berth Hire",
        "Traffic_Type": "Coastal",
        "Basis": "GT per hour",
        "Unit": "Rs/GT/hour",
        "Rate": 0.082,
        "Conditions": "Coastal vessels"
    },


    # =========================
    # ROADSTEAD CHARGE
    # =========================

    {
        "Port": "Paradip",
        "Charge_Category": "Roadstead",
        "Traffic_Type": "Foreign",
        "Basis": "Per hour",
        "Unit": "USD/hour",
        "Rate": 6.15,
        "Conditions": "Vessels at berth in roadstead within port water limits"
    },

    {
        "Port": "Paradip",
        "Charge_Category": "Roadstead",
        "Traffic_Type": "Coastal",
        "Basis": "Per hour",
        "Unit": "Rs/hour",
        "Rate": 151.16,
        "Conditions": "Vessels at berth in roadstead within port water limits"
    },


    # =========================
    # PORT DUES
    # =========================

    {
        "Port": "Paradip",
        "Charge_Category": "Port Dues",
        "Traffic_Type": "Foreign",
        "Basis": "GRT per entry",
        "Unit": "USD/GRT/entry",
        "Rate": 0.34,
        "Conditions": "Foreign-going vessels"
    },

    {
        "Port": "Paradip",
        "Charge_Category": "Port Dues",
        "Traffic_Type": "Coastal",
        "Basis": "GRT per entry",
        "Unit": "Rs/GRT/entry",
        "Rate": 8.36,
        "Conditions": "Coastal vessels"
    }
]


vessel_charges = pd.DataFrame(records)


print("\nVessel port charges:")
print(vessel_charges)


print("\nShape:")
print(vessel_charges.shape)


print("\nCharge categories:")
print(vessel_charges["Charge_Category"].unique())


print("\nTraffic types:")
print(vessel_charges["Traffic_Type"].unique())


# Save
vessel_charges.to_parquet(
    output_file,
    index=False
)


print("\nVessel port charge dataset saved successfully!")
print("Output:", output_file)