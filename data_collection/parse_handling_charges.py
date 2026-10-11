from pathlib import Path
import pandas as pd


output_file = Path("../data/processed/handling_charges.parquet")

print("Creating Paradip handling charge dataset...")


records = [

    # =========================
    # MCHP
    # =========================

    {
        "Port": "Paradip",
        "Charge_Category": "MCHP",
        "Charge_Name": "Unloading of coal wagon through coal handling system",
        "Commodity": "Coal/Coke",
        "Cargo_Type": "Dry Bulk",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 72.64,
        "Coastal_Rate": 72.64,
        "Conditions": ""
    },

    {
        "Port": "Paradip",
        "Charge_Category": "MCHP",
        "Charge_Name": "Shipment of coal through coal handling plant",
        "Commodity": "Coal/Coke",
        "Cargo_Type": "Dry Bulk",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": 7500000,
        "Unit": "Rs/MT",
        "Foreign_Rate": 108.90,
        "Coastal_Rate": 108.90,
        "Conditions": "Up to 7.5 million tonnes"
    },

    {
        "Port": "Paradip",
        "Charge_Category": "MCHP",
        "Charge_Name": "Shipment of coal through coal handling plant",
        "Commodity": "Coal/Coke",
        "Cargo_Type": "Dry Bulk",
        "Volume_Min_MT": 7500000,
        "Volume_Max_MT": 10000000,
        "Unit": "Rs/MT",
        "Foreign_Rate": 99.83,
        "Coastal_Rate": 99.83,
        "Conditions": "From 7.5 million tonnes to 10 million tonnes"
    },

    {
        "Port": "Paradip",
        "Charge_Category": "MCHP",
        "Charge_Name": "Shipment of coal through coal handling plant",
        "Commodity": "Coal/Coke",
        "Cargo_Type": "Dry Bulk",
        "Volume_Min_MT": 10000000,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 90.78,
        "Coastal_Rate": 90.78,
        "Conditions": "Above 10 million tonnes"
    },

    {
        "Port": "Paradip",
        "Charge_Category": "MCHP",
        "Charge_Name": "Shipment through coal handling plant",
        "Commodity": "Iron Ore/Pellet/Similar Dry Bulk",
        "Cargo_Type": "Dry Bulk",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 108.90,
        "Coastal_Rate": 108.90,
        "Conditions": "Iron ore fines, iron ore pellets and other similar dry bulk cargo"
    },

    {
        "Port": "Paradip",
        "Charge_Category": "MCHP",
        "Charge_Name": "Unloading of wagons at RRS of MCHP",
        "Commodity": "Iron Ore/Pellet/Similar Dry Bulk",
        "Cargo_Type": "Dry Bulk",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 72.64,
        "Coastal_Rate": 72.64,
        "Conditions": "Iron ore fines, iron ore pellets and other similar dry bulk cargo"
    },


    # =========================
    # IOHP
    # =========================

    {
        "Port": "Paradip",
        "Charge_Category": "IOHP",
        "Charge_Name": "Iron ore shipment",
        "Commodity": "Iron Ore/Pellet",
        "Cargo_Type": "Dry Bulk",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": 1000000,
        "Unit": "Rs/MT",
        "Foreign_Rate": 32.95,
        "Coastal_Rate": 32.95,
        "Conditions": "Shipment up to 1.0 MTPA"
    },

    {
        "Port": "Paradip",
        "Charge_Category": "IOHP",
        "Charge_Name": "Iron ore shipment",
        "Commodity": "Iron Ore/Pellet",
        "Cargo_Type": "Dry Bulk",
        "Volume_Min_MT": 1000000,
        "Volume_Max_MT": 1500000,
        "Unit": "Rs/MT",
        "Foreign_Rate": 28.19,
        "Coastal_Rate": 28.19,
        "Conditions": "Shipment between 1.0 and 1.5 MMTPA"
    },

    {
        "Port": "Paradip",
        "Charge_Category": "IOHP",
        "Charge_Name": "Iron ore shipment",
        "Commodity": "Iron Ore/Pellet",
        "Cargo_Type": "Dry Bulk",
        "Volume_Min_MT": 1500000,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 23.40,
        "Coastal_Rate": 23.40,
        "Conditions": "Shipment above 1.5 MTPA"
    },

    {
        "Port": "Paradip",
        "Charge_Category": "IOHP",
        "Charge_Name": "Tippling",
        "Commodity": "Iron Ore/Pellet",
        "Cargo_Type": "Dry Bulk",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 28.67,
        "Coastal_Rate": 28.67,
        "Conditions": ""
    },

    {
        "Port": "Paradip",
        "Charge_Category": "IOHP",
        "Charge_Name": "Thermal coal shipment",
        "Commodity": "Thermal Coal",
        "Cargo_Type": "Dry Bulk",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 69.55,
        "Coastal_Rate": 69.55,
        "Conditions": ""
    },

    {
        "Port": "Paradip",
        "Charge_Category": "IOHP",
        "Charge_Name": "Tippling",
        "Commodity": "Thermal Coal",
        "Cargo_Type": "Dry Bulk",
        "Volume_Min_MT": 0,
        "Volume_Max_MT": None,
        "Unit": "Rs/MT",
        "Foreign_Rate": 28.67,
        "Coastal_Rate": 28.67,
        "Conditions": ""
    }
]


# Create DataFrame
handling_data = pd.DataFrame(records)


print("\nHandling charge data:")
print(handling_data)

print("\nShape:")
print(handling_data.shape)

print("\nCharge categories:")
print(handling_data["Charge_Category"].unique())

print("\nCommodities:")
print(handling_data["Commodity"].unique())


# Save
handling_data.to_parquet(
    output_file,
    index=False
)

print("\nHandling charge dataset saved successfully!")
print("Output:", output_file)