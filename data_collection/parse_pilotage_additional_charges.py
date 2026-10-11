from pathlib import Path
import pandas as pd

output_file = Path(
    "../data/processed/pilotage_additional_charges.parquet"
)

print("Creating Paradip additional Pilotage & Towage charges...")

records = [
    {
        "Port": "Paradip",
        "Charge_Category": "Cold Movement",
        "Traffic_Type": "Foreign",
        "Basis": "Percentage of Pilotage & Towage",
        "Unit": "%",
        "Rate": 25.0,
        "Conditions": "Pilotage and towage charges are 25% extra"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Cold Movement",
        "Traffic_Type": "Coastal",
        "Basis": "Percentage of Pilotage & Towage",
        "Unit": "%",
        "Rate": 25.0,
        "Conditions": "Pilotage and towage charges are 25% extra"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Convenience Shifting",
        "Traffic_Type": "Foreign",
        "Basis": "Percentage of Pilotage & Towage",
        "Unit": "%",
        "Rate": 50.0,
        "Conditions": "Applies when vessel is shifted/removed for own or another vessel's convenience"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Convenience Shifting",
        "Traffic_Type": "Coastal",
        "Basis": "Percentage of Pilotage & Towage",
        "Unit": "%",
        "Rate": 50.0,
        "Conditions": "Applies when vessel is shifted/removed for own or another vessel's convenience"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Pilot Cancellation",
        "Traffic_Type": "Foreign",
        "Basis": "Per cancellation",
        "Unit": "USD",
        "Rate": 147.52,
        "Conditions": "Cancellation less than 2 hours before scheduled time"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Pilot Cancellation",
        "Traffic_Type": "Coastal",
        "Basis": "Per cancellation",
        "Unit": "Rs",
        "Rate": 3628.15,
        "Conditions": "Cancellation less than 2 hours before scheduled time"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Pilot Detention",
        "Traffic_Type": "Foreign",
        "Basis": "Per hour after 30 minutes",
        "Unit": "USD/hour",
        "Rate": 147.52,
        "Conditions": "Vessel unable to move within 30 minutes of pilot boarding"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Pilot Detention",
        "Traffic_Type": "Coastal",
        "Basis": "Per hour after 30 minutes",
        "Unit": "Rs/hour",
        "Rate": 3628.15,
        "Conditions": "Vessel unable to move within 30 minutes of pilot boarding"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Movement Cancellation After Boarding",
        "Traffic_Type": "Foreign",
        "Basis": "Per cancellation",
        "Unit": "USD",
        "Rate": 295.09,
        "Conditions": "Movement cancelled after pilot has boarded"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Movement Cancellation After Boarding",
        "Traffic_Type": "Coastal",
        "Basis": "Per cancellation",
        "Unit": "Rs",
        "Rate": 7256.31,
        "Conditions": "Movement cancelled after pilot has boarded"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Pilot Detention Before Boarding",
        "Traffic_Type": "Foreign",
        "Basis": "Per hour after 30 minutes",
        "Unit": "USD/hour",
        "Rate": 147.52,
        "Conditions": "Pilot detained in pilot launch for more than 30 minutes before boarding"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Pilot Detention Before Boarding",
        "Traffic_Type": "Coastal",
        "Basis": "Per hour after 30 minutes",
        "Unit": "Rs/hour",
        "Rate": 3628.15,
        "Conditions": "Pilot detained in pilot launch for more than 30 minutes before boarding"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Warping",
        "Traffic_Type": "Foreign",
        "Basis": "Per operation",
        "Unit": "USD",
        "Rate": 737.69,
        "Conditions": "Warping for vessel convenience; no charge for port convenience"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Warping",
        "Traffic_Type": "Coastal",
        "Basis": "Per operation",
        "Unit": "Rs",
        "Rate": 18140.80,
        "Conditions": "Warping for vessel convenience; no charge for port convenience"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Yokohama Fender",
        "Traffic_Type": "Foreign",
        "Basis": "Per request",
        "Unit": "USD",
        "Rate": 442.63,
        "Conditions": "Fixing/removal or providing Yokohama Fender for double banking"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Yokohama Fender",
        "Traffic_Type": "Coastal",
        "Basis": "Per request",
        "Unit": "Rs",
        "Rate": 10884.47,
        "Conditions": "Fixing/removal or providing Yokohama Fender for double banking"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Sunday/Holiday Non-Movement",
        "Traffic_Type": "Foreign",
        "Basis": "Per planned movement",
        "Unit": "USD",
        "Rate": 590.17,
        "Conditions": "Movement planned for Sunday/Holiday but not carried out due to vessel-attributed reasons"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Sunday/Holiday Non-Movement",
        "Traffic_Type": "Coastal",
        "Basis": "Per planned movement",
        "Unit": "Rs",
        "Rate": 14512.64,
        "Conditions": "Movement planned for Sunday/Holiday but not carried out due to vessel-attributed reasons"
    }
]

additional_charges = pd.DataFrame(records)

print("\nAdditional Pilotage & Towage charges:")
print(additional_charges.to_string(index=False))

print("\nShape:")
print(additional_charges.shape)

print("\nCharge categories:")
print(additional_charges["Charge_Category"].unique())

additional_charges.to_parquet(
    output_file,
    index=False
)

print("\nAdditional charges dataset saved successfully!")
print("Output:", output_file)