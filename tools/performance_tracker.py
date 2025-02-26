import pandas as pd

def analyze_past_trades():
    try:
        df = pd.read_csv("storage/recommendation_log.csv")
        print(df.tail(5))
    except FileNotFoundError:
        print("No past trade data found.")
