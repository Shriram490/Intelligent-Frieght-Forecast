from pathlib import Path
import pandas as pd


BASE_DIR = Path("../data/processed")


FILES = {
    "commodity_prices": BASE_DIR / "commodity_prices.parquet",
    "fuel_prices": BASE_DIR / "fuel_prices.parquet",
    "freight_data": BASE_DIR / "freight_data.parquet",
}


def validate_dataset(name, file_path):

    print("\n" + "=" * 70)
    print(f"{name.upper()}")
    print("=" * 70)

    df = pd.read_parquet(file_path)

    # Basic information
    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(list(df.columns))

    # Date information
    df["Date"] = pd.to_datetime(df["Date"])

    print("\nDate range:")
    print("From:", df["Date"].min())
    print("To:", df["Date"].max())

    print("\nNumber of unique dates:")
    print(df["Date"].nunique())

    # Missing values
    print("\nMissing values:")
    print(df.isna().sum())

    # Duplicate rows
    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    # Duplicate dates
    duplicate_dates = df["Date"].duplicated().sum()

    print("\nDuplicate dates:")
    print(duplicate_dates)

    # Date gaps
    dates = df["Date"].drop_duplicates().sort_values()

    gaps = dates.diff().dropna()

    print("\nMost common date gaps:")
    print(gaps.value_counts().head(10))

    # Numeric columns
    numeric_columns = df.select_dtypes(include="number").columns

    print("\nZero values:")
    for column in numeric_columns:
        print(f"{column}: {(df[column] == 0).sum()}")

    # Commodity information
    if "Commodity" in df.columns:

        print("\nNumber of commodities:")
        print(df["Commodity"].nunique())

        print("\nCommodity list:")
        print(df["Commodity"].unique())

        print("\nRecords per commodity:")
        print(df["Commodity"].value_counts())

    # Statistics
    print("\nBasic statistics:")
    print(df[numeric_columns].describe())


print("Validating market datasets...")

for name, file_path in FILES.items():

    if not file_path.exists():

        print("\nFILE NOT FOUND:")
        print(file_path)

        continue

    validate_dataset(name, file_path)


print("\n" + "=" * 70)
print("MARKET DATA VALIDATION COMPLETE")
print("=" * 70)