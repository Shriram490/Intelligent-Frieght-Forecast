import polars as pl


# =============================================================================
# FREIGHT DATA ANALYSIS
# =============================================================================

print("=" * 80)
print("FREIGHT DATA ANALYSIS")
print("=" * 80)


# =============================================================================
# 1. READ FEATURE DATASET
# =============================================================================

print("\nReading freight feature dataset...")

file_path = "../data/processed/freight_features.parquet"

df = pl.read_parquet(file_path)

print(f"Shape: {df.shape}")


# =============================================================================
# 2. BASIC INFORMATION
# =============================================================================

print("\n" + "=" * 80)
print("1. BASIC INFORMATION")
print("=" * 80)

print(f"Total records: {df.height}")
print(f"Total columns: {df.width}")

print("\nColumns:")
for column in df.columns:
    print(f"- {column}")


# =============================================================================
# 3. DATE RANGE
# =============================================================================

print("\n" + "=" * 80)
print("2. DATE RANGE")
print("=" * 80)

first_date = df["Date"].min()
last_date = df["Date"].max()

print(f"First date: {first_date}")
print(f"Last date:  {last_date}")


# =============================================================================
# 4. PRICE STATISTICS
# =============================================================================

print("\n" + "=" * 80)
print("3. PRICE STATISTICS")
print("=" * 80)

price_stats = df.select(
    [
        pl.col("Price").count().alias("Count"),
        pl.col("Price").mean().alias("Mean"),
        pl.col("Price").median().alias("Median"),
        pl.col("Price").std().alias("Std Dev"),
        pl.col("Price").min().alias("Minimum"),
        pl.col("Price").max().alias("Maximum"),
    ]
)

print(price_stats)


# =============================================================================
# 5. PRICE QUANTILES
# =============================================================================

print("\n" + "=" * 80)
print("4. PRICE DISTRIBUTION")
print("=" * 80)

quantiles = df.select(
    [
        pl.col("Price").quantile(0.25).alias("25%"),
        pl.col("Price").quantile(0.50).alias("50%"),
        pl.col("Price").quantile(0.75).alias("75%"),
        pl.col("Price").quantile(0.90).alias("90%"),
        pl.col("Price").quantile(0.95).alias("95%"),
    ]
)

print(quantiles)


# =============================================================================
# 6. VOLATILITY ANALYSIS
# =============================================================================

print("\n" + "=" * 80)
print("5. VOLATILITY ANALYSIS")
print("=" * 80)

volatility_stats = df.select(
    [
        pl.col("Volatility_7").mean().alias("Average 7-Day Volatility"),
        pl.col("Volatility_7").max().alias("Maximum 7-Day Volatility"),
        pl.col("Volatility_30").mean().alias("Average 30-Day Volatility"),
        pl.col("Volatility_30").max().alias("Maximum 30-Day Volatility"),
    ]
)

print(volatility_stats)


# =============================================================================
# 7. MOMENTUM ANALYSIS
# =============================================================================

print("\n" + "=" * 80)
print("6. PRICE MOMENTUM")
print("=" * 80)

momentum_stats = df.select(
    [
        pl.col("Price_Change_7").mean().alias("Average 7-Day Change"),
        pl.col("Price_Change_7").min().alias("Minimum 7-Day Change"),
        pl.col("Price_Change_7").max().alias("Maximum 7-Day Change"),
        pl.col("Price_Change_30").mean().alias("Average 30-Day Change"),
        pl.col("Price_Change_30").min().alias("Minimum 30-Day Change"),
        pl.col("Price_Change_30").max().alias("Maximum 30-Day Change"),
    ]
)

print(momentum_stats)


# =============================================================================
# 8. YEARLY PRICE ANALYSIS
# =============================================================================

print("\n" + "=" * 80)
print("7. YEARLY PRICE ANALYSIS")
print("=" * 80)

yearly_stats = (
    df.group_by("Year")
    .agg(
        [
            pl.col("Price").mean().alias("Average Price"),
            pl.col("Price").min().alias("Minimum Price"),
            pl.col("Price").max().alias("Maximum Price"),
            pl.col("Price").std().alias("Price Std Dev"),
        ]
    )
    .sort("Year")
)

print(yearly_stats)


# =============================================================================
# 9. MONTHLY PRICE ANALYSIS
# =============================================================================

