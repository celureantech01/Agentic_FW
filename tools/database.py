import sqlite3

DB_FILE = "stock_data.db"

def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a given table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def create_tables():
    """Create necessary tables if they do not exist, ensuring no duplicate columns."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create stock_analysis table if it doesn't exist
    cursor.execute("""CREATE TABLE IF NOT EXISTS stock_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_symbol TEXT NOT NULL,
        date TEXT NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER
    )""")

    # Additional columns for technical analysis
    additional_columns = {
        "rsi": "REAL",
        "sma_50": "REAL",
        "sma_200": "REAL",
        "macd": "REAL",
        "macd_signal": "REAL",
        "upper_band": "REAL",
        "middle_band": "REAL",
        "lower_band": "REAL"
    }

    # Check and add missing columns
    for column, data_type in additional_columns.items():
        if not column_exists(cursor, "stock_analysis", column):
            cursor.execute(f"ALTER TABLE stock_analysis ADD COLUMN {column} {data_type}")

    # Create recommendations table with UNIQUE constraint on stock_symbol
    cursor.execute("""CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_symbol TEXT NOT NULL UNIQUE,  -- Ensure stock_symbol is UNIQUE
        recommendation TEXT,
        gpt_recommendation TEXT
    )""")

    conn.commit()
    conn.close()

def insert_stock_price(stock_symbol, date, open_price, high, low, close, volume):
    """Insert stock price data into stock_analysis table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO stock_analysis 
                      (stock_symbol, date, open, high, low, close, volume) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)""",
                   (stock_symbol, date, open_price, high, low, close, volume))

    conn.commit()
    conn.close()

def insert_technical_analysis(stock_symbol, date, rsi, sma_50, sma_200, macd, macd_signal, upper_band, middle_band, lower_band):
    """Update technical analysis data in stock_analysis table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""UPDATE stock_analysis 
                      SET rsi=?, sma_50=?, sma_200=?, macd=?, macd_signal=?, 
                          upper_band=?, middle_band=?, lower_band=? 
                      WHERE stock_symbol=? AND date=?""",
                   (rsi, sma_50, sma_200, macd, macd_signal, upper_band, middle_band, lower_band, stock_symbol, date))

    conn.commit()
    conn.close()

def insert_recommendation(stock_symbol, recommendation, gpt_recommendation):
    """Insert or update recommendations in the recommendations table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO recommendations (stock_symbol, recommendation, gpt_recommendation) 
                          VALUES (?, ?, ?) 
                          ON CONFLICT(stock_symbol) 
                          DO UPDATE SET recommendation=excluded.recommendation, 
                                        gpt_recommendation=excluded.gpt_recommendation""",
                   (stock_symbol, recommendation, gpt_recommendation))

    conn.commit()
    conn.close()

# Run table creation at import
create_tables()
