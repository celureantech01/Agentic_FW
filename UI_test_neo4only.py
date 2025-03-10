import streamlit as st
import sqlite3
import pandas as pd
import asyncio
import matplotlib.pyplot as plt
import re
from main_agentic import main
from tools.database import create_tables, insert_stock_price, insert_technical_analysis, insert_recommendation
from tools.neo4j_connector import retrieve_knowledge

st.title("Stock Analysis App")

# Ensure the SQLite database tables exist
create_tables()

# Extract stock symbol from user query
def extract_stock_symbol(query):
    match = re.search(r"\b([A-Z]{2,5})\b", query)
    return match.group(1) if match else None

# Main input for stock analysis query
user_query = st.text_input("Enter Stock-related Query (e.g., What is the recommendation for IBM?):", "")

# Knowledge base search bar
knowledge_query = st.text_input("🔍 Search Market Knowledge Base", "")

async def fetch_stock_analysis(stock_symbol):
    """Run the async main function properly within Streamlit."""
    return await main(stock_symbol)

async def fetch_knowledge_base(knowledge_query):
    """Fetch only Neo4j-based market knowledge."""
    return {"market_knowledge": retrieve_knowledge(knowledge_query)}

# Extract stock ticker if found in user query
stock_symbol = extract_stock_symbol(user_query)

if stock_symbol:
    st.subheader(f"Stock Analysis for {stock_symbol}")

    with st.spinner("Fetching stock analysis..."):
        result = asyncio.run(fetch_stock_analysis(stock_symbol))

    if result and "error" not in result:
        # ✅ Display stock price data
        if "stock_data" in result and "price_data" in result["stock_data"]:
            price_data = result["stock_data"]["price_data"]
            st.subheader("Stock Price Data")
            st.dataframe(price_data)

            for i in range(len(price_data["Date"])):
                insert_stock_price(
                    stock_symbol, # Make sure this is just "TSLA"
                    price_data["Date"][i],
                    price_data["Open"][i],
                    price_data["High"][i],
                    price_data["Low"][i],
                    price_data["Close"][i],
                    price_data["Volume"][i]
                )
        else:
            st.warning("No stock price data available.")

        # ✅ Display Technical Analysis
        st.subheader("Technical Analysis")
        # Ensure "technical_analysis" exists and has the required keys
        if "stock_data" in result and "technical_analysis" in result["stock_data"]:
            technical_analysis = result["stock_data"]["technical_analysis"]
            st.dataframe(technical_analysis)

            # Unpacking individual values from the dictionary
            insert_technical_analysis(
                stock_symbol,
                technical_analysis.get("rsi", [None])[0] if isinstance(technical_analysis.get("rsi"),
                                                                       list) else technical_analysis.get("rsi"),
                technical_analysis.get("sma_50", [None])[0] if isinstance(technical_analysis.get("sma_50"),
                                                                          list) else technical_analysis.get("sma_50"),
                technical_analysis.get("sma_200", [None])[0] if isinstance(technical_analysis.get("sma_200"),
                                                                           list) else technical_analysis.get("sma_200"),
                technical_analysis.get("macd", [None])[0] if isinstance(technical_analysis.get("macd"),
                                                                        list) else technical_analysis.get("macd"),
                technical_analysis.get("MACD_signal", [None])[0] if isinstance(technical_analysis.get("MACD_signal"),
                                                                               list) else technical_analysis.get(
                    "MACD_signal"),
                technical_analysis.get("macd_signal", [None])[0] if isinstance(technical_analysis.get("macd_signal"),
                                                                               list) else technical_analysis.get(
                    "macd_signal"),
                technical_analysis.get("upper_band", [None])[0] if isinstance(technical_analysis.get("upper_band"),
                                                                              list) else technical_analysis.get(
                    "upper_band"),
                technical_analysis.get("middle_band", [None])[0] if isinstance(technical_analysis.get("middle_band"),
                                                                               list) else technical_analysis.get(
                    "middle_band"),
                technical_analysis.get("lower_band", [None])[0] if isinstance(technical_analysis.get("lower_band"),
                                                                              list) else technical_analysis.get(
                    "lower_band")
            )

        else:
            st.write("No technical analysis available.")

        # ✅ Display Financial News
        if "financial_news" in result["stock_data"]:
            st.subheader("Latest Financial News")
            news_df = pd.DataFrame(result["stock_data"]["financial_news"], columns=["Title", "URL"])
            st.dataframe(news_df)
        else:
            st.warning("No news available.")

        # ✅ Display Market Knowledge from Neo4j
        if "market_knowledge" in result:
            st.subheader("📚 Market Knowledge from Neo4j")
            knowledge_list = [item for item in result["market_knowledge"] if item != "No additional market knowledge available."]
            if knowledge_list:
                st.markdown("\n".join([f"- {item}" for item in knowledge_list]))
            else:
                st.warning("No additional market knowledge available.")

        # ✅ Display Sentiment Analysis
        st.subheader("Sentiment Analysis")
        sentiment_score = result["stock_data"].get("sentiment", "No sentiment data available.")
        st.write(f"Reddit Sentiment Score: {sentiment_score}")

        # ✅ Display Recommendations
        st.subheader("Recommendations")
        internal_recommendation = result.get('recommendation_agent_output', 'No recommendation')
        gpt_recommendation = result.get('final_recommendation', 'No GPT recommendation')

        st.write(f"**Internal Recommendation:** {internal_recommendation}")
        st.write(f"**GPT Recommendation:** {gpt_recommendation}")

        # ✅ Save Recommendation to DB
        if gpt_recommendation != "No GPT recommendation":
            insert_recommendation(stock_symbol, "Default Recommendation", gpt_recommendation)
    else:
        st.error(result.get("error", "Error fetching stock analysis. Please try again."))

