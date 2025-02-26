import streamlit as st
import asyncio
import pandas as pd
from main_agentic import main as generate_full_context

# Set page config
st.set_page_config(page_title="Stock Analysis", layout="wide")

# Title
st.title("📈 Stock Analysis & Recommendation")

# User input box
user_input = st.text_input(
    "Enter stock-related query (e.g., 'What is the recommendation for IBM based on technical indicators?'):"
)

# Submit button
if st.button("Analyze Stock") and user_input:
    with st.spinner("Fetching data... Please wait."):
        # Run the main processing pipeline
        stock_analysis = asyncio.run(generate_full_context(user_input))

        # Extract relevant data
        stock_data = stock_analysis.get("stock_data", {})
        technical_analysis = stock_analysis.get("technical_analysis", {})
        news = stock_analysis.get("news", [])
        sentiment = stock_analysis.get("sentiment", {})
        internal_recommendation = stock_analysis.get("recommendation_agent_output", "No output available.")
        final_recommendation = stock_analysis.get("final_recommendation", "")

        # --- Display Results ---

        # Stock Data Table
        st.subheader("📊 Stock Price Data")
        if isinstance(stock_data, dict) and stock_data:
            # Debugging: Print structure of stock_data
            st.write("Debugging stock_data structure:",
                     {k: len(v) if isinstance(v, list) else "Not a list" for k, v in stock_data.items()})

            valid_lists = [v for v in stock_data.values() if isinstance(v, list)]

            if valid_lists:
                min_length = min(len(v) for v in valid_lists)
                st.write(f"Minimum list length: {min_length}")

                # Ensure all lists are truncated to the same length
                stock_data = {k: v[:min_length] if isinstance(v, list) else v for k, v in stock_data.items()}
                df_stock = pd.DataFrame(stock_data).apply(pd.to_numeric, errors='coerce')
                st.dataframe(df_stock.style.format("{:.2f}"))
            else:
                st.write("Stock data is available but empty.")
        else:
            st.write("No stock data available.")

        # Technical Indicators Table
        st.subheader("📉 Technical Indicators")
        if isinstance(technical_analysis, dict) and technical_analysis:
            valid_tech_lists = [v for v in technical_analysis.values() if isinstance(v, list)]

            if valid_tech_lists:
                min_length = min(len(v) for v in valid_tech_lists)
                technical_analysis = {k: v[:min_length] if isinstance(v, list) else v for k, v in
                                      technical_analysis.items()}
                df_tech = pd.DataFrame(technical_analysis).apply(pd.to_numeric, errors='coerce')
                st.dataframe(df_tech.style.format("{:.2f}"))
            else:
                st.write("Technical analysis data is available but empty.")
        else:
            st.write("No technical analysis available.")

        # News Section
        st.subheader("📰 Financial News")
        if isinstance(news, list) and news:
            df_news = pd.DataFrame(news)
            st.dataframe(df_news)
        else:
            st.write("No news available.")

        # Sentiment Analysis
        st.subheader("💬 Reddit & Market Sentiment")
        if isinstance(sentiment, dict) and sentiment:
            sentiment_str = "\n".join([f"- **{k}:** {v}" for k, v in sentiment.items()])
            st.markdown(sentiment_str)
        else:
            st.write("No sentiment analysis available.")

        # Internal Recommendation
        st.subheader("🤖 Internal Recommendation")
        st.markdown(f"**<span style='color:purple;'>{internal_recommendation}</span>**", unsafe_allow_html=True)

        # Highlighted LLM Recommendation
        st.subheader("🏆 Final GPT-4 Recommendation")
        st.markdown(f"**<span style='color:darkblue;'>{final_recommendation}</span>**", unsafe_allow_html=True)
