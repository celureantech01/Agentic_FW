import asyncio
import pandas as pd
from tools import data_fetcher  # Import the data_fetcher module
from agents.stock_agent import StockAgent
from agents.recommendation_agent import RecommendationAgent
from tools.technical_analysis import analyze_asset


async def test_data_fetcher():
    """Tests data fetching, stock agent processing, and recommendation generation."""
    asset_symbol = "IBM"
    company_name = "IBM"

    print(f"\n🔍 Fetching data for {asset_symbol} ({company_name})...")
    asset_data = await data_fetcher.get_asset_data(asset_symbol, company_name)

    # Print the raw data fetched from APIs
    print(f"\n📊 Raw Fetched Data for {asset_symbol}:\n{asset_data}")

    if asset_data is None or not isinstance(asset_data, dict):
        print(f"❌ Error: No valid data available for {asset_symbol}.")
        return

    # Process Data Using StockAgent
    stock_agent = StockAgent(data_fetcher)  # Pass the data_fetcher module, not the function
    processed_data = await stock_agent.process_stock(asset_symbol, company_name)

    # Print the processed data after StockAgent
    print(f"\n🔍 Processed Data After StockAgent:\n{processed_data}")

    if processed_data is None:
        print(f"❌ Error: Stock agent did not return any processed data.")
        return

    # Handle Price Data
    price_data = processed_data.get("price_data", {})

    if price_data:
        try:
            price_df = pd.DataFrame(price_data)
            print(f"\n📊 Stock Price Data for {asset_symbol} (Last 5 Days):\n", price_df.tail(5).to_string(index=False))

            # Perform Technical Analysis
            print(f"\n🔍 Running Technical Analysis for {asset_symbol}...")
            analysis = analyze_asset(price_df)

            if isinstance(analysis, pd.DataFrame):
                print(f"\n📊 Technical Analysis for {asset_symbol} (Last Row):\n", analysis.tail(1))

                # Store the technical analysis in processed_data for recommendation agent
                processed_data["technical_analysis"] = analysis.to_dict(orient="records")
            else:
                print(f"❌ Error: Technical analysis failed for {asset_symbol}.")
        except Exception as e:
            print(f"⚠️ Error processing price data: {e}")
    else:
        print(f"\n⚠️ No valid 'price_data' available for {asset_symbol}.")

    # Display Additional Data
    print(f"\n📊 Financial Data for {asset_symbol}:\n",
          processed_data.get("financial_data", "⚠️ No financial data available."))

    if "financial_news" in processed_data:
        print(f"\n📰 Latest Financial News for {company_name}:\n")
        for i, news in enumerate(processed_data["financial_news"][:3], 1):
            print(f"  {i}. {news}")
    else:
        print(f"\n⚠️ No financial news available for {company_name}.")

    if "reddit_sentiment" in processed_data:
        print(f"\n📈 Reddit Sentiment Score: {processed_data['reddit_sentiment']}")

    if "telegram_messages" in processed_data:
        print(f"\n📩 Recent Telegram Messages:\n", processed_data["telegram_messages"])
    else:
        print(f"\n⚠️ No Telegram messages found.")

    # Debug: Check if technical analysis is present before recommendation
    print(
        f"\n🛠 Debug: Checking Technical Analysis Data Before Recommendation:\n{processed_data.get('technical_analysis', '❌ No Technical Analysis Found')}")

    # Generate Recommendation
    print(f"\n📌 Generating Recommendation for {asset_symbol}...")
    recommendation_agent = RecommendationAgent(stock_agent)

    # Pass technical analysis data explicitly
    await recommendation_agent.generate_recommendation(asset_symbol, company_name, processed_data.get("technical_analysis"))
    #
    # Only pass asset_symbol and company_name (remove extra argument)
    # await recommendation_agent.generate_recommendation(asset_symbol, company_name)

if __name__ == "__main__":
    asyncio.run(test_data_fetcher())