# Knowledge Base Search
if knowledge_query:
    st.subheader("📚 Market Knowledge Base Results")
    with st.spinner("Fetching market knowledge..."):
        knowledge_result = asyncio.run(fetch_knowledge_base(knowledge_query))

    if knowledge_result and "error" not in knowledge_result:
        market_knowledge = knowledge_result.get("market_knowledge", [])
        if market_knowledge:
            st.markdown("\n".join([f"- {item}" for item in market_knowledge]))
        else:
            st.warning("No additional market knowledge available.")
    else:
        st.error(knowledge_result.get("error", "Error fetching knowledge. Please try again."))

if not user_query and not knowledge_query:
    st.write("Please enter a stock query or search for market knowledge.")

# ✅ STOCK DATA VISUALIZATION SECTION
DB_FILE = "stock_data.db"

def fetch_stock_data(stock_symbol, column_name="high"):
    conn = sqlite3.connect(DB_FILE)
    query = f"SELECT date, {column_name} FROM stock_analysis WHERE stock_symbol LIKE ? ORDER BY date"
    df = pd.read_sql_query(query, conn, params=(f"%{stock_symbol}%",))  # Use LIKE for flexibility
    conn.close()
    return df

st.title("Stock Data Visualization")

if stock_symbol:
    st.subheader(f"Stock Data for {stock_symbol}")

    # Dropdown for selecting price column
    column_options = ["open", "high", "low", "close", "volume"]
    selected_column = st.selectbox("Select column to plot:", column_options, index=1)

    # Fetch and visualize stock data
    df = fetch_stock_data(stock_symbol, selected_column)

    if df.empty:
        st.warning(f"No data found for {stock_symbol}. Try another ticker.")
    else:
        st.subheader(f"{stock_symbol} {selected_column.capitalize()} Price Trend")
        fig, ax = plt.subplots()
        ax.plot(df["date"], df[selected_column], marker="o", linestyle="-", color="b", label=selected_column)
        ax.set_xlabel("Date")
        ax.set_ylabel(selected_column.capitalize())
        ax.set_title(f"{stock_symbol} - {selected_column.capitalize()} Over Time")
        ax.legend()
        plt.xticks(rotation=45)
        st.pyplot(fig)
