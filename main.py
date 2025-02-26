import argparse
import asyncio
import pandas as pd
from agents.stock_agent import StockAgent
from agents.recommendation_agent import RecommendationAgent
from agents.feedback_agent import FeedbackAgent
from agents.knowledge_worker_agent import KnowledgeWorkerAgent
from tools.data_fetcher import get_asset_data  # Correctly import the data_fetcher function

async def main():
    parser = argparse.ArgumentParser(description="Financial Market analysis agents")
    parser.add_argument("--mode", type=str, choices=["recommend", "feedback", "knowledge"], required=True)
    parser.add_argument("--symbol", type=str, required=True, help="Stock symbol (e.g., AAPL, TSLA, BTC)")
    parser.add_argument("--company", type=str, required=True, help="Company name (e.g., Tesla)")
    args = parser.parse_args()

    if args.mode == "recommend":
        print("\n🔄 Step 1: Fetching & analyzing stock data...")

        stock_agent = StockAgent(get_asset_data)  # ✅ FIX: Pass the get_asset_data function to StockAgent
        asset_data = await stock_agent.process_stock(args.symbol, args.company)  # ✅ Use process_stock method

        if asset_data is None:
            print(f"❌ Error: No data available for {args.symbol}.")
            return

        # ✅ Display price data in a formatted table
        if "price_data" in asset_data:
            print(f"\n🔍 Type of 'price_data': {type(asset_data['price_data'])}")
            if isinstance(asset_data["price_data"], dict):
                try:
                    price_df = pd.DataFrame(asset_data["price_data"])
                    print(f"\n📊 Stock Price Data for {args.symbol} (Last 5 Days):\n")
                    print(price_df.tail(5).to_string(index=False))
                except Exception as e:
                    print(f"⚠️ Error converting price_data to DataFrame: {e}")
            else:
                print(f"⚠️ No valid 'price_data' available for {args.symbol}.")

        # ✅ Display financial data
        if "financial_data" in asset_data:
            print(f"\n📊 Financial Data for {args.symbol}:\n", asset_data["financial_data"])

        # ✅ Display financial news
        if "financial_news" in asset_data:
            print(f"\n📰 Latest Financial News for {args.company}:\n")
            for i, news in enumerate(asset_data["financial_news"][:3], 1):
                print(f"  {i}. {news}")
        else:
            print(f"\n⚠️ No financial news available for {args.company}.")

        print("\n📊 Step 2: Generating recommendation...")
        recommendation_agent = RecommendationAgent()
        recommendation = await recommendation_agent.generate_recommendation(args.symbol, args.company)

        # ✅ Print recommendation result
        print(f"Generated Recommendation: {recommendation}")

    elif args.mode == "feedback":
        FeedbackAgent().track_performance()
    elif args.mode == "knowledge":
        KnowledgeWorkerAgent().retrieve_knowledge()
    else:
        print("Invalid mode. Choose from: recommend, feedback, knowledge.")

if __name__ == "__main__":
    asyncio.run(main())  # Run the main function in an event loop
