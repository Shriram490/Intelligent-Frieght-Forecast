import duckdb

file_path = "../data/processed/commodity_prices.parquet"

print("Reading Parquet file using DuckDB...")

result = duckdb.sql(f"""
    SELECT *
    FROM read_parquet('{file_path}')
    LIMIT 10
""")

print("\nFirst 10 rows:")
print(result)

print("\nTotal records:")

count = duckdb.sql(f"""
    SELECT COUNT(*)
    FROM read_parquet('{file_path}')
""")

print(count)