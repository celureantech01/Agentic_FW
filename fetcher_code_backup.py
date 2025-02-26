import yfinance as yf
import requests
from utils.config import COINMARKETCAP_API_KEY, ALPHAVANTAGE_API_KEY, TWELVEDATA_API_KEY


def get_asset_data(ticker, period="6mo"):
    """
    Fetches historical stock data from Yahoo Finance.

    :param ticker: Stock symbol (e.g., 'AAPL', 'GOOGL').
    :param period: Time range (e.g., '1d', '5d', '1mo', '6mo', '1y').
    :return: Pandas DataFrame with stock data or None if an error occurs.
    """
    try:
        data = yf.download(ticker, period=period, auto_adjust=True)
        if data.empty:
            raise ValueError(f"No data found for {ticker}")
        return data
    except Exception as e:
        print(f"Error fetching stock data for {ticker}: {e}")
        return None  # Prevents crashes


def get_crypto_data(symbol="BTC"):
    """
    Fetches live cryptocurrency data from CoinMarketCap API.

    :param symbol: Crypto symbol (e.g., 'BTC', 'ETH').
    :return: Dictionary with price info or None if an error occurs.
    """
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}"
    headers = {"X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises error if API request fails
        data = response.json()
        if "data" in data and symbol in data["data"]:
            return data["data"][symbol]
        else:
            raise ValueError(f"Invalid response for {symbol}")
    except Exception as e:
        print(f"Error fetching crypto data for {symbol}: {e}")
        return None  # Prevents crashes
