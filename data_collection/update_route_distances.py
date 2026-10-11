import polars as pl
from pathlib import Path

print("Updating route distance reference...")
print("=" * 80)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ROUTE_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "route_reference.parquet"
)

# ============================================================
# LOAD ROUTE REFERENCE
# ============================================================

print("\nLoading route reference...")

df = pl.read_parquet(ROUTE_PATH)

print(f"Rows before update: {df.height}")

# ============================================================
# ROUTE DISTANCE REFERENCE
# ============================================================
#
# Values represent approximate ocean-route distances in
# nautical miles (NM).
#
# These are reference/estimated values, NOT historical
# measured voyage distances.
#
# They are intended for:
# - voyage duration estimation
# - fuel consumption estimation
# - voyage cost modelling
# - route comparison
#
# ============================================================

distance_map = {
    ("South Kalimantan", "Paradip"): 2200,
    ("South Kalimantan", "Dhamra"): 2250,
    ("South Kalimantan", "Visakhapatnam"): 2050,
    ("South Kalimantan", "Krishnapatnam"): 1900,

    ("Newcastle", "Paradip"): 3900,
    ("Newcastle", "Dhamra"): 3850,
    ("Newcastle", "Visakhapatnam"): 3600,
    ("Newcastle", "Krishnapatnam"): 3500,

    ("Hay Point", "Paradip"): 4100,

    ("South Africa", "Paradip"): 5600,
}

# ============================================================
# CREATE DISTANCE COLUMN
# ============================================================

distance_expr = None

for (origin, destination), distance in distance_map.items():

    condition = (
        (pl.col("Origin") == origin)
        & (pl.col("Destination") == destination)
    )

    if distance_expr is None:
        distance_expr = (
            pl.when(condition)
            .then(pl.lit(distance))
        )
    else:
        distance_expr = distance_expr.when(condition).then(
            pl.lit(distance)
        )

distance_expr = distance_expr.otherwise(None)

df = df.with_columns(
    distance_expr.cast(pl.Float64).alias("Typical_Distance_NM")
)

# ============================================================
# UPDATE DATA STATUS
# ============================================================

df = df.with_columns(
    pl.when(pl.col("Typical_Distance_NM").is_not_null())
    .then(pl.lit("Reference"))
    .otherwise(pl.lit("Missing"))
    .alias("Data_Status")
)

# ============================================================
# VALIDATION
# ============================================================

print("\nUpdated route reference:")

print(
    df.select(
        [
            "Origin",
            "Destination",
            "Typical_Distance_NM",
            "Data_Status",
        ]
    )
    .sort(["Origin", "Destination"])
)

print("\nMissing distance values:")

missing_distance = df.filter(
    pl.col("Typical_Distance_NM").is_null()
).height

print(missing_distance)

print("\nDistance statistics:")

print(
    df.select(
        [
            pl.col("Typical_Distance_NM")
            .min()
            .alias("Minimum_NM"),

            pl.col("Typical_Distance_NM")
            .max()
            .alias("Maximum_NM"),

            pl.col("Typical_Distance_NM")
            .mean()
            .round(2)
            .alias("Average_NM"),
        ]
    )
)

# ============================================================
# SAVE
# ============================================================

df.write_parquet(ROUTE_PATH)

print("\n" + "=" * 80)
print("ROUTE DISTANCE REFERENCE UPDATED")
print("=" * 80)

print(f"\nRows: {df.height}")
print(f"Columns: {df.width}")

print(f"\nOutput:")
print(ROUTE_PATH)