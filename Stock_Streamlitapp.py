import streamlit as st
import pandas as pd
import asyncio
from main_agentic import main  # Importing the async function

st.title("Stock Analysis App")

# User input for stock symbol
stock_symbol = st.text_input("Enter Stock related query e.g.What is the recommendation for IBM based on technical indicators?:", "")

async def fetch_stock_analysis(stock_symbol):
    """Run the async main function properly within Streamlit."""
    return await main(stock_symbol)

if stock_symbol:
    st.subheader("Stock Price Analysis")

    # Run async function using Streamlit’s built-in `asyncio.run`
    with st.spinner("Fetching stock analysis..."):
        result = asyncio.run(fetch_stock_analysis(stock_symbol))

    if result and "error" not in result:
        # Stock Price Data
        st.subheader("Stock Price Data")
        if "stock_data" in result:
            st.dataframe(result["stock_data"].get("price_data", "No stock data available."))

        # Technical Analysis
        st.subheader("Technical Analysis")
        if "stock_data" in result and "technical_analysis" in result["stock_data"]:
            st.dataframe(result["stock_data"]["technical_analysis"])
        else:
            st.write("No technical analysis available.")

        # Financial News
        st.subheader("Latest Financial News")
        if "stock_data" in result and "financial_news" in result["stock_data"]:
            news_data = result["stock_data"]["financial_news"]
            if news_data:
                news_df = pd.DataFrame(news_data, columns=["Title", "URL"])
                st.dataframe(news_df)
            else:
                st.write("No news available.")
        else:
            st.write("No news available.")

        # Market Knowledge Section
        st.subheader("📚 Market Knowledge from Neo4j")

        market_knowledge = result.get("market_knowledge", [])

        # Clean market knowledge (remove any unwanted default message and process correctly)
        if isinstance(market_knowledge, list):
            market_knowledge = [item for item in market_knowledge if
                                item != "No additional market knowledge available."]

        # Check if there is valid knowledge to display
        if market_knowledge:
            formatted_knowledge = [
                f"- {item.split(': ', 1)[-1]}" if ": " in item else f"- {item} "
                for item in market_knowledge
            ]
            knowledge_str = "\n".join(formatted_knowledge)
            st.markdown(knowledge_str)
        else:
            st.write("No additional market knowledge available.")

        # Sentiment Analysis
        st.subheader("Sentiment Analysis")
        if "stock_data" in result:
            sentiment_score = result["stock_data"].get("sentiment", "No sentiment data available.")
            st.write(f"Reddit Sentiment Score: {sentiment_score}")

        # Recommendations
        st.subheader("Recommendations")
        st.write(f"**Internal Recommendation:** {result.get('recommendation_agent_output', 'No recommendation')}")
        st.write(f"**GPT Recommendation:** {result.get('final_recommendation', 'No GPT recommendation')}")

    else:
        st.error(result.get("error", "Error fetching data. Please try again."))
else:
    st.write("Please enter a stock symbol to begin.")
