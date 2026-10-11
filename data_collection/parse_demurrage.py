from pathlib import Path
import pandas as pd


output_file = Path("../data/processed/demurrage_charges.parquet")

print("Creating Paradip demurrage dataset...")


records = [
    {
        "Port": "Paradip",
        "Charge_Category": "Demurrage",
        "Cargo_Type": "Dry Bulk",
        "Traffic_Type": "Import",
        "Period": "1st week",
        "Min_Days": 1,
        "Max_Days": 7,
        "Unit": "Rs/MT/day",
        "Rate": 4.77,
        "Conditions": "Goods left lying in transit shed or open transit space beyond free period"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Demurrage",
        "Cargo_Type": "Dry Bulk",
        "Traffic_Type": "Import",
        "Period": "2nd week",
        "Min_Days": 8,
        "Max_Days": 14,
        "Unit": "Rs/MT/day",
        "Rate": 14.32,
        "Conditions": "Goods left lying in transit shed or open transit space beyond free period"
    },
    {
        "Port": "Paradip",
        "Charge_Category": "Demurrage",
        "Cargo_Type": "Dry Bulk",
        "Traffic_Type": "Import",
        "Period": "3rd week onwards",
        "Min_Days": 15,
        "Max_Days": None,
        "Unit": "Rs/MT/day",
        "Rate": 23.88,
        "Conditions": "Goods left lying in transit shed or open transit space beyond free period"
    }
]


demurrage_data = pd.DataFrame(records)


print("\nDemurrage data:")
print(demurrage_data)


print("\nShape:")
print(demurrage_data.shape)


print("\nPeriods:")
print(demurrage_data["Period"].tolist())


print("\nRates:")
print(demurrage_data["Rate"].tolist())


demurrage_data.to_parquet(
    output_file,
    index=False
)


print("\nDemurrage dataset saved successfully!")
print("Output:", output_file)