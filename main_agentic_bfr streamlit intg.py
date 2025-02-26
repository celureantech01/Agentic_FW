import argparse
import asyncio
import re
import openai
import os
import pandas as pd
from agents.stock_agent import StockAgent
from agents.recommendation_agent import RecommendationAgent
from agents.knowledge_worker_agent import KnowledgeWorkerAgent
from tools.data_fetcher import DataFetcher

# Initialize OpenAI API with an environment variable (REMOVE hardcoded key)
openai.api_key = "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"

def extract_symbols_and_keywords(user_input):
    """
    Extract stock symbol, company name, and keywords from user input.
    Symbols are assumed to be uppercase stock symbols (e.g., AAPL, TSLA).
    Keywords contain all other words for additional context.
    """
    symbol_regex = r'\b[A-Z]{2,5}\b'  # Matches stock symbols (e.g., AAPL, TSLA)
    symbols_found = re.findall(symbol_regex, user_input)

    # Remove extracted symbols from input to get remaining keywords
    remaining_input = re.sub(symbol_regex, '', user_input).strip()
    keywords = remaining_input.split() if remaining_input else []

    # Assign symbol and company name (assume same unless specified)
    symbol = symbols_found[0] if symbols_found else None
    company = symbol if symbol else "Unknown Company"

    return symbol, company, keywords

async def get_final_recommendation(stock_data, recommendation, market_knowledge):
    """
    Generate a final recommendation from GPT-4 based on stock data, recommendation, and market knowledge.
    """
    # Truncate or summarize large inputs
    price_data = stock_data.get("price_data", "No price data available.")
    if isinstance(price_data, list) and len(price_data) > 5:
        price_data = price_data[-5:]  # Keep only the last 5 entries

    financial_news = stock_data.get("financial_news", [])
    if isinstance(financial_news, list):
        # Convert tuples to strings if needed
        financial_news = [str(item) if isinstance(item, tuple) else item for item in financial_news]
        financial_news = financial_news[:2]  # Keep only the top 2 news articles
        financial_news = "\n".join(financial_news) if financial_news else "No financial news available."

    technical_analysis = stock_data.get("technical_analysis", "No technical analysis available.")
    if isinstance(technical_analysis, str) and len(technical_analysis) > 500:
        technical_analysis = technical_analysis[:500] + "..."  # Truncate long analysis

    market_knowledge = market_knowledge or "No additional market knowledge available."
    if len(market_knowledge) > 1000:
        market_knowledge = market_knowledge[:1000] + "..."  # Truncate long knowledge input

    # Construct prompt for GPT-4
    prompt = f"""
    Stock Recommendation Summary:

    Symbol: {stock_data.get("symbol", "Unknown")}
    Company Name: {stock_data.get("company", "Unknown")}

    Price Data (Last 5 entries):
    {price_data}

    Financial News (Top 2 headlines):
    {financial_news}

    Technical Analysis (Summarized):
    {technical_analysis}

    Market Knowledge (Summarized):
    {market_knowledge}

    Generated Recommendation:
    {recommendation}

    Given the above data, provide a final recommendation on whether to Buy, Sell, or Hold {stock_data.get("symbol", "this stock")}.
    Include reasoning based on stock performance, technical indicators, and market sentiment.
    """

    # Debugging: Print prompt length before sending to GPT-4
    print(f"📝 Final prompt length: {len(prompt.split())} words")

    # Use OpenAI ChatCompletion API (latest syntax)
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert stock advisor."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=250,  # Reduce output size to prevent exceeding context length
        temperature=0.5
    )

    return response.choices[0].message.content.strip()

async def main():
    # Get user input
    user_input = input("Enter your query (e.g., 'Recommendation for AAPL stock based on technical indicators'): ")

    # Extract stock symbol, company name, and keywords
    symbol, company, keywords = extract_symbols_and_keywords(user_input)

    if not symbol:
        print("❌ No valid stock symbol found. Please enter a valid stock ticker (e.g., AAPL, TSLA).")
        return

    print(f"\n✅ Extracted Symbol: {symbol}")
    print(f"✅ Extracted Company Name: {company}")
    print(f"✅ Extracted Keywords for Market Query: {keywords}")

    # Step 1: Fetch stock data
    print("\n🔄 Step 1: Fetching & analyzing stock data...")
    data_fetcher = DataFetcher()
    stock_agent = StockAgent(data_fetcher)
    asset_data = await stock_agent.process_stock(symbol, company)

    if not asset_data:
        print(f"❌ No data available for {symbol}.")
        return

    # Display fetched stock data
    print(f"\n📊 Stock Price Data for {symbol}:")
    price_df = pd.DataFrame(asset_data.get("price_data", []))
    print(price_df.tail(5).to_string(index=False))

    # Display latest financial news
    if "financial_news" in asset_data and asset_data["financial_news"]:
        print(f"\n📰 Latest Financial News for {company}:\n")
        for i, news in enumerate(asset_data["financial_news"][:3], 1):
            print(f"  {i}. {news}")

    # Step 2: Generate recommendation
    print("\n📊 Step 2: Generating recommendation...")
    recommendation_agent = RecommendationAgent(stock_agent)
    recommendation = await recommendation_agent.generate_recommendation(
        asset_symbol=symbol,
        company_name=company,
        technical_analysis=stock_agent.technical_data
    )

    if recommendation:
        print(f"\n📢 Generated Recommendation for {symbol}: {recommendation}")
    else:
        print(f"\n⚠️ No valid recommendation generated for {symbol}.")

    # Step 3: Retrieve market knowledge from Neo4j
    print("\n📚 Step 3: Retrieving relevant market knowledge from Neo4j...")
    knowledge_worker = KnowledgeWorkerAgent()
    user_query = ' '.join(keywords + ['market factors', 'recommendation', 'price projection'])
    market_knowledge = knowledge_worker.retrieve_knowledge(user_query)

    # Step 4: Generate final recommendation using GPT-4
    print("\n🤖 Step 4: Generating final recommendation using GPT-4...")
    final_recommendation = await get_final_recommendation(asset_data, recommendation, market_knowledge)

    print(f"\n📢 GPT-4 Final Recommendation: {final_recommendation}")

if __name__ == "__main__":
    asyncio.run(main())  # Run the event loop
