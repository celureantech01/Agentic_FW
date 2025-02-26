import argparse
import asyncio
import re
from agents.stock_agent import StockAgent
from agents.recommendation_agent import RecommendationAgent
from agents.knowledge_worker_agent import KnowledgeWorkerAgent
from tools.data_fetcher import DataFetcher
import pandas as pd


def extract_symbols_and_keywords(user_input):
    """
    Extract the stock symbol, company name, and keywords from user input.
    The symbol and company are assumed to be uppercase stock symbols and company names.
    Keywords are everything else in the input.
    """
    # Define regex for stock symbol (upper-case word) and company names (words).
    symbol_regex = r'\b[A-Z]{2,5}\b'  # Matches stock symbols like AAPL, TSLA, etc.
    symbols_found = re.findall(symbol_regex, user_input)

    # Assuming company name could be a known name or just a word that isn't a symbol
    # Extract the rest as company name and keywords
    symbols = symbols_found if symbols_found else []
    remaining_input = re.sub(symbol_regex, '', user_input).strip()

    # Use remaining text as keywords
    keywords = remaining_input.split() if remaining_input else []

    # If no symbol is found, infer company name as symbol too (if company is mentioned)
    company = symbols[0] if symbols else "Unknown Company"
    symbol = symbols[0] if symbols else "Unknown Symbol"

    return symbol, company, keywords


async def main():
    # Get user input from a free-form input prompt
    user_input = input(
        "Enter your query (e.g., 'What is the recommendation of AAPL stock based on technical indicators?'): "
    )

    # Automatically extract stock symbol, company name, and query keywords
    symbol, company, keywords = extract_symbols_and_keywords(user_input)

    print(f"\n✅ Extracted Symbol: {symbol}")
    print(f"✅ Extracted Company Name: {company}")
    print(f"✅ Extracted Keywords for Knowledge Query: {keywords}")

    # Step 1: Fetch and process stock data
    print("\n🔄 Step 1: Fetching & analyzing stock data...")
    data_fetcher = DataFetcher()  # Initialize the DataFetcher object
    stock_agent = StockAgent(data_fetcher)  # Pass it to StockAgent
    asset_data = await stock_agent.process_stock(symbol, company)

    if asset_data is None:
        print(f"❌ Error: No data available for {symbol}.")
        return

    # Display price data (processed)
    print(f"\n📊 Stock Price Data for {symbol}:")
    price_df = pd.DataFrame(asset_data.get("price_data", []))
    print(price_df.tail(5).to_string(index=False))

    # Display financial news
    if "financial_news" in asset_data:
        print(f"\n📰 Latest Financial News for {company}:\n")
        for i, news in enumerate(asset_data["financial_news"][:3], 1):
            print(f"  {i}. {news}")

    # Step 2: Generating recommendation
    print("\n📊 Step 2: Generating recommendation...")
    recommendation_agent = RecommendationAgent(stock_agent)

    # Ensure technical analysis data is available
    if hasattr(stock_agent, "technical_data"):
        print(f"📌 Debug: Passing technical analysis to recommendation agent:\n{stock_agent.technical_data}")

    # Generate recommendation with technical analysis
    recommendation = await recommendation_agent.generate_recommendation(
        asset_symbol=symbol,  # ✅ Fixed variable name
        company_name=company,  # ✅ Fixed variable name
        technical_analysis=stock_agent.technical_data  # Ensure this is passed
    )

    # ✅ Print the generated recommendation
    if recommendation:
        print(f"\n📢 Final Recommendation for {symbol}: {recommendation}")
    else:
        print(f"\n⚠️ No valid recommendation generated for {symbol}.")

    # Step 3: Knowledge retrieval from Neo4j
    print("\n📚 Step 3: Retrieving relevant market knowledge from Neo4j...")

    # Construct a query for knowledge worker based on input
    # Do not pass symbol or company, only the keywords
    knowledge_worker = KnowledgeWorkerAgent()

    user_query = ' '.join(keywords + ['market factors', 'recommendation', 'price projection'])

    # Pass the constructed query to the KnowledgeWorkerAgent
    knowledge_worker.retrieve_knowledge(user_query)


if __name__ == "__main__":
    asyncio.run(main())  # Run the main function in an event loop
