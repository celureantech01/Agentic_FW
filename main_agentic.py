import re
import asyncio
import openai
import os
import pandas as pd
from agents.stock_agent import StockAgent
from agents.recommendation_agent import RecommendationAgent
from tools.data_fetcher import DataFetcher
from langchain.prompts import PromptTemplate
from neo4j import GraphDatabase
from sklearn.metrics.pairwise import cosine_similarity
from tools.neo4j_connector import Neo4jConnector  # Import your Neo4jConnector

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


async def get_final_response(stock_data, user_query, market_knowledge):
    """
    Generate a response using GPT-4, dynamically adjusting to the type of user query.
    """
    # Prepare stock data dynamically
    technical_analysis = stock_data.get("technical_analysis", {})
    recent_prices = stock_data.get("price_data", [])
    if isinstance(recent_prices, list) and len(recent_prices) > 5:
        price_data = recent_prices[-5:]

    financial_news = stock_data.get("financial_news", [])
    news_formatted = "\n".join([  # Format the news data
        f"- {item.get('title', 'No title')} ({item.get('date', '')})"
        if isinstance(item, dict) else f"- {item[0]} ({item[1]})"
        for item in financial_news[:3]
    ]) if financial_news else "No financial news available."

    market_knowledge_str = "\n".join(market_knowledge) if market_knowledge else "No additional market knowledge available."

    # 🔥 Use LangChain's Prompt Template
    template = """You are a stock market expert.
    Answer the user query strictly based on the provided data.
    If the question is about specific technical indicators, return only those.
    If the question is about a recommendation, return a well-reasoned Buy/Sell/Hold decision.

    User Query: {question}

    --- Stock Data ---
    Stock Symbol: {symbol}
    Company Name: {company}

    📊 Price Data (Last 5 Days):
    {recent_prices}

    📈 Technical Indicators:
    {technical_analysis}

    📰 News Headlines:
    {news_formatted}

    🧠 Market Knowledge:
    {market_knowledge}

    Based on the user query, generate a direct and precise answer.
    """

    # 🔥 Setup Memory
    prompt = PromptTemplate(
        input_variables=["question", "symbol", "company", "recent_prices", "technical_analysis", "news_formatted",
                         "market_knowledge"], template=template)

    # 🔥 Generate GPT Response with Dynamic Context
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "system", "content": "You are an expert financial analyst."
        }, {
            "role": "user", "content": prompt.format(
                question=user_query,
                symbol=stock_data.get("symbol", "Unknown"),
                company=stock_data.get("company", "Unknown"),
                recent_prices=recent_prices,
                technical_analysis=technical_analysis,
                news_formatted=news_formatted,
                market_knowledge=market_knowledge_str
            )
        }],
        max_tokens=300,
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

    # 🔥 Step 3: Directly Querying Neo4j for Market Knowledge
    print("\n📚 Step 3: Retrieving relevant market knowledge from Neo4j...")

    # Initialize Neo4jConnector for direct querying
    neo4j_connector = Neo4jConnector()

    # Assuming the query to be based on user's input
    market_knowledge = neo4j_connector.retrieve_knowledge(user_input)

    print("\n📚 Knowledge Retrieved (Raw Data):")
    print(market_knowledge)

    # Clean market knowledge data just before passing to the UI
    # Assuming market_knowledge is a list of dictionaries with 'name' and 'description'
    market_knowledge_str = "\n".join([f"Name: {item['name']}, Description: {item['description']}" for item in
                                      market_knowledge]) if market_knowledge else "No additional market knowledge available."

    print("\n📚 Knowledge Processed for UI:", market_knowledge_str)

    print("\n🤖 Step 4: Generating final recommendation using GPT-4...")
    final_recommendation_response = await get_final_response(asset_data, recommendation, market_knowledge_str)

    print(f"\n📢 GPT-4 Final Recommendation: {final_recommendation_response}")

    return {
        "stock_data": asset_data,
        "market_knowledge": market_knowledge_str,
        "recommendation_agent_output": recommendation,
        "final_recommendation": final_recommendation_response
    }


if __name__ == "__main__":
    user_query = input("Enter your query (e.g., 'Recommendation for AAPL stock based on technical indicators'): ")
    asyncio.run(main(user_query))
