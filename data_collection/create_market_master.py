from pathlib import Path
import polars as pl


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

FREIGHT_FILE = PROCESSED_DIR / "freight_data.parquet"
COMMODITY_FILE = PROCESSED_DIR / "commodity_prices.parquet"
FUEL_FILE = PROCESSED_DIR / "fuel_prices.parquet"

OUTPUT_FILE = PROCESSED_DIR / "market_master.parquet"


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

print("Creating market master dataset...")
print("=" * 80)

print("\nLoading freight data...")
freight = pl.read_parquet(FREIGHT_FILE)

print("Loading commodity data...")
commodity = pl.read_parquet(COMMODITY_FILE)

print("Loading fuel data...")
fuel = pl.read_parquet(FUEL_FILE)


# ---------------------------------------------------------
# PREPARE FREIGHT DATA
# ---------------------------------------------------------

print("\nPreparing freight data...")

freight = (
    freight
    .sort("Date")
    .with_columns(
        pl.col("Date").dt.truncate("1mo").alias("Month")
    )
)

print(f"Freight rows: {freight.height}")


# ---------------------------------------------------------
# PREPARE COMMODITY DATA
# ---------------------------------------------------------

print("\nPreparing commodity data...")

commodity = (
    commodity
    .sort(["Date", "Commodity"])
    .with_columns(
        pl.col("Date").dt.truncate("1mo").alias("Month")
    )
)

print(f"Commodity rows: {commodity.height}")
print(f"Unique commodities: {commodity["Commodity"].n_unique()}")


# ---------------------------------------------------------
# PREPARE FUEL DATA
# ---------------------------------------------------------

print("\nPreparing fuel data...")

fuel = (
    fuel
    .sort(["Date", "Commodity"])
    .with_columns(
        pl.col("Date").dt.truncate("1mo").alias("Month")
    )
)

print(f"Fuel rows: {fuel.height}")


# ---------------------------------------------------------
# CREATE FUEL-WIDE TABLE
# ---------------------------------------------------------

print("\nCreating fuel price table...")

fuel_wide = (
    fuel
    .select(["Month", "Commodity", "Price"])
    .pivot(
        on="Commodity",
        index="Month",
        values="Price"
    )
    .rename({
        "Crude oil, Brent": "Crude_Oil_Brent",
        "Crude oil, Dubai": "Crude_Oil_Dubai",
        "Crude oil, average": "Crude_Oil_Average",
        "Crude oil, WTI": "Crude_Oil_WTI"
    })
)

print(f"Fuel table rows: {fuel_wide.height}")


# ---------------------------------------------------------
# JOIN FUEL TO FREIGHT
# ---------------------------------------------------------

print("\nJoining fuel prices to freight data...")

market = freight.join(
    fuel_wide,
    on="Month",
    how="left"
)


# ---------------------------------------------------------
# SELECT IMPORTANT COMMODITIES
# ---------------------------------------------------------

# These are kept as separate features for now.
# We can add/remove commodities later depending on
# the forecasting scenario.

selected_commodities = [
    "Coal, Australian",
    "Coal, South African **",
    "Iron ore, cfr spot"
]


commodity_selected = (
    commodity
    .filter(
        pl.col("Commodity").is_in(selected_commodities)
    )
    .select([
        "Month",
        "Commodity",
        "Price"
    ])
    .pivot(
        on="Commodity",
        index="Month",
        values="Price"
    )
)


# ---------------------------------------------------------
# RENAME COMMODITY COLUMNS
# ---------------------------------------------------------

rename_map = {
    "Coal, Australian": "Coal_Australian_Price",
    "Coal, South African **": "Coal_South_African_Price",
    "Iron ore, cfr spot": "Iron_Ore_Price"
}

commodity_selected = commodity_selected.rename(rename_map)


# ---------------------------------------------------------
# JOIN COMMODITY DATA
# ---------------------------------------------------------

print("\nJoining commodity prices...")

market = market.join(
    commodity_selected,
    on="Month",
    how="left"
)


# ---------------------------------------------------------
# CLEAN COLUMN ORDER
# ---------------------------------------------------------

market = market.select([
    "Date",
    "Month",
    "Price",
    "Open",
    "High",
    "Low",
    "Change %",
    "Crude_Oil_Brent",
    "Crude_Oil_Dubai",
    "Crude_Oil_Average",
    "Crude_Oil_WTI",
    "Coal_Australian_Price",
    "Coal_South_African_Price",
    "Iron_Ore_Price"
])


# ---------------------------------------------------------
# SORT
# ---------------------------------------------------------

market = market.sort("Date")


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

market.write_parquet(OUTPUT_FILE)


# ---------------------------------------------------------
# REPORT
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("MARKET MASTER DATASET CREATED")
print("=" * 80)

print(f"\nRows: {market.height}")
print(f"Columns: {market.width}")

print("\nColumns:")
print(market.columns)

print("\nDate range:")
print(f"From: {market["Date"].min()}")
print(f"To:   {market["Date"].max()}")

print("\nMissing values:")
print(market.null_count())

print("\nFirst 10 rows:")
print(market.head(10))

print("\nOutput:")
print(OUTPUT_FILE)