import polars as pl
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


print("Creating route market dataset...")
print("=" * 80)


# ============================================================
# LOAD DATASETS
# ============================================================

print("\nLoading market master...")
market = pl.read_parquet(
    PROCESSED_DIR / "market_master.parquet"
)

print(f"Market rows: {market.height}")


print("\nLoading route reference...")
routes = pl.read_parquet(
    PROCESSED_DIR / "route_reference.parquet"
)

print(f"Route rows: {routes.height}")


print("\nLoading vessel reference...")
vessels = pl.read_parquet(
    PROCESSED_DIR / "vessel_reference.parquet"
)

print(f"Vessel rows: {vessels.height}")


# ============================================================
# PREPARE MARKET DATA
# ============================================================

print("\nPreparing market data...")

market = market.select([
    "Date",
    "Month",
    "Price",
    "Crude_Oil_Brent",
    "Crude_Oil_Dubai",
    "Crude_Oil_Average",
    "Crude_Oil_WTI",
    "Coal_Australian_Price",
    "Coal_South_African_Price",
    "Iron_Ore_Price"
])


market = market.rename({
    "Price": "Freight_Rate"
})


# ============================================================
# PREPARE ROUTES
# ============================================================

print("Preparing routes...")

routes = routes.select([
    "Origin",
    "Origin_Country",
    "Destination",
    "Destination_Country",
    "Region",
    "Typical_Distance_NM",
    "Primary_Vessel_Types"
])


# ============================================================
# EXPAND ROUTES BY VESSEL TYPE
# ============================================================

print("Expanding routes by vessel type...")

route_rows = []

for row in routes.iter_rows(named=True):

    vessel_types = [
        v.strip()
        for v in row["Primary_Vessel_Types"].split(",")
    ]

    for vessel_type in vessel_types:

        route_rows.append({
            "Origin": row["Origin"],
            "Origin_Country": row["Origin_Country"],
            "Destination": row["Destination"],
            "Destination_Country": row["Destination_Country"],
            "Region": row["Region"],
            "Typical_Distance_NM": row["Typical_Distance_NM"],
            "Vessel_Type": vessel_type
        })


route_vessels = pl.DataFrame(route_rows)

print(f"Route-vessel combinations: {route_vessels.height}")


# ============================================================
# JOIN VESSEL CHARACTERISTICS
# ============================================================

print("Joining vessel characteristics...")

route_vessels = route_vessels.join(
    vessels,
    on="Vessel_Type",
    how="left"
)


# ============================================================
# CREATE DATE × ROUTE × VESSEL DATASET
# ============================================================

print("\nCreating date × route × vessel combinations...")

market = market.with_columns(
    pl.lit(1).alias("_join_key")
)

route_vessels = route_vessels.with_columns(
    pl.lit(1).alias("_join_key")
)


route_market = market.join(
    route_vessels,
    on="_join_key",
    how="inner"
).drop("_join_key")


# ============================================================
# SELECT FINAL COLUMNS
# ============================================================

route_market = route_market.select([
    "Date",
    "Month",

    "Origin",
    "Origin_Country",

    "Destination",
    "Destination_Country",
    "Region",

    "Vessel_Type",

    "Typical_DWT_Min",
    "Typical_DWT_Max",
    "Average_Speed_Knots",
    "Fuel_Consumption_MT_Day",
    "Typical_Cargo_MT",

    "Typical_Distance_NM",

    "Freight_Rate",

    "Crude_Oil_Brent",
    "Crude_Oil_Dubai",
    "Crude_Oil_Average",
    "Crude_Oil_WTI",

    "Coal_Australian_Price",
    "Coal_South_African_Price",
    "Iron_Ore_Price"
])


# ============================================================
# SORT
# ============================================================

route_market = route_market.sort([
    "Date",
    "Origin",
    "Destination",
    "Vessel_Type"
])


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("ROUTE MARKET DATASET CREATED")
print("=" * 80)

print(f"\nRows: {route_market.height}")
print(f"Columns: {route_market.width}")

print("\nColumns:")
print(route_market.columns)

print("\nDate range:")
print(f"From: {route_market['Date'].min()}")
print(f"To:   {route_market['Date'].max()}")

print("\nUnique origins:")
print(route_market["Origin"].unique())

print("\nUnique destinations:")
print(route_market["Destination"].unique())

print("\nUnique vessel types:")
print(route_market["Vessel_Type"].unique())

print("\nMissing values:")
print(
    route_market.null_count()
)

print("\nFirst 10 rows:")
print(
    route_market.head(10)
)


# ============================================================
# SAVE
# ============================================================

output_path = PROCESSED_DIR / "route_market_dataset.parquet"

route_market.write_parquet(
    output_path,
    compression="zstd"
)

print("\n" + "=" * 80)
print("ROUTE MARKET DATASET SAVED")
print("=" * 80)

print(f"\nOutput:")
print(output_path)