import pandas as pd

file_path = "../data/raw/CMO-Historical-Data-Monthly.xlsx"

print("Reading Monthly Prices sheet...")

# Read Excel without assuming a header
raw_data = pd.read_excel(
    file_path,
    sheet_name="Monthly Prices",
    header=None
)

# Commodity names
# commodity_names = raw_data.iloc[4].tolist()

# Show commodity names from the workbook
commodity_names = raw_data.iloc[4].tolist()
commodity_names[0] = "Date"

print("\nAvailable commodities:")
for commodity in commodity_names:
    print(commodity)
# Units
units = raw_data.iloc[5].tolist()

# Actual monthly data
data = raw_data.iloc[6:].copy()

# Assign commodity names
data.columns = commodity_names

# Rename first column to Date
# data = data.rename(columns={data.columns[0]: "Date"})


# ==========================================
# CONVERT TO CLEAN LONG FORMAT
# ==========================================

# Convert dates to proper datetime format
data["Date"] = pd.to_datetime(
    data["Date"].astype(str),
    format="%YM%m"
)

# Convert wide format to long format
commodity_data = data.melt(
    id_vars=["Date"],
    var_name="Commodity",
    value_name="Price"
)

# Convert prices to numeric
commodity_data["Price"] = pd.to_numeric(
    commodity_data["Price"],
    errors="coerce"
)

# Remove rows where price is missing
commodity_data = commodity_data.dropna(subset=["Price"])

# Sort the dataset
commodity_data = commodity_data.sort_values(
    ["Date", "Commodity"]
).reset_index(drop=True)


# ==========================================
# CHECK THE RESULT
# ==========================================

print("\nLong-format data:")
print(commodity_data.head(20))

print("\nShape:")
print(commodity_data.shape)

print("\nData types:")
print(commodity_data.dtypes)

print("\nCommodities:")
print(commodity_data["Commodity"].unique())

# Save processed data
output_file = "../data/processed/commodity_prices.parquet"

commodity_data.to_parquet(
    output_file,
    index=False
)

print("\nProcessed data saved successfully!")
print("File:", output_file)