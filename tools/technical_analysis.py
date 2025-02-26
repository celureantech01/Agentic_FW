# # import pandas as pd
# # import yfinance as yf
# #
# # def analyze_asset(asset_data):
# #     """
# #     Performs technical analysis on the given asset data.
# #     :param asset_data: DataFrame containing historical stock prices.
# #     :return: DataFrame with added technical indicators.
# #     """
# #     if asset_data is None or asset_data.empty:
# #         raise ValueError("Empty asset data received")
# #
# #     # Calculate Moving Averages
# #     asset_data['SMA_50'] = asset_data['Close'].rolling(window=50, min_periods=1).mean()
# #     asset_data['SMA_200'] = asset_data['Close'].rolling(window=200, min_periods=1).mean()
# #
# #     # Relative Strength Index (RSI)
# #     delta = asset_data['Close'].diff()
# #     gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
# #     loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
# #     rs = gain / (loss + 1e-10)  # Avoid division by zero
# #     asset_data['RSI'] = 100 - (100 / (1 + rs))
# #
# #     # Bollinger Bands
# #     rolling_mean = asset_data['Close'].rolling(window=20, min_periods=1).mean()
# #     rolling_std = asset_data['Close'].rolling(window=20, min_periods=1).std()
# #
# #     asset_data['Middle_Band'] = rolling_mean  # Ensure this is a Series
# #     asset_data['Upper_Band'] = rolling_mean + (rolling_std * 2)
# #     asset_data['Lower_Band'] = rolling_mean - (rolling_std * 2)
# #
# #     return asset_data.tail(5)  # Return last 5 rows for analysis
# #=========================================================================
# import pandas as pd
# import yfinance as yf
#
# def analyze_asset(asset_data):
#     """
#     Performs technical analysis on the given asset data.
#     :param asset_data: DataFrame containing historical stock prices.
#     :return: DataFrame with added technical indicators.
#     """
#     if asset_data is None or asset_data.empty:
#         raise ValueError("Empty asset data received")
#
#     # Calculate Moving Averages
#     asset_data['SMA_50'] = asset_data['Close'].rolling(window=50, min_periods=1).mean()
#     asset_data['SMA_200'] = asset_data['Close'].rolling(window=200, min_periods=1).mean()
#
#     # Relative Strength Index (RSI)
#     delta = asset_data['Close'].diff()
#     gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
#     loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
#     rs = gain / (loss + 1e-10)  # Avoid division by zero
#     asset_data['RSI'] = 100 - (100 / (1 + rs))
#
#     # Bollinger Bands
#     rolling_mean = asset_data['Close'].rolling(window=20, min_periods=1).mean()
#     rolling_std = asset_data['Close'].rolling(window=20, min_periods=1).std()
#
#     asset_data['Middle_Band'] = rolling_mean  # Ensure this is a Series
#     asset_data['Upper_Band'] = rolling_mean + (rolling_std * 2)
#     asset_data['Lower_Band'] = rolling_mean - (rolling_std * 2)
#
#     # Moving Average Convergence Divergence (MACD)
#     asset_data['MACD'] = asset_data['Close'].ewm(span=12, adjust=False).mean() - asset_data['Close'].ewm(span=26, adjust=False).mean()
#     asset_data['MACD_Signal'] = asset_data['MACD'].ewm(span=9, adjust=False).mean()
#
#     # Add MACD Signal (bullish or bearish based on MACD and Signal line)
#     asset_data['macd_signal'] = asset_data['MACD'] > asset_data['MACD_Signal']
#     asset_data['macd_signal'] = asset_data['macd_signal'].map({True: "bullish", False: "bearish"})
#
#     # Return the latest 5 rows of data with technical indicators
#     return asset_data.tail(5)
#
import pandas as pd
import numpy as np

def analyze_asset(asset_data):
    """Performs technical analysis on historical stock prices."""

    # Ensure valid DataFrame
    if asset_data is None or not isinstance(asset_data, pd.DataFrame) or asset_data.empty:
        raise ValueError("❌ Error: Invalid or empty asset data received.")

    # Ensure 'Close' column exists
    if "Close" not in asset_data.columns:
        raise ValueError("❌ Error: Missing required 'Close' column.")

    asset_data = asset_data.copy()

    # Calculate indicators
    asset_data["SMA_50"] = asset_data["Close"].rolling(window=50, min_periods=1).mean()
    asset_data["SMA_200"] = asset_data["Close"].rolling(window=200, min_periods=1).mean()

    # RSI Calculation
    delta = asset_data["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14, min_periods=1).mean()
    loss = -delta.where(delta < 0, 0).rolling(14, min_periods=1).mean()
    rs = gain / loss.replace(0, np.nan)
    asset_data["RSI"] = 100 - (100 / (1 + rs))
    asset_data["RSI"].fillna(50, inplace=True)

    # Bollinger Bands
    rolling_mean = asset_data["Close"].rolling(window=20, min_periods=1).mean()
    rolling_std = asset_data["Close"].rolling(window=20, min_periods=1).std()
    asset_data["Middle_Band"] = rolling_mean
    asset_data["Upper_Band"] = rolling_mean + (rolling_std * 2)
    asset_data["Lower_Band"] = rolling_mean - (rolling_std * 2)

    # MACD Calculation
    asset_data["MACD"] = asset_data["Close"].ewm(span=12, adjust=False).mean() - asset_data["Close"].ewm(span=26, adjust=False).mean()
    asset_data["MACD_Signal"] = asset_data["MACD"].ewm(span=9, adjust=False).mean()
    asset_data["macd_signal"] = np.where(asset_data["MACD"] > asset_data["MACD_Signal"], "bullish", "bearish")

    return asset_data[["RSI", "SMA_50", "SMA_200", "MACD", "MACD_Signal", "macd_signal", "Upper_Band", "Middle_Band", "Lower_Band"]].tail(5)
