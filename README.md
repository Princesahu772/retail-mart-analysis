RetailMart Data Pipeline

How to Run

1. pip install -r requirements.txt
2. python pipeline.py

Or open RetailMart_Sales_Analysis.ipynb in Jupyter and run all cells.

What It Does

- Loads sales, product, and store data from CSV files
- Cleans duplicates, missing values, and incorrect data types
- Merges all datasets and calculates total revenue per transaction
- Loads the final cleaned data into a SQLite database
- Runs SQL queries for top products and revenue per store per day
- Generates a summary report with total transactions, revenue, top city, and top product

Files

- pipeline.py          - Complete data pipeline script
- RetailMart_Sales_Analysis.ipynb - Jupyter notebook with step-by-step execution
- sales_data.csv       - Daily sales transactions
- product.csv          - Product details
- stores.csv           - Store information
- requirements.txt     - Python dependencies
