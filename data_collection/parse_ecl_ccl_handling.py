from pathlib import Path
import pandas as pd

output_file = Path(
    "../data/processed/ecl_ccl_handling_charges.parquet"
)

print("Creating Paradip ECL/CCL handling charges dataset...")

records = [
    # Section 4.17 A
    {
        "Port": "Paradip",
        "Section": "4.17 A",
        "Cargo_Type": "ECL/CCL",
        "Handling_Mode": (
            "Tippling in IOHP by N-Box wagon, "
            "shifting through IOHP-MCHP connectivity, "
            "loading through MCHP berth"
        ),
        "Unloading_Rate": 91.88,
        "Shipment_Rate": 108.90,
        "Existing_Total_Rate": 200.78,
        "Unloading_Discount": 63.55,
        "Shipment_Discount": 75.32,
        "Total_Discount": 138.87,
        "Final_Unloading_Rate": 28.33,
        "Final_Shipment_Rate": 33.59,
        "Final_Total_Rate": 61.92
    },
    {
        "Port": "Paradip",
        "Section": "4.17 A",
        "Cargo_Type": "ECL/CCL",
        "Handling_Mode": (
            "Unloading in RRS by BOBR wagon, "
            "then loading through MCHP berth"
        ),
        "Unloading_Rate": 72.64,
        "Shipment_Rate": 108.90,
        "Existing_Total_Rate": 181.54,
        "Unloading_Discount": 32.91,
        "Shipment_Discount": 49.35,
        "Total_Discount": 82.26,
        "Final_Unloading_Rate": 39.72,
        "Final_Shipment_Rate": 59.55,
        "Final_Total_Rate": 99.27
    },
    {
        "Port": "Paradip",
        "Section": "4.17 A",
        "Cargo_Type": "ECL/CCL",
        "Handling_Mode": (
            "Manual unloading of N-Box wagon, "
            "manual shifting to MCHP, "
            "loading through MCHP berth"
        ),
        "Unloading_Rate": 0.00,
        "Shipment_Rate": 108.90,
        "Existing_Total_Rate": 108.90,
        "Unloading_Discount": 0.00,
        "Shipment_Discount": 61.26,
        "Total_Discount": 61.26,
        "Final_Unloading_Rate": 0.00,
        "Final_Shipment_Rate": 47.65,
        "Final_Total_Rate": 47.65
    },

    # Section 4.17 B
    {
        "Port": "Paradip",
        "Section": "4.17 B",
        "Cargo_Type": "ECL/CCL",
        "Handling_Mode": (
            "Tippling in IOHP by N-Box wagon, "
            "then loading through IOHP berth"
        ),
        "Unloading_Rate": 28.67,
        "Shipment_Rate": 69.55,
        "Existing_Total_Rate": 98.21,
        "Unloading_Discount": 12.98,
        "Shipment_Discount": 31.50,
        "Total_Discount": 44.49,
        "Final_Unloading_Rate": 15.68,
        "Final_Shipment_Rate": 38.05,
        "Final_Total_Rate": 53.73
    },
    {
        "Port": "Paradip",
        "Section": "4.17 B",
        "Cargo_Type": "ECL/CCL",
        "Handling_Mode": (
            "Manual unloading of N-Box wagon, "
            "shifting to IOHP, "
            "loading through IOHP"
        ),
        "Unloading_Rate": 0.00,
        "Shipment_Rate": 69.55,
        "Existing_Total_Rate": 69.55,
        "Unloading_Discount": 0.00,
        "Shipment_Discount": 39.11,
        "Total_Discount": 39.11,
        "Final_Unloading_Rate": 0.00,
        "Final_Shipment_Rate": 30.44,
        "Final_Total_Rate": 30.44
    }
]

handling_data = pd.DataFrame(records)

print("\nECL/CCL handling charges:")
print(handling_data.to_string(index=False))

print("\nShape:")
print(handling_data.shape)

print("\nSections:")
print(handling_data["Section"].unique())

handling_data.to_parquet(output_file, index=False)

print("\nECL/CCL handling dataset saved successfully!")
print("Output:", output_file)