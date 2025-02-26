import asyncio
import sys
import os
import pandas as pd

# Ensure the script can find 'tools' by adding the project's root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools import data_fetcher  # Import data_fetcher for fetching stock data
from tools import technical_analysis  # Import technical_analysis for technical indicators

class StockAgent:
    def __init__(self, data_fetcher):
        self.data_fetcher = data_fetcher
        self.technical_data = None  # Initialize to hold the technical analysis data

    async def process_stock(self, ticker, company_name):
        """Fetch stock data and process it"""
        print(f"\n🔍 Fetching data for {ticker} ({company_name})...\n")

        # Fetch asset data
        asset_data = await self.data_fetcher.get_asset_data(ticker, company_name)

        # Debugging: Print structure of fetched data
        print("\n📊 Raw Fetched Data Structure:")
        for key in asset_data.keys():
            print(f"  - {key}: {type(asset_data[key])}")

        # Process price data (from Alpha Vantage)
        price_data = None
        if "price_data" in asset_data and isinstance(asset_data["price_data"], dict):
            try:
                price_data = pd.DataFrame(asset_data["price_data"])
                print(f"\n📊 Stock Price Data for {ticker} (Last 5 Days):\n")
                print(price_data.tail(5).to_string(index=False))

                # Perform technical analysis
                analysis_result = technical_analysis.analyze_asset(price_data)
                print(f"\n📊 Technical Analysis Result for {ticker}:\n")
                print(analysis_result.tail(5).to_string(index=False))

                self.technical_data = analysis_result.to_dict(orient="list")  # Save technical analysis data

                asset_data["technical_analysis"] = self.technical_data  # Add technical analysis to the asset data

            except Exception as e:
                print(f"⚠️ Error converting price_data to DataFrame: {e}")
                print(f"Raw price_data: {asset_data['price_data']}")

        else:
            print(f"\n⚠️ No price data available for {ticker}\n")

        # Process other data (news, sentiment, etc.)
        if "financial_news" in asset_data and asset_data["financial_news"]:
            print(f"\n📰 Latest Financial News for {company_name}:\n")
            for i, news in enumerate(asset_data["financial_news"][:3], 1):
                print(f"  {i}. {news}")
        else:
            print(f"\n⚠️ No financial news available for {company_name}\n")

        if "reddit_sentiment" in asset_data:
            print(f"\n📈 Reddit Sentiment Score: {asset_data['reddit_sentiment']}\n")

        # if "telegram_messages" in asset_data and asset_data["telegram_messages"]:
        #     print(f"\n📩 Recent Telegram Messages:\n")
        #     for i, msg in enumerate(asset_data["telegram_messages"][:3], 1):
        #         print(f"  {i}. {msg}")
        # else:
        #     print(f"\n⚠️ No Telegram messages found.\n")

        return asset_data  # Return data for further processing
