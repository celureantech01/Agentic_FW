import sqlite3

DB_FILE = "stock_data.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Fetch all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Querying all data from all tables...\n")

for table in tables:
    table_name = table[0]
    print(f"Table: {table_name}")

    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()

    if not rows:
        print("No data found.\n")
    else:
        # Fetch column names
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [col[1] for col in cursor.fetchall()]

        print(f"Columns: {columns}")
        for row in rows:
            print(row)

    print("\n" + "=" * 50 + "\n")

conn.close()
