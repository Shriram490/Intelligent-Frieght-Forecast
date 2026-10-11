from pathlib import Path
import pandas as pd


input_file = Path("../data/processed/wharfage_section.txt")
output_file = Path("../data/processed/wharfage_rates.parquet")


print("Reading wharfage section...")

text = input_file.read_text(encoding="utf-8")


# --------------------------------------------------
# Manually define the structured tariff rows
# based on the extracted tariff section.
# --------------------------------------------------

records = [

    # Coal / Coke
    {
        "Port": "Paradip",
        "Charge_Category": "Wharfage",
        "Commodity": "Coal/Coke",
        "Cargo_Type": "Dry Bulk",
        "Rate_Type": "Volume-based",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": 500000,
        "Unit": "Rs/MT",
        "Foreign_Rate": 60.43,
        "Coastal_Rate": 36.26,
        "Conditions": "Import up to 5 lakh tonnes per user per commodity per annum"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Wharfage",
        "Commodity": "Coal/Coke",
        "Cargo_Type": "Dry Bulk",
        "Rate_Type": "Volume-based",
        "Volume_Min_MT": 500000,
        "Volume_Max_MT": 750000,
        "Unit": "Rs/MT",
        "Foreign_Rate": 50.86,
        "Coastal_Rate": 30.49,
        "Conditions": "Import between 5 lakh and 7.5 lakh tonnes per user per commodity per annum"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Wharfage",
        "Commodity": "Coal/Coke",
        "Cargo_Type": "Dry Bulk",
        "Rate_Type": "Volume-based",
        "Volume_Min_MT": 750000,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 41.32,
        "Coastal_Rate": 24.81,
        "Conditions": "Import above 7.5 lakh tonnes per user per commodity per annum"
    },

    # Iron Ore
    {
        "Port": "Paradip",
        "Charge_Category": "Wharfage",
        "Commodity": "Iron Ore/Pellet/Magnetite Concentrate",
        "Cargo_Type": "Dry Bulk",
        "Rate_Type": "Flat",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 32.95,
        "Coastal_Rate": 32.95,
        "Conditions": "Iron ore, iron ore pellet and standard magnetite concentrate"
    },

    # Chrome Ore
    {
        "Port": "Paradip",
        "Charge_Category": "Wharfage",
        "Commodity": "Chrome Ore/Chrome Concentrate",
        "Cargo_Type": "Dry Bulk",
        "Rate_Type": "Flat",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 71.68,
        "Coastal_Rate": 42.99,
        "Conditions": ""
    },

    # Manganese Ore
    {
        "Port": "Paradip",
        "Charge_Category": "Wharfage",
        "Commodity": "Manganese Ore",
        "Cargo_Type": "Dry Bulk",
        "Rate_Type": "Flat",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 71.39,
        "Coastal_Rate": 42.86,
        "Conditions": ""
    },

    # Cement / Limestone etc.
    {
        "Port": "Paradip",
        "Charge_Category": "Wharfage",
        "Commodity": "Cement/Clinker/Limestone/Dolomite/Gypsum",
        "Cargo_Type": "Dry Bulk",
        "Rate_Type": "Volume-based",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": 200000,
        "Unit": "Rs/MT",
        "Foreign_Rate": 76.43,
        "Coastal_Rate": 45.89,
        "Conditions": "Up to 2 lakh tonnes per user per commodity"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Wharfage",
        "Commodity": "Cement/Clinker/Limestone/Dolomite/Gypsum",
        "Cargo_Type": "Dry Bulk",
        "Rate_Type": "Volume-based",
        "Volume_Min_MT": 200000,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 66.90,
        "Coastal_Rate": 40.11,
        "Conditions": "Above 2 lakh tonnes per user per commodity"
    },

    # Fertilizer
    {
        "Port": "Paradip",
        "Charge_Category": "Wharfage",
        "Commodity": "Finished Fertilizer/Ammonium Nitrate/FRM",
        "Cargo_Type": "Dry Bulk",
        "Rate_Type": "Flat",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 38.22,
        "Coastal_Rate": 22.91,
        "Conditions": ""
    },

    # Food grains
    {
        "Port": "Paradip",
        "Charge_Category": "Wharfage",
        "Commodity": "Food Grains/Oil Seeds/Cereals/Pulses",
        "Cargo_Type": "Dry Bulk",
        "Rate_Type": "Volume-based",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": 50000,
        "Unit": "Rs/MT",
        "Foreign_Rate": 95.55,
        "Coastal_Rate": 57.34,
        "Conditions": "Up to 50,000 MT per user per commodity"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Wharfage",
        "Commodity": "Food Grains/Oil Seeds/Cereals/Pulses",
        "Cargo_Type": "Dry Bulk",
        "Rate_Type": "Volume-based",
        "Volume_Min_MT": 50000,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 57.34,
        "Coastal_Rate": 34.42,
        "Conditions": "Above 50,000 MT per user per commodity"
    },

    # Rice / Sugar
    {
        "Port": "Paradip",
        "Charge_Category": "Wharfage",
        "Commodity": "Rice/Sugar",
        "Cargo_Type": "Dry Bulk",
        "Rate_Type": "Flat",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 28.67,
        "Coastal_Rate": 17.21,
        "Conditions": "In bulk"
    },

    # Salt
    {
        "Port": "Paradip",
        "Charge_Category": "Wharfage",
        "Commodity": "Salt",
        "Cargo_Type": "Dry Bulk",
        "Rate_Type": "Flat",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 9.55,
        "Coastal_Rate": 5.76,
        "Conditions": ""
    }
]


# --------------------------------------------------
# Convert to DataFrame
# --------------------------------------------------

wharfage_data = pd.DataFrame(records)


print("\nParsed Wharfage Data:")
print(wharfage_data)


print("\nShape:")
print(wharfage_data.shape)


print("\nCommodities:")
print(wharfage_data["Commodity"].unique())


# --------------------------------------------------
# Save
# --------------------------------------------------

wharfage_data.to_parquet(
    output_file,
    index=False
)


print("\nWharfage data saved successfully!")
print("Output:", output_file)