import pandas as pd

file_path = "../data/raw/BalticDryIndexHistoricalData.csv"

print("Reading Baltic Dry Index data...")

# Read CSV
data = pd.read_csv(file_path)

# Remove unnecessary volume column
data = data.drop(columns=["Vol."])

# Convert Date
data["Date"] = pd.to_datetime(
    data["Date"],
    format="%m/%d/%Y"
)

# Convert numerical columns
numeric_columns = ["Price", "Open", "High", "Low"]

for column in numeric_columns:
    data[column] = (
        data[column]
        .astype(str)
        .str.replace(",", "", regex=False)
    )

    data[column] = pd.to_numeric(
        data[column],
        errors="coerce"
    )

# Convert percentage change
data["Change %"] = (
    data["Change %"]
    .astype(str)
    .str.replace("%", "", regex=False)
)

data["Change %"] = pd.to_numeric(
    data["Change %"],
    errors="coerce"
)

# Sort chronologically
data = data.sort_values("Date").reset_index(drop=True)

print("\nProcessed data:")
print(data.head(10))

print("\nShape:")
print(data.shape)

print("\nData types:")
print(data.dtypes)

print("\nDate range:")
print(data["Date"].min(), "to", data["Date"].max())

# Save processed dataset
output_file = "../data/processed/freight_data.parquet"

data.to_parquet(
    output_file,
    index=False
)

print("\nFreight data saved successfully!")
print("File:", output_file)