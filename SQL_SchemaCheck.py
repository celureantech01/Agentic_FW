import sqlite3

DB_FILE = "stock_data.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Fetch all table schemas
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Database Schema:\n")
for table in tables:
    table_name, table_sql = table
    print(f"Schema for {table_name}:")
    print(table_sql)
    print("\n" + "="*50 + "\n")

conn.close()
