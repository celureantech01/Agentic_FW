import re
import asyncio
import openai
import os
import pandas as pd
from agents.stock_agent import StockAgent
from agents.recommendation_agent import RecommendationAgent
from agents.knowledge_worker_agent import KnowledgeWorkerAgent
from tools.data_fetcher import DataFetcher

# Ensure OpenAI API key is set via environment variables
openai.api_key = "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"
if not openai.api_key:
    raise ValueError("❌ OpenAI API key is missing. Set it as an environment variable.")

def extract_symbols_and_keywords(user_input):
    """
    Extract stock symbol, company name, and keywords from user input.
    """
    symbol_regex = r'\b[A-Z]{2,5}\b'
    symbols_found = re.findall(symbol_regex, user_input)
    remaining_input = re.sub(symbol_regex, '', user_input).strip()
    keywords = remaining_input.split() if remaining_input else []

    symbol = symbols_found[0] if symbols_found else None
    company = symbol if symbol else "Unknown Company"

    return symbol, company, keywords

async def get_final_recommendation(stock_data, recommendation, market_knowledge):
    """
    Generate a final recommendation using GPT-4.
    """
    price_data = stock_data.get("price_data", [])
    if isinstance(price_data, list) and len(price_data) > 5:
        price_data = price_data[-5:]

    financial_news = stock_data.get("financial_news", [])
    news_formatted = "\n".join([  # Format the news data
        f"- {item.get('title', 'No title')} ({item.get('date', '')})"
        if isinstance(item, dict) else f"- {item[0]} ({item[1]})"
        for item in financial_news[:3]
    ]) if financial_news else "No financial news available."

    technical_analysis = stock_data.get("technical_analysis", [])
    if isinstance(technical_analysis, list) and len(technical_analysis) > 3:
        technical_analysis = technical_analysis[:3]

    market_knowledge_str = "\n".join(market_knowledge) if market_knowledge else "No additional market knowledge available."
    if len(market_knowledge_str) > 1000:
        market_knowledge_str = market_knowledge_str[:1000] + "..."

    prompt = f"""
    Stock Recommendation Summary:

    Symbol: {stock_data.get("symbol", "Unknown")}
    Company Name: {stock_data.get("company", "Unknown")}

    📊 Price Data (Last 5 entries):
    {price_data}

    📰 Financial News (Top 3 headlines):
    {news_formatted}

    📈 Technical Analysis (Key Indicators):
    {technical_analysis}

    🧠 Market Knowledge:
    {market_knowledge_str}

    🔍 Generated Recommendation:
    {recommendation}

    Just answer user query based on data provided to you
    """
    # Given the above data, provide a final recommendation on whether to Buy, Sell, or Hold {stock_data.get("symbol", "this stock")}.
    # Include reasoning based on stock performance, technical indicators, and market sentiment.

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[  # Creating the chat for GPT-4 model
            {"role": "system", "content": "You are an expert stock advisor."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=250,
        temperature=0.5
    )

    return response.choices[0].message.content.strip()

async def main(user_input):
    """
    Main function to process user input and return structured stock analysis.
    """
    symbol, company, keywords = extract_symbols_and_keywords(user_input)

    if not symbol:
        return {"error": "❌ No valid stock symbol found. Please enter a valid stock ticker (e.g., AAPL, TSLA)."}

    print(f"\n✅ Extracted Symbol: {symbol}")
    print(f"✅ Extracted Company Name: {company}")
    print(f"✅ Extracted Keywords for Market Query: {keywords}")

    print("\n🔄 Step 1: Fetching & analyzing stock data...")
    data_fetcher = DataFetcher()
    stock_agent = StockAgent(data_fetcher)
    asset_data = await stock_agent.process_stock(symbol, company)

    if not asset_data:
        return {"error": f"❌ No data available for {symbol}."}

    print(f"\n📊 Stock Price Data for {symbol}:")
    price_df = pd.DataFrame(asset_data.get("price_data", []))
    print(price_df.tail(5).to_string(index=False))

    print("\n📈 Technical Analysis Data:")
    if "technical_analysis" in asset_data:
        ta_df = pd.DataFrame(asset_data["technical_analysis"])
        print(ta_df.tail(10).to_string(index=False))
    else:
        print("⚠️ No technical analysis data available.")

    print("\n📰 News Data:")
    if "financial_news" in asset_data:
        for news in asset_data["financial_news"][:3]:
            if isinstance(news, dict):
                print(f"- {news.get('title', 'No Title')} ({news.get('date', 'No Date')})")
            elif isinstance(news, tuple):
                print(f"- {news[0]} ({news[1]})")  # Assuming the tuple format is (title, date)
    else:
        print("⚠️ No financial news available.")

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
        recommendation = "⚠️ No valid recommendation generated."
        print(f"\n⚠️ No valid recommendation generated for {symbol}.")

    print("\n📚 Step 3: Retrieving relevant market knowledge from Neo4j...")
    knowledge_worker = KnowledgeWorkerAgent()
    user_query = ' '.join(keywords + ['market factors', 'recommendation', 'price projection'])
    market_knowledge = knowledge_worker.retrieve_knowledge(user_query)
    if not market_knowledge:  # Ensure it's a list
        market_knowledge = []

    # Debug output for checking the backend processed knowledge
    print("\n📚 Knowledge Retrieved (Raw Data):")
    for record in market_knowledge:
        print(record)

    print("\n📚 Debug: Market Knowledge Before Processing (Raw List):", repr(market_knowledge))

    print("\n🛠️ Debug: Structure of Market Knowledge (Before Cleaning):")
    for i, record in enumerate(market_knowledge):
        print(f"{i}: {repr(record)} (Type: {type(record)})")

    # Clean market knowledge data just before passing to the UI
    if isinstance(market_knowledge, list) and market_knowledge:
        market_knowledge = [record.strip() for record in market_knowledge if record.strip()]

        # market_knowledge = [
        #     str(record[1]).strip()  # Extract second value since first is None
        #     for record in market_knowledge
        #     if len(record) > 1 and record[1] and str(
        #         record[1]).strip().lower() != "no additional market knowledge available."
        # ]

    else:
        market_knowledge = ["No additional market knowledge available."]

    # Debug output for checking the processed knowledge
    print("\n📚 Knowledge Processed for UI:", market_knowledge)

    print("\n🤖 Step 4: Generating final recommendation using GPT-4...")
    final_recommendation = await get_final_recommendation(asset_data, recommendation, market_knowledge)

    print(f"\n📢 GPT-4 Final Recommendation: {final_recommendation}")

    return {
        "stock_data": asset_data,
        "market_knowledge": market_knowledge,
        "recommendation_agent_output": recommendation,
        "final_recommendation": final_recommendation
    }

if __name__ == "__main__":
    user_query = input("Enter your query (e.g., 'Recommendation for AAPL stock based on technical indicators'): ")
    asyncio.run(main(user_query))
