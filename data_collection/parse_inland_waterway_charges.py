import pandas as pd


print("Creating Paradip inland waterway charges dataset...")


data = [
    {
        "Port": "Paradip",
        "Charge_Category": "VRC and Wharfage",
        "Basis": "Per Tonne",
        "Unit": "Rs/MT",
        "Rate": 12.72,
        "Transport_Mode": "Inland Waterways",
        "Applicable_To": "Movement of cargo inland/vessel/river-sea vessel"
    }
]


df = pd.DataFrame(data)


print("\nInland waterway charges:")
print(df)

print("\nShape:")
print(df.shape)


output_file = "../data/processed/inland_waterway_charges.parquet"

df.to_parquet(output_file, index=False)

print("\nInland waterway charges dataset saved successfully!")
print("Output:", output_file)