print("\n" + "=" * 80)
print("8. MONTHLY PRICE ANALYSIS")
print("=" * 80)

monthly_stats = (
    df.group_by("Month")
    .agg(
        [
            pl.col("Price").mean().alias("Average Price"),
            pl.col("Price").min().alias("Minimum Price"),
            pl.col("Price").max().alias("Maximum Price"),
        ]
    )
    .sort("Month")
)

print(monthly_stats)


# =============================================================================
# 10. HIGHEST PRICE PERIODS
# =============================================================================

print("\n" + "=" * 80)
print("9. TOP 10 HIGHEST FREIGHT PRICE RECORDS")
print("=" * 80)

highest_prices = (
    df.select(["Date", "Price", "Change %"])
    .sort("Price", descending=True)
    .head(10)
)

print(highest_prices)


# =============================================================================
# 11. LOWEST PRICE PERIODS
# =============================================================================

print("\n" + "=" * 80)
print("10. TOP 10 LOWEST FREIGHT PRICE RECORDS")
print("=" * 80)

lowest_prices = (
    df.select(["Date", "Price", "Change %"])
    .sort("Price")
    .head(10)
)

print(lowest_prices)


# =============================================================================
# 12. EXTREME PRICE MOVEMENTS
# =============================================================================

print("\n" + "=" * 80)
print("11. EXTREME PRICE MOVEMENTS")
print("=" * 80)

extreme_movements = df.filter(
    pl.col("Change %").abs() > 10
)

print(f"Extreme movements (> ±10%): {extreme_movements.height}")

print("\nLargest movements:")

print(
    extreme_movements
    .select(["Date", "Price", "Change %"])
    .sort("Change %", descending=True)
    .head(10)
)


# =============================================================================
# 13. MOVING AVERAGE COMPARISON
# =============================================================================

print("\n" + "=" * 80)
print("12. MOVING AVERAGE ANALYSIS")
print("=" * 80)

latest = df.tail(1).select(
    [
        "Date",
        "Price",
        "Price_MA_7",
        "Price_MA_30",
        "Price_MA_90",
    ]
)

print("Latest price compared with moving averages:")

print(latest)


# =============================================================================
# 14. LAG COMPARISON
# =============================================================================

print("\n" + "=" * 80)
print("13. LAG FEATURE ANALYSIS")
print("=" * 80)

lag_analysis = df.tail(10).select(
    [
        "Date",
        "Price",
        "Price_Lag_1",
        "Price_Lag_7",
        "Price_Lag_30",
    ]
)

print(lag_analysis)


# =============================================================================
# 15. FEATURE CORRELATION WITH PRICE
# =============================================================================

print("\n" + "=" * 80)
print("14. FEATURE CORRELATION WITH PRICE")
print("=" * 80)

numeric_columns = [
    "Price",
    "Open",
    "High",
    "Low",
    "Change %",
    "Year",
    "Month",
    "Quarter",
    "Day_of_Week",
    "Price_Lag_1",
    "Price_Lag_7",
    "Price_Lag_30",
    "Price_MA_7",
    "Price_MA_30",
    "Price_MA_90",
    "Volatility_7",
    "Volatility_30",
    "Price_Change_7",
    "Price_Change_30",
    "Price_Range",
    "Price_Range_Pct",
]

correlations = []

for column in numeric_columns:
    if column != "Price":
        correlation = df.select(
            pl.corr("Price", column)
        ).item()

        correlations.append(
            {
                "Feature": column,
                "Correlation_with_Price": correlation,
            }
        )

correlation_df = pl.DataFrame(correlations).sort(
    "Correlation_with_Price",
    descending=True,
)

print(correlation_df)


# =============================================================================
# 16. MISSING VALUES IN ENGINEERED FEATURES
# =============================================================================

print("\n" + "=" * 80)
print("15. MISSING VALUES IN FEATURES")
print("=" * 80)

missing_values = df.null_count()

print(missing_values)


# =============================================================================
# 17. FINAL SUMMARY
# =============================================================================

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)

print(f"\nDataset records: {df.height}")
print(f"Dataset features: {df.width}")
print(f"Date range: {first_date} → {last_date}")

print("\nNext step:")
print("Use the analysis results to prepare the dataset for")
print("forecasting model training.")

print("=" * 80)