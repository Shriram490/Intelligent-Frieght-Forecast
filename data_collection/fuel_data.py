import pandas as pd

input_file = "../data/processed/commodity_prices.parquet"
output_file = "../data/processed/fuel_prices.parquet"

print("Reading commodity price data...")

# Read processed commodity dataset
data = pd.read_parquet(input_file)

# Crude oil series we want to keep
fuel_commodities = [
    "Crude oil, Brent",
    "Crude oil, Dubai",
    "Crude oil, WTI",
    "Crude oil, average"
]

# Filter fuel data
fuel_data = data[
    data["Commodity"].isin(fuel_commodities)
].copy()

# Sort chronologically
fuel_data = fuel_data.sort_values(
    ["Date", "Commodity"]
).reset_index(drop=True)

# ==========================================
# CHECK THE RESULT
# ==========================================

print("\nFuel data:")
print(fuel_data.head(20))

print("\nShape:")
print(fuel_data.shape)

print("\nData types:")
print(fuel_data.dtypes)

print("\nFuel commodities:")
print(fuel_data["Commodity"].unique())

print("\nDate range:")
print(
    fuel_data["Date"].min(),
    "to",
    fuel_data["Date"].max()
)

print("\nMissing values:")
print(fuel_data.isna().sum())

# Save processed fuel data
fuel_data.to_parquet(
    output_file,
    index=False
)

print("\nFuel data saved successfully!")
print("File:", output_file)