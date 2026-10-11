import pandas as pd


print("Creating Paradip barge facilitation charge dataset...")


data = [
    {
        "Port": "Paradip",
        "Charge_Category": "Barge Loading Facilitation",
        "Location": "IFFCO Pontoon Jetty",
        "Basis": "Per Tonne",
        "Unit": "Rs/MT",
        "Rate": 2.04,
        "Applicable_To": "Loading of barge"
    }
]


df = pd.DataFrame(data)


print("\nBarge facilitation charges:")
print(df)

print("\nShape:")
print(df.shape)


output_file = "../data/processed/barge_facilitation_charges.parquet"

df.to_parquet(output_file, index=False)

print("\nBarge facilitation dataset saved successfully!")
print("Output:", output_file)