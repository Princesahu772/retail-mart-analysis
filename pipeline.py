import pandas as pd
import numpy as np
import sqlite3

BASE = r'D:\Retail Mart Sales Analysis' # here we enter the location and name of the folder you are required to change it with your folder

# Task 1: Data Ingestion
print("=" * 60)
print("TASK 1: DATA INGESTION")
print("=" * 60)

sales = pd.read_csv(f'{BASE}\\sales_data.csv')
products = pd.read_csv(f'{BASE}\\product.csv')
stores = pd.read_csv(f'{BASE}\\stores.csv')

# 1. Loaded DataFrames - Shapes & First 5 rows
print("\n1. Loaded DataFrames - Shapes & First 5 rows:")
print("\n--- sales_data.csv ---")
print(f"Shape: {sales.shape}")
print(sales.head())
print("\n--- products.csv ---")
print(f"Shape: {products.shape}")
print(products.head())
print("\n--- stores.csv ---")
print(f"Shape: {stores.shape}")
print(stores.head())

# 2. Check for missing values
print("\n2. Missing Values Summary:")
print("\n--- sales_data ---")
print(sales.isnull().sum())
print("\n--- products ---")
print(products.isnull().sum())
print("\n--- stores ---")
print(stores.isnull().sum())

# Task 2: Data Cleaning
print("\n" + "=" * 60)
print("TASK 2: DATA CLEANING")
print("=" * 60)

# 3. Remove duplicate rows
dup_count = sales.duplicated().sum()
sales_clean = sales.drop_duplicates().copy()
print(f"\n3. Duplicates found and removed: {dup_count}")

# 4. Fill missing quantity with 0, drop rows where amount is NULL
sales_clean['quantity'] = pd.to_numeric(sales_clean['quantity'], errors='coerce')
sales_clean['amount'] = pd.to_numeric(sales_clean['amount'], errors='coerce')
sales_clean['quantity'] = sales_clean['quantity'].fillna(0).astype(int)
sales_clean = sales_clean.dropna(subset=['amount'])
print(f"4. Cleaned DataFrame shape after filling quantity & dropping null amount: {sales_clean.shape}")

# 5. Convert data types
sales_clean['sale_date'] = pd.to_datetime(sales_clean['sale_date'], format='mixed', dayfirst=True, errors='coerce')
sales_clean['amount'] = sales_clean['amount'].astype(float)
sales_clean['product_id'] = sales_clean['product_id'].astype(str)
print("5. Converted sale_date to datetime, amount to float, and standardized dtypes")

# Task 3: Data Transformation
print("\n" + "=" * 60)
print("TASK 3: DATA TRANSFORMATION")
print("=" * 60)

# 6. Merge DataFrames
products['product_id'] = products['product_id'].astype(str)
merged = sales_clean.merge(products, on='product_id', how='left').merge(stores, on='store_id', how='left')
print("\n6. Final Merged DataFrame:")
print(merged)

# 7. Add total_revenue column
merged['total_revenue'] = merged['quantity'] * merged['price']
rev_stats = merged['total_revenue'].dropna()
print(f"\n7. Total Revenue stats (using NumPy):")
print(f"   Mean: {np.mean(rev_stats):.2f}")
print(f"   Max:  {np.max(rev_stats):.2f}")
print(f"   Min:  {np.min(rev_stats):.2f}")

# 8. Group by city
city_revenue = merged.groupby('city')['total_revenue'].sum().sort_values(ascending=False)
print("\n8. Total Revenue per City (sorted descending):")
print(city_revenue.to_string())

# Task 4: Data Loading (SQL)
print("\n" + "=" * 60)
print("TASK 4: DATA LOADING (SQL)")
print("=" * 60)

# 9. Load into SQLite
conn = sqlite3.connect(f'{BASE}\\retail_mart.db')
merged.to_sql('retail_sales', conn, if_exists='replace', index=False)
print("\n9. Data loaded into SQLite database -> table 'retail_sales'")

# 10. Top 3 best-selling products
query_top3 = """
SELECT product_name, SUM(quantity) as total_qty_sold
FROM retail_sales
GROUP BY product_name
ORDER BY total_qty_sold DESC
LIMIT 3
"""
top3 = pd.read_sql(query_top3, conn)
print("\n10. Top 3 Best-Selling Products by Quantity:")
print(top3.to_string(index=False))

# Task 5: Reporting & Insights
print("\n" + "=" * 60)
print("TASK 5: REPORTING & INSIGHTS")
print("=" * 60)

# 11. Revenue per store per day
query_rev_per_store = """
SELECT store_id, store_name, sale_date, SUM(total_revenue) as revenue
FROM retail_sales
GROUP BY store_id, store_name, sale_date
ORDER BY store_id, sale_date
"""
rev_per_store = pd.read_sql(query_rev_per_store, conn)
print("\n11. Total Revenue per Store per Day:")
print(rev_per_store.to_string(index=False))

# 12. Summary report
print("\n12. Summary Report:")
print(f"   Total number of transactions: {len(merged)}")
print(f"   Total revenue: {merged['total_revenue'].sum():.2f}")
top_city = city_revenue.index[0]
print(f"   Top selling city: {top_city}")
top_prod_rev = merged.groupby('product_name')['total_revenue'].sum()
top_product = top_prod_rev.idxmax()
print(f"   Top selling product: {top_product}")

conn.close()

# Task 6: Pipeline & Error Handling
print("\n" + "=" * 60)
print("TASK 6: PIPELINE & ERROR HANDLING")
print("=" * 60)


def run_pipeline(sales_path, products_path, stores_path, db_path):
    try:
        print("\n--- Pipeline Started ---")

        sales = pd.read_csv(sales_path)
        products = pd.read_csv(products_path)
        stores = pd.read_csv(stores_path)

        dup_count = sales.duplicated().sum()
        sales_clean = sales.drop_duplicates().copy()

        sales_clean['quantity'] = pd.to_numeric(sales_clean['quantity'], errors='coerce')
        sales_clean['amount'] = pd.to_numeric(sales_clean['amount'], errors='coerce')
        sales_clean['quantity'] = sales_clean['quantity'].fillna(0).astype(int)
        sales_clean = sales_clean.dropna(subset=['amount'])
        sales_clean['sale_date'] = pd.to_datetime(sales_clean['sale_date'], format='mixed', dayfirst=True, errors='coerce')
        sales_clean['amount'] = sales_clean['amount'].astype(float)
        sales_clean['product_id'] = sales_clean['product_id'].astype(str)

        products['product_id'] = products['product_id'].astype(str)
        merged = sales_clean.merge(products, on='product_id', how='left').merge(stores, on='store_id', how='left')
        merged['total_revenue'] = merged['quantity'] * merged['price']

        conn = sqlite3.connect(db_path)
        merged.to_sql('retail_sales', conn, if_exists='replace', index=False)
        conn.close()

        print(f"Pipeline completed successfully. {len(merged)} records loaded into {db_path}")
        return merged

    except FileNotFoundError as e:
        print(f"ERROR: File not found - {e}")
    except Exception as e:
        print(f"ERROR: {e}")


result = run_pipeline(
    f'{BASE}\\sales_data.csv',
    f'{BASE}\\product.csv',
    f'{BASE}\\stores.csv',
    f'{BASE}\\retail_mart.db'
)
print("\n--- Pipeline Execution Complete ---")
