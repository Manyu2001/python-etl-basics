import pandas as pd
import sqlite3

# EXTRACT
print("Extracting...")
df = pd.read_csv('data/olist_orders_dataset.csv')
print(f"Rows loaded: {len(df)}")
print(df.head())
# TRANSFORM
print("Transforming...")

# Keep only useful columns
df = df[['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp']]

# Drop nulls
df = df.dropna()

# Convert date column
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

# Add derived columns
df['order_year'] = df['order_purchase_timestamp'].dt.year
df['order_month'] = df['order_purchase_timestamp'].dt.month

# Filter only delivered orders
df = df[df['order_status'] == 'delivered']

print(f"Rows after transform: {len(df)}")
# LOAD
print("Loading...")

conn = sqlite3.connect('output.db')
df.to_sql('orders_clean', conn, if_exists='replace', index=False)
conn.close()

print("Done! Data loaded into output.db → table: orders_clean")
# VALIDATE
conn = sqlite3.connect('output.db')
result = pd.read_sql("SELECT order_year, order_month, COUNT(*) as order_count FROM orders_clean GROUP BY order_year, order_month ORDER BY order_year, order_month", conn)
conn.close()

print(result)