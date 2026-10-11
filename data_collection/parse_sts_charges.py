import pandas as pd


print("Creating Paradip STS operation charges dataset...")


data = [
    {
        "Port": "Paradip",
        "Operation_Type": "STS Operation",
        "Operation_Slab": "0-4",
        "Location": "Notified Water Spread Area",
        "USD_Rate": 10240.13,
        "INR_Rate": 852900.05
    },
    {
        "Port": "Paradip",
        "Operation_Type": "STS Operation",
        "Operation_Slab": "0-4",
        "Location": "NOJ",
        "USD_Rate": 12288.36,
        "INR_Rate": 1023480.66
    },
    {
        "Port": "Paradip",
        "Operation_Type": "STS Operation",
        "Operation_Slab": "5-9",
        "Location": "Notified Water Spread Area",
        "USD_Rate": 8191.90,
        "INR_Rate": 682320.44
    },
    {
        "Port": "Paradip",
        "Operation_Type": "STS Operation",
        "Operation_Slab": "5-9",
        "Location": "NOJ",
        "USD_Rate": 9830.49,
        "INR_Rate": 818784.73
    },
    {
        "Port": "Paradip",
        "Operation_Type": "STS Operation",
        "Operation_Slab": "10+",
        "Location": "Notified Water Spread Area",
        "USD_Rate": 6143.68,
        "INR_Rate": 511739.83
    },
    {
        "Port": "Paradip",
        "Operation_Type": "STS Operation",
        "Operation_Slab": "10+",
        "Location": "NOJ",
        "USD_Rate": 7372.61,
        "INR_Rate": 614088.80
    }
]


df = pd.DataFrame(data)


print("\nSTS charges:")
print(df)

print("\nShape:")
print(df.shape)


output_file = "../data/processed/sts_operation_charges.parquet"

df.to_parquet(output_file, index=False)

print("\nSTS charges dataset saved successfully!")
print("Output:", output_file